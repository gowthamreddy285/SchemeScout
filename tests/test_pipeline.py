import pytest
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from retrieval.engine import CitizenRetrievalEngine
from generation.generator import PolicyGenerator
from ingestion.embedder import CitizenIngestor
import config

@pytest.fixture
def engine():
    return CitizenRetrievalEngine()

@pytest.fixture
def generator():
    return PolicyGenerator()

# 1. Test Embedder Dimension
def test_embedding_dimension():
    from langchain_community.embeddings import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
    vector = embeddings.embed_query("test query")
    assert len(vector) == 384  # bge-small dimension

# 2. Test Retriever TOP_K
def test_retriever_top_k(engine):
    results = engine.vector_db.similarity_search("PMEGP", k=config.TOP_K_RETRIEVAL)
    assert len(results) <= config.TOP_K_RETRIEVAL

# 3. Test Reranker TOP_K
def test_reranker_top_k(engine):
    results = engine.retrieve("PMEGP")
    assert len(results) <= config.TOP_K_RERANK

# 4. Test API Health (Mocking if needed, but here testing the engine directly)
def test_engine_initialization(engine):
    assert engine.vector_db is not None
    assert engine.reranker is not None

# 5. Test Hybrid Retrieval (Scheme Name Match)
def test_pmegp_retrieval(engine):
    results = engine.retrieve("What is PMEGP?")
    scheme_names = [doc.metadata.get("scheme_name") for doc in results]
    assert any("PMEGP" in name for name in scheme_names if name)

# 6. Test JSON Loading
def test_json_parsing():
    import json
    test_json = os.path.join("backend", "data", "raw", "schemes", "pmegp_msme.json")
    with open(test_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert "text" in data[0]
    assert "metadata" in data[0]

# 7. Test State Boosting
def test_state_boosting(engine):
    # Query with Karnataka should boost Karnataka results
    results = engine.retrieve("Karnataka startups")
    if results:
        # Check if top results have Karnataka state
        states = [doc.metadata.get("state") for doc in results]
        assert "Karnataka" in states

# 8. Test Citation URL Guard (Logic check)
def test_url_validation_logic():
    def is_valid(url):
        return bool(url and url != 'N/A' and url.startswith('http'))
    
    assert is_valid("https://google.com") is True
    assert is_valid("N/A") is False
    assert is_valid(None) is False
    assert is_valid("localhost:5173/N/A") is False

# 9. Test Generator Fallback (Empty chunks)
def test_generator_no_chunks(generator):
    result = generator.generate("test query", [])
    assert "No relevant policy information" in result["answer"]
    assert result["citations"] == []

# 10. Test Config Constants
def test_config_values():
    assert config.TOP_K_RETRIEVAL == 10
    assert config.TOP_K_RERANK == 3
    assert "llama-3.3" in config.GROQ_MODEL
