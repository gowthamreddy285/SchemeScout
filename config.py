import os
from dotenv import load_dotenv

load_dotenv()

# Project Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# Model Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "BAAI/bge-reranker-base"

# LLM Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# RAG Hyperparameters
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K_RETRIEVAL = 10
TOP_K_RERANK = 3

# Policy Intelligence Domains
DOMAINS = ["msme", "startup", "student", "agriculture"]
