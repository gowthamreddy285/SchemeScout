import os
import json
import glob

REQUIRED_KEYS = [
    "scheme_name",
    "ministry",
    "state",
    "year",
    "category",
    "beneficiary",
    "section",
    "source_url"
]

def make_uniform(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return False
        
    if not isinstance(data, list):
        return False
        
    modified = False
    for item in data:
        if "metadata" not in item:
            item["metadata"] = {}
            modified = True
            
        meta = item["metadata"]
        
        new_meta = {}
        for k in REQUIRED_KEYS:
            new_meta[k] = meta.get(k)
        
        # Apply defaults for missing values
        if not new_meta.get("scheme_name"): new_meta["scheme_name"] = "Unknown Scheme"
        if not new_meta.get("ministry"): new_meta["ministry"] = "Government of India"
        if not new_meta.get("state"): new_meta["state"] = "Central"
        if not new_meta.get("year"): new_meta["year"] = 2024
        if not new_meta.get("category"): new_meta["category"] = "General"
        if not new_meta.get("beneficiary"): new_meta["beneficiary"] = "Citizens"
        if not new_meta.get("section"): new_meta["section"] = "overview"
        if new_meta.get("source_url") is None: new_meta["source_url"] = ""
        
        if meta != new_meta:
            item["metadata"] = new_meta
            modified = True
            
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    return False

def main():
    scheme_dir = os.path.join("backend", "data", "raw", "schemes")
    json_files = glob.glob(os.path.join(scheme_dir, "*.json"))
    
    modified_count = 0
    for f in json_files:
        if make_uniform(f):
            print(f"Updated: {os.path.basename(f)}")
            modified_count += 1
            
    print(f"Total files updated: {modified_count} out of {len(json_files)}")

if __name__ == "__main__":
    main()
