import os
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder
from config import *

# Updated Models for Policy Intelligence
POLICY_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
POLICY_RERANKER_MODEL = "BAAI/bge-reranker-base"

class CitizenRetrievalEngine:
    def __init__(self):
        print(f"Loading Vector DB from {CHROMA_DB_DIR}")
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
        
        # Initialize Reranker
        print(f"Loading Reranker: {POLICY_RERANKER_MODEL}")
        self.reranker = CrossEncoder(POLICY_RERANKER_MODEL)
        
        # BM25 will be initialized on demand or during startup if docs are available
        self.bm25_retriever = None
        self._initialize_bm25()

    def _initialize_bm25(self):
        # Load all documents from vector store to initialize BM25
        # This is a simple approach for small-medium datasets
        try:
            all_docs = self.vector_db.get(include=['documents', 'metadatas'])
            if all_docs['documents']:
                from langchain_core.documents import Document
                docs = [
                    Document(page_content=doc, metadata=meta) 
                    for doc, meta in zip(all_docs['documents'], all_docs['metadatas'])
                ]
                self.bm25_retriever = BM25Retriever.from_documents(docs)
                self.bm25_retriever.k = TOP_K_RETRIEVAL
                print(f"BM25 initialized with {len(docs)} documents.")
            else:
                print("No documents found in Vector DB to initialize BM25.")
        except Exception as e:
            print(f"Error initializing BM25: {e}")

    def retrieve(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks using Hybrid Search (Vector + BM25) and Reranking.
        filters: Dictionary of metadata filters (e.g. {"ministry": "MSME", "state": "Karnataka"})
        """
        # 1. Vector Search
        search_kwargs = {"k": TOP_K_RETRIEVAL}
        if filters:
            search_kwargs["filter"] = filters
        
        vector_results = self.vector_db.similarity_search(query, **search_kwargs)
        
        # 2. BM25 Search (Filters applied manually for now as LangChain BM25 is limited)
        bm25_results = []
        if self.bm25_retriever:
            bm25_results = self.bm25_retriever.invoke(query)
            if filters:
                for key, value in filters.items():
                    bm25_results = [doc for doc in bm25_results if doc.metadata.get(key) == value]
        
        # 3. Combine & Deduplicate
        all_results = vector_results + bm25_results
        unique_results = []
        seen_content = set()
        for doc in all_results:
            if doc.page_content not in seen_content:
                unique_results.append(doc)
                seen_content.add(doc.page_content)
        
        # 4. Reranking & State Boosting
        if unique_results:
            pairs = [[query, doc.page_content] for doc in unique_results]
            scores = self.reranker.predict(pairs)
            
            # State Boost Logic: If state name is in query, boost those results
            states = ["Karnataka", "Maharashtra", "Tamil Nadu", "Gujarat", "Delhi"]
            detected_state = next((s for s in states if s.lower() in query.lower()), None)

            for doc, score in zip(unique_results, scores):
                final_score = float(score)
                if detected_state and doc.metadata.get("state") == detected_state:
                    final_score += 2.0  # Significant boost for correct state
                doc.metadata["rerank_score"] = final_score
            
            unique_results.sort(key=lambda x: x.metadata["rerank_score"], reverse=True)
            
            # Return top-k reranked
            return unique_results[:TOP_K_RERANK]
        
        return []

if __name__ == "__main__":
    # Test retrieval
    engine = CitizenRetrievalEngine()
    
    # Test 1: General Query
    print("\n--- TEST 1: General Policy Query ---")
    results = engine.retrieve("What are the benefits of PMEGP for manufacturing?")
    for i, res in enumerate(results):
        print(f"\nResult {i+1} (Score: {res.metadata.get('rerank_score', 'N/A')}):")
        print(f"Scheme: {res.metadata.get('scheme_name')} ({res.metadata.get('ministry')})")
        print(f"Content: {res.page_content[:200]}...")

    # Test 2: Filtered Query
    print("\n--- TEST 2: Filtered Query (State: Karnataka) ---")
    results = engine.retrieve("startup grants", filters={"state": "Karnataka"})
    for i, res in enumerate(results):
        print(f"\nResult {i+1} (Score: {res.metadata.get('rerank_score', 'N/A')}):")
        print(f"Scheme: {res.metadata.get('scheme_name')} (State: {res.metadata.get('state')})")
        print(f"Content: {res.page_content[:200]}...")
