import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix Unicode issues on Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from retrieval.engine import CitizenRetrievalEngine
from generation.generator import PolicyGenerator

def run_evaluation():
    print("Initializing RAG Pipeline...")
    engine = CitizenRetrievalEngine()
    generator = PolicyGenerator()
    
    queries = [
        "I am a 19-year-old SC category student who wants to start a small business — which schemes apply to me?",
        "Can a woman who already has a running business apply for Stand-Up India or is it only for new businesses?",
        "My family owns agricultural land but I want to start a tech startup — am I eligible for any schemes?",
        "What is the exact subsidy percentage under CLCSS for technology upgradation?",
        "How many installments does PM-KISAN give per year and when are they credited?",
        "What is the maximum project cost covered under PMEGP?",
        "I want to apply for Udyam registration — what happens after I get the certificate?",
        "What is the process to get DPIIT recognition and how long does it take?",
        "What schemes are available specifically for women in northeastern states of India?",
        "Are there any government schemes for handicraft artisans?",
        "What support does the government give for cold storage infrastructure for farmers?",
        "What is the difference between PMEGP and CLCSS?",
        "Is Mudra Yojana and PMMY the same thing?",
        "What are the income tax slabs for small business owners in India?",
        "How do I register a private limited company in India?"
    ]
    
    results = []
    
    for i, query in enumerate(queries, 1):
        print(f"[{i}/15] Processing: {query[:50]}...")
        chunks = engine.retrieve(query)
        result = generator.generate(query, chunks)
        
        results.append({
            "id": i,
            "query": query,
            "answer": result["answer"],
            "citations": [c["scheme_name"] for c in result["citations"]],
            "chunks_used": result["chunks_used"]
        })
    
    output_path = "evaluation_round_2_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nEvaluation complete. Results saved to {output_path}")
    
    # Print a summary to the console
    for res in results:
        print(f"\n--- Q{res['id']}: {res['query']} ---")
        print(f"Answer:\n{res['answer']}\n")
        print(f"Citations: {', '.join(res['citations'])}")
        print("-" * 50)

if __name__ == "__main__":
    run_evaluation()
