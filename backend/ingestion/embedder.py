import sys
import os
import glob
from typing import List
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *

# Models are loaded from config.py

class CitizenIngestor:
    def __init__(self):
        print(f"Initializing Embeddings model: {EMBEDDING_MODEL_NAME}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_db = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=self.embeddings,
            collection_name="policy_intelligence"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def ingest_all(self):
        # Process Schemes directory (JSON)
        schemes_path = os.path.join(RAW_DATA_DIR, "schemes")
        if os.path.exists(schemes_path):
            print("Processing Government Schemes (JSON)...")
            json_files = glob.glob(os.path.join(schemes_path, "*.json"))
            for file_path in json_files:
                self.process_json_file(file_path)

        # Process PDF directory
        pdfs_path = os.path.join(RAW_DATA_DIR, "pdfs")
        if os.path.exists(pdfs_path):
            print("\nProcessing Policy Documents (PDF)...")
            pdf_files = glob.glob(os.path.join(pdfs_path, "*.pdf"))
            for file_path in pdf_files:
                self.process_pdf_file(file_path)

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
    def process_pdf_file(self, file_path: str):
        print(f"  Loading PDF file: {file_path}")
        try:
            loader = PyMuPDFLoader(file_path)
            docs = loader.load()
            
            # Enrich metadata
            filename = os.path.basename(file_path)
            scheme_name = filename.replace(".pdf", "").replace("_", " ").upper()
            
            for doc in docs:
                doc.metadata.update({
                    "scheme_name": scheme_name,
                    "document_type": "official_guideline",
                    "source_url": "N/A" # Ideally source URL would be tracked
                })

            chunks = self.text_splitter.split_documents(docs)
            self.vector_db.add_documents(chunks)
            print(f"    Added {len(chunks)} chunks to vector store.")
        except Exception as e:
            print(f"    ERROR adding PDF {file_path}: {e}")

if __name__ == "__main__":
    ingestor = CitizenIngestor()
    ingestor.ingest_all()
