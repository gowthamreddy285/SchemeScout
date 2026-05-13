import os
import glob
from typing import List
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from config import *

# Updated Embedding Model for Policy Intelligence
POLICY_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

class CitizenIngestor:
    def __init__(self):
        print(f"Initializing Embeddings model: {POLICY_EMBEDDING_MODEL}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=POLICY_EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_db = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=self.embeddings,
            collection_name="policy_intelligence"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def ingest_all(self):
        # Process Schemes directory
        schemes_path = os.path.join(RAW_DATA_DIR, "schemes")
        if os.path.exists(schemes_path):
            print("Processing Government Schemes...")
            json_files = glob.glob(os.path.join(schemes_path, "*.json"))
            for file_path in json_files:
                self.process_json_file(file_path)

        print("\nPolicy Intelligence Ingestion complete.")

    def process_json_file(self, file_path: str):
        print(f"  Loading JSON file: {file_path}")
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        from langchain_core.documents import Document
        docs = []
        for item in data:
            # Metadata expanded for Policy Intelligence
            metadata = item.get("metadata", {})
            doc = Document(
                page_content=item["text"],
                metadata=metadata
            )
            docs.append(doc)
        
        chunks = self.text_splitter.split_documents(docs)
        try:
            self.vector_db.add_documents(chunks)
            print(f"    Added {len(chunks)} chunks to vector store.")
        except Exception as e:
            print(f"    ERROR adding documents from {file_path}: {e}")
            raise e

if __name__ == "__main__":
    ingestor = CitizenIngestor()
    ingestor.ingest_all()
