import os
import json
import pandas as pd
import kagglehub

def main():
    print("Downloading dataset from Kaggle...")
    path = kagglehub.dataset_download('jainamgada45/indian-government-schemes')
    print(f"Downloaded to: {path}")
    
    csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the dataset.")
        return
        
    csv_path = os.path.join(path, csv_files[0])
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Handle NaN values
    df = df.fillna('')
    
    schemes_json = []
    
    for _, row in df.iterrows():
        scheme_name = row.get('scheme_name', '').strip()
        if not scheme_name:
            continue
            
        details = row.get('details', '').strip()
        benefits = row.get('benefits', '').strip()
        eligibility = row.get('eligibility', '').strip()
        application = row.get('application', '').strip()
        documents = row.get('documents', '').strip()
        
        # Combine into a single descriptive text block
        text_parts = []
        if details: 
            text_parts.append(f"{scheme_name}: {details}")
        else: 
            text_parts.append(f"{scheme_name}")
        
        if eligibility: text_parts.append(f"Eligibility: {eligibility}")
        if benefits: text_parts.append(f"Benefits: {benefits}")
        if application: text_parts.append(f"Application Process: {application}")
        if documents: text_parts.append(f"Required Documents: {documents}")
        
        text = " ".join(text_parts)
        
        # Determine state/central based on 'level'
        level_val = row.get('level', '').strip()
        state_val = level_val if level_val else "Central"
        
        # Infer a rough beneficiary from tags if possible
        tags_val = row.get('tags', '').strip()
        
        metadata = {
            "scheme_name": scheme_name,
            "ministry": "Government of India", # Dataset doesn't have ministry, using a fallback
            "state": state_val,
            "year": 2024,
            "category": row.get('schemeCategory', '').strip() or "General",
            "beneficiary": tags_val if tags_val else "Citizens",
            "section": "overview"
        }
        
        # Source URL
        slug = row.get('slug', '').strip()
        if slug:
            metadata["source_url"] = f"https://www.myscheme.gov.in/schemes/{slug}"
        else:
            metadata["source_url"] = ""
            
        schemes_json.append({
            "text": text,
            "metadata": metadata
        })
        
    output_path = os.path.join("backend", "data", "raw", "schemes", "kaggle_schemes.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schemes_json, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully processed and saved {len(schemes_json)} schemes to {output_path}")

if __name__ == "__main__":
    main()
