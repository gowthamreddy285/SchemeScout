import os
import requests

# PDF Directory
PDF_DIR = "c:\\Users\\gowtham\\Desktop\\citizen-rag\\data\\raw\\schemes\\source_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

# Target PDF URLs with browser headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

pdf_urls = {
    "PM_Vishwakarma_Guidelines.pdf": "https://pmvishwakarma.gov.in/cdn/MiscFiles/eng_v30.0_PM_Vishwakarma_Guidelines_final.pdf",
    "SISFS_Guidelines.pdf": "https://www.startupindia.gov.in/content/dam/invest-india/Templates/public/SISFS_Guidelines.pdf",
    "PM_KISAN_Guidelines.pdf": "https://pmkisan.gov.in/Documents/RevisedOperationalGuidelines.pdf"
}

def download_pdfs():
    print(f"Starting download to {PDF_DIR}...")
    for filename, url in pdf_urls.items():
        try:
            print(f"  Downloading {filename} from {url}...")
            response = requests.get(url, headers=headers, timeout=60, verify=False)
            if response.status_code == 200:
                with open(os.path.join(PDF_DIR, filename), 'wb') as f:
                    f.write(response.content)
                print(f"    Success! Saved {os.path.getsize(os.path.join(PDF_DIR, filename))} bytes.")
            else:
                print(f"    Failed with status code: {response.status_code}")
        except Exception as e:
            print(f"    Error: {e}")

if __name__ == "__main__":
    download_pdfs()
