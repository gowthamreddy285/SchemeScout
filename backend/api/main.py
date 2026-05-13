"""
api/main.py
Policy Intelligence - FastAPI Backend

Endpoints:
  POST /query          — Main query endpoint (retrieval + generation)
  GET  /health         — Health check
  GET  /schemes/count  — Count of indexed schemes
  GET  /filters        — Available filter options

Rate Limiting (via slowapi):
  /query       — RATE_LIMIT_QUERY  (default: 20/minute per IP)
  all others   — RATE_LIMIT_DEFAULT (default: 60/minute per IP)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from retrieval.engine import CitizenRetrievalEngine
from generation.generator import PolicyGenerator
from config import RATE_LIMIT_QUERY, RATE_LIMIT_DEFAULT, EMBEDDING_MODEL_NAME

# ── Rate Limiter ──────────────────────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT_DEFAULT])

# ── App ──────────────────────────────────────────────────────────────────────

from contextlib import asynccontextmanager

# Singletons
retrieval_engine = None
generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global retrieval_engine, generator
    print("Loading retrieval engine...")
    retrieval_engine = CitizenRetrievalEngine()
    print("Loading generator...")
    generator = PolicyGenerator()
    print("API ready.")
    yield

app = FastAPI(
    title="Policy Intelligence API",
    description="RAG-powered Indian Government Scheme Query System",
    version="1.0.0",
    lifespan=lifespan
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response Models ─────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500, example="What are PMEGP benefits?")
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        example={"ministry": "MSME", "state": "Karnataka", "section": "eligibility"}
    )

class Citation(BaseModel):
    scheme_name: str
    ministry: str
    state: str
    section: str
    source_url: str
    rerank_score: float

class QueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    chunks_used: int
    provider: Optional[str]

class HealthResponse(BaseModel):
    status: str
    db_documents: int
    llm_provider: Optional[str]
    embedding_model: str

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse)
@limiter.limit(RATE_LIMIT_QUERY)
async def query(request: Request, body: QueryRequest):
    """
    Main query endpoint. Retrieves relevant policy chunks and generates a cited answer.

    Rate limited to RATE_LIMIT_QUERY per IP (default: 20/minute).

    Supports metadata filters:
    - ministry: "MSME", "Agriculture", "Ministry of Education", etc.
    - state: "Central", "Karnataka", "Tamil Nadu", etc.
    - category: "MSME", "Agriculture/Credit", "Startup/Seed", etc.
    - section: "eligibility", "benefits", "application", "overview"
    """
    if retrieval_engine is None:
        raise HTTPException(status_code=503, detail="Retrieval engine not initialized.")

    try:
        chunks = retrieval_engine.retrieve(body.query, filters=body.filters)

        if not chunks:
            return QueryResponse(
                query=body.query,
                answer="No relevant policy information found. Try rephrasing or adjusting your filters.",
                citations=[],
                chunks_used=0,
                provider=None
            )

        result = generator.generate(body.query, chunks)

        return QueryResponse(
            query=body.query,
            answer=result["answer"],
            citations=[Citation(**c) for c in result["citations"]],
            chunks_used=result["chunks_used"],
            provider=result["provider"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def health(request: Request):
    """Health check — confirms DB, LLM, and embedding model are ready."""
    if retrieval_engine is None:
        raise HTTPException(status_code=503, detail="Engine not ready.")

    all_docs = retrieval_engine.vector_db.get()
    doc_count = len(all_docs.get("ids", []))

    return HealthResponse(
        status="ok",
        db_documents=doc_count,
        llm_provider=generator.provider if generator else None,
        embedding_model=EMBEDDING_MODEL_NAME
    )


@app.get("/schemes/count")
@limiter.limit(RATE_LIMIT_DEFAULT)
async def scheme_count(request: Request):
    """Returns number of indexed document chunks."""
    if retrieval_engine is None:
        raise HTTPException(status_code=503, detail="Engine not ready.")
    all_docs = retrieval_engine.vector_db.get()
    return {"indexed_chunks": len(all_docs.get("ids", []))}


@app.get("/filters")
@limiter.limit(RATE_LIMIT_DEFAULT)
async def available_filters(request: Request):
    """Returns the available filter options for structured queries."""
    return {
        "ministry": [
            "MSME", "Agriculture", "Ministry of Education",
            "Ministry of Tribal Affairs", "MeitY", "SFAC", "Startup Karnataka"
        ],
        "state": [
            "Central", "Karnataka", "Tamil Nadu", "Maharashtra", "Delhi"
        ],
        "category": [
            "MSME", "MSME/Credit", "MSME/Export", "MSME/Khadi",
            "Agriculture/Credit", "Agriculture/Irrigation", "Agriculture/Market",
            "Startup/Seed", "Startup/Scaleup", "Startup/R&D",
            "Student/Scholarship", "Student/Fellowship"
        ],
        "section": ["eligibility", "benefits", "application", "overview"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)
