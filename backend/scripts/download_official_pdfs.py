import json
import os
import glob
import time
import requests
from googlesearch import search

def download_official_pdfs():
    files = glob.glob("data/raw/schemes/*.json")
    out_dir = "data/raw/official_pdfs"
    os.makedirs(out_dir, exist_ok=True)
    
    schemes_processed = set()
    failed_schemes = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"Starting to hunt for official PDFs using Google. Saving to: {out_dir}")

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception:
                continue
            
            if not isinstance(data, list): continue

            for item in data:
                meta = item.get("metadata", {})
                name = meta.get("scheme_name", "")
                
                if not name or name in schemes_processed:
                    continue
                    
                schemes_processed.add(name)
                safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
                pdf_path = os.path.join(out_dir, f"{safe_name}.pdf")
                
                if os.path.exists(pdf_path):
                    continue

                # Focusing specifically on .gov.in domains and pdf filetype
                query = f'"{name}" official guidelines filetype:pdf site:gov.in'
                print(f"\\nSearching for: {query}")
                
                success = False
                try:
                    # Search using googlesearch-python
                    for url in search(query, num_results=3, lang="en"):
                        if '.pdf' in url.lower():
                            print(f"  -> Found PDF URL: {url}")
                            try:
                                response = requests.get(url, headers=headers, timeout=15, verify=False)
                                if response.status_code == 200 and b'%PDF' in response.content[:10]:
                                    with open(pdf_path, 'wb') as pdf_file:
                                        pdf_file.write(response.content)
                                    print(f"  -> Successfully downloaded: {safe_name}.pdf")
                                    success = True
                                    break
                                else:
                                    print(f"  -> Failed: Not a valid PDF or bad status ({response.status_code})")
                            except Exception as e:
                                print(f"  -> Download error: {e}")
                except Exception as e:
                    print(f"  -> Search error: {e}")
                
                if not success:
                    print(f"  -> No working direct PDF link found.")
                    failed_schemes.append(name)
                
                # Sleep to avoid rate limiting from Google
                time.sleep(3)
                
                # Update failed list every iteration so user can check
                with open("data/raw/failed_downloads.json", "w") as out:
                    json.dump(failed_schemes, out, indent=2)

    print(f"\\nFinished. Failed to download {len(failed_schemes)} schemes.")
    print(f"List saved to data/raw/failed_downloads.json")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    download_official_pdfs()
