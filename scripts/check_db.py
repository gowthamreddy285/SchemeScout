import os
import sys

sys.path.insert(0, os.path.abspath("backend"))
from config import *
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

print("Connecting to Chroma DB...")
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)
vector_db = Chroma(
    persist_directory=CHROMA_DB_DIR,
    embedding_function=embeddings,
    collection_name="policy_intelligence"
)

count = vector_db._collection.count()
print(f"Total chunks in Vector DB right now: {count}")

if count > 0:
    print("\n--- Testing Vector Retrieval from the Database ---")
    results = vector_db.similarity_search("student scholarships", k=1)
    if results:
        print(f"Match found! Scheme Name: {results[0].metadata.get('scheme_name', 'Unknown')}")
        print(f"Content snippet: {results[0].page_content[:150]}...")
