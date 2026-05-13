"""
backend/config.py  ← SINGLE SOURCE OF TRUTH for all runtime settings.

All other modules import from here. Never hardcode these values elsewhere.
"""
import os
from dotenv import load_dotenv

# Load environment variables from the nearest .env file, overriding terminal cache
load_dotenv(override=True)

# ── Directory Paths ────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# ── API Keys ───────────────────────────────────────────────────────────────────
GROQ_API_KEY      = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ── Model Names ────────────────────────────────────────────────────────────────
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
RERANKER_MODEL_NAME  = os.getenv("RERANKER_MODEL_NAME",  "BAAI/bge-reranker-base")
GROQ_MODEL           = os.getenv("GROQ_MODEL",           "llama-3.3-70b-versatile")

# ── Chunking ───────────────────────────────────────────────────────────────────
# All ingestors MUST read from here — never hardcode chunk sizes inline.
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE",    "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# ── Retrieval ──────────────────────────────────────────────────────────────────
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "10"))
TOP_K_RERANK    = int(os.getenv("TOP_K_RERANK",    "3"))

# ── Rate Limiting ──────────────────────────────────────────────────────────────
# Requests per minute per IP for the /query endpoint
RATE_LIMIT_QUERY  = os.getenv("RATE_LIMIT_QUERY",  "20/minute")
# Requests per minute per IP for all other endpoints
RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")

# ── Domain Tags ───────────────────────────────────────────────────────────────
DOMAINS = ["msme", "startup", "student", "agriculture"]
