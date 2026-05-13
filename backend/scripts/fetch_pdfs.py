import os
import requests
import json
from googlesearch import search
import time

def fetch_scheme_pdfs(output_dir="backend/data/raw/pdfs"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Load all unique scheme names from our JSON files
    schemes = set()
    schemes_dir = "backend/data/raw/schemes"
    for f in os.listdir(schemes_dir):
        if f.endswith(".json"):
            with open(os.path.join(schemes_dir, f), 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    for item in data:
                        if 'metadata' in item and 'scheme_name' in item['metadata']:
                            schemes.add(item['metadata']['scheme_name'])
                except: continue

    print(f"Targeting PDF guidelines for {len(schemes)} schemes...")

    # For each scheme, search for its official PDF guidelines
    for scheme in sorted(list(schemes)):
        filename = f"{scheme.replace(' ', '_').replace('/', '_')}_guidelines.pdf"
        filepath = os.path.join(output_dir, filename)
        
        if os.path.exists(filepath):
            print(f"  [Skip] {scheme} (Already exists)")
            continue

        query = f"{scheme} official guidelines PDF India"
        print(f"  Searching for: {query}")
        
        try:
            # Get the first few results and look for a PDF link
            # googlesearch-python returns a generator of strings
            results = search(query, num_results=5)
            pdf_url = None
            for url in results:
                if url.lower().endswith('.pdf'):
                    pdf_url = url
                    break
            
            if pdf_url:
                print(f"    Downloading from: {pdf_url}")
                response = requests.get(pdf_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"    [Success] Saved to {filename}")
                else:
                    print(f"    [Fail] HTTP Status {response.status_code}")
            else:
                print(f"    [No PDF Link Found]")
            
            # Politeness delay to avoid Google/Portal blocks
            time.sleep(2)
            
        except Exception as e:
            print(f"    [Error] {e}")
            time.sleep(5)

if __name__ == "__main__":
    fetch_scheme_pdfs()
