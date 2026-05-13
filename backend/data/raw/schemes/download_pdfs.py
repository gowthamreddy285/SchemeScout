import os
import requests

# PDF Directory
PDF_DIR = "c:\\Users\\gowtham\\Desktop\\citizen-rag\\data\\raw\\schemes\\source_pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

# Target PDF URLs
pdf_urls = {
    "SISFS_Guidelines.pdf": "https://www.startupindia.gov.in/content/dam/invest-india/Templates/public/Seed_Fund_Guidelines.pdf",
    "PM_KISAN_Guidelines.pdf": "https://pmkisan.gov.in/Documents/RevisedOperationalGuidelines.pdf",
    "PMEGP_Guidelines.pdf": "https://slbcorissa.com/PMEGP-Scheme-Guidelines.pdf",
    "RKVY_RAFTAAR_Guidelines.pdf": "https://nivedi.res.in/pdf/RKVY-RAFTAAR%20Guidelines.pdf"
}

def download_pdfs():
    print(f"Starting download to {PDF_DIR}...")
    for filename, url in pdf_urls.items():
        try:
            print(f"  Downloading {filename}...")
            response = requests.get(url, timeout=30, verify=False) # verify=False for some govt sites with SSL issues
            if response.status_code == 200:
                with open(os.path.join(PDF_DIR, filename), 'wb') as f:
                    f.write(response.content)
                print(f"    Success!")
            else:
                print(f"    Failed with status code: {response.status_code}")
        except Exception as e:
            print(f"    Error: {e}")

if __name__ == "__main__":
    download_pdfs()
