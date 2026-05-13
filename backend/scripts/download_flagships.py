import os
import requests

def download_flagships():
    output_dir = "data/raw/pdfs"
    os.makedirs(output_dir, exist_ok=True)
    
    flagships = {
        "PMAY-G": "https://pmayg.nic.in/netiay/PMAYG_Guidelines_English.pdf",
        "PM-KISAN": "https://pmkisan.gov.in/Documents/Revised_Guidelines_PM_Kisan_Scheme.pdf",
        "Ayushman_Bharat": "https://nha.gov.in/img/resources/PM-JAY-Guidelines.pdf",
        "Mudra_Yojana": "https://www.mudra.org.in/Download/PMMY_Guidelines.pdf",
        "PM-USP": "https://education.gov.in/sites/upload_files/mhrd/files/PM-USP_Guidelines.pdf"
    }
    
    for name, url in flagships.items():
        filepath = os.path.join(output_dir, f"{name}_guidelines.pdf")
        print(f"Downloading {name} from {url}...")
        try:
            response = requests.get(url, timeout=20, verify=False, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"  [Success] Saved to {name}_guidelines.pdf")
            else:
                print(f"  [Fail] HTTP {response.status_code}")
        except Exception as e:
            print(f"  [Error] {e}")

if __name__ == "__main__":
    download_flagships()
