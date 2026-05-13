import os
import sys
import io
from dotenv import load_dotenv

load_dotenv()

# Force UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from retrieval.engine import CitizenRetrievalEngine
from generation.generator import PolicyGenerator

def sample_outputs():
    engine = CitizenRetrievalEngine()
    generator = PolicyGenerator()
    
    # Test queries
    queries = [
        "What is the maximum project cost covered under PMEGP?",
        "Is Mudra Yojana and PMMY the same thing?",
        "How many installments does PM-KISAN give per year?"
    ]
    
    for q in queries:
        print(f"\nQUERY: {q}")
        chunks = engine.retrieve(q)
        result = generator.generate(q, chunks)
        print(f"ANSWER:\n{result['answer']}")
        print(f"CITATIONS: {[c['scheme_name'] for c in result['citations']]}")
        print("-" * 50)

if __name__ == "__main__":
    sample_outputs()
