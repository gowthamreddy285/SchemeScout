import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Base directory (backend folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Paths
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Retrieval Settings
TOP_K_RETRIEVAL = 25
TOP_K_RERANK = 15

# Generation Settings
GROQ_MODEL = "llama3-70b-8192"
