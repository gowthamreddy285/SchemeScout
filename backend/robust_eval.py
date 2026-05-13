import os
import sys
import json
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure we can import from the current directory (backend)
sys.path.insert(0, os.getcwd())

from retrieval.engine import CitizenRetrievalEngine
from generation.generator import PolicyGenerator
import config

print(f"DEBUG: Using GROQ_MODEL={getattr(config, 'GROQ_MODEL', 'NOT FOUND')}")

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
        print(f"\n[{i}/15] Query: {query}")
        try:
            chunks = engine.retrieve(query)
            result = generator.generate(query, chunks)
            
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Citations: {[c['scheme_name'] for c in result['citations']]}")
            
            results.append({
                "id": i,
                "query": query,
                "answer": result["answer"],
                "citations": [c["scheme_name"] for c in result["citations"]],
                "chunks_used": result["chunks_used"]
            })
        except Exception as e:
            print(f"CRITICAL ERROR on Q{i}: {e}")
    
    output_path = "final_eval_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nEvaluation complete. Results saved to {output_path}")

if __name__ == "__main__":
    run_evaluation()
