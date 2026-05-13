import os
import sys
import json
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from retrieval.engine import CitizenRetrievalEngine
from generation.generator import PolicyGenerator

# Systematic test suite
TEST_QUERIES = [
    {
        "query": "What is the maximum project cost covered under PMEGP?",
        "expected_schemes": ["PMEGP"],
        "category": "fact_checking"
    },
    {
        "query": "Is Mudra Yojana and PMMY the same thing?",
        "expected_schemes": ["Mudra Yojana", "PMMY"],
        "category": "ambiguity"
    },
    {
        "query": "What are the benefits for women entrepreneurs in Karnataka?",
        "expected_schemes": ["Stand-Up India", "NEEDS"],
        "category": "eligibility"
    },
    {
        "query": "How do I register a private limited company?",
        "expected_schemes": [],  # Out of scope
        "category": "out_of_scope"
    }
]

def evaluate():
    print("🚀 Starting Formal Evaluation...")
    engine = CitizenRetrievalEngine()
    generator = PolicyGenerator()
    
    results = []
    total_score = 0
    
    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"[{i}/{len(TEST_QUERIES)}] Query: {test['query']}")
        start_time = time.time()
        
        chunks = engine.retrieve(test['query'])
        response = generator.generate(test['query'], chunks)
        
        latency = time.time() - start_time
        
        # Check retrieval quality
        retrieved_schemes = [doc.metadata.get("scheme_name") for doc in chunks]
        hit = any(expected in retrieved_schemes for expected in test['expected_schemes']) if test['expected_schemes'] else (len(chunks) == 0 or "No relevant information" in response['answer'])
        
        score = 1.0 if hit else 0.0
        total_score += score
        
        results.append({
            "query": test['query'],
            "category": test['category'],
            "retrieved": retrieved_schemes,
            "score": score,
            "latency": round(latency, 2)
        })

    summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_queries": len(TEST_QUERIES),
        "accuracy": total_score / len(TEST_QUERIES),
        "avg_latency": sum(r['latency'] for r in results) / len(results),
        "results": results
    }

    output_path = os.path.join("results", "formal_evaluation.json")
    os.makedirs("results", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ Evaluation Complete. Accuracy: {summary['accuracy']*100}%")
    print(f"📄 Report saved to {output_path}")

if __name__ == "__main__":
    evaluate()
