import os
import json
import glob

def main():
    scheme_dir = os.path.join("backend", "data", "raw", "schemes")
    # Get all json files, but exclude master_schemes.json if it already exists
    json_files = [f for f in glob.glob(os.path.join(scheme_dir, "*.json")) if not f.endswith("master_schemes.json")]
    
    merged_data = []
    
    for f in json_files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if isinstance(data, list):
                    merged_data.extend(data)
                elif isinstance(data, dict):
                    merged_data.append(data)
        except Exception as e:
            print(f"Error reading {os.path.basename(f)}: {e}")
            
    output_file = os.path.join(scheme_dir, "master_schemes.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully merged {len(json_files)} files into master_schemes.json")
    print(f"Total schemes combined: {len(merged_data)}")

if __name__ == "__main__":
    main()
