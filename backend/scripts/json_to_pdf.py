import json
import asyncio
import os
import glob
from playwright.async_api import async_playwright

async def generate_pdfs():
    files = glob.glob("data/raw/schemes/*.json")
    out_dir = "data/raw/pdfs"
    os.makedirs(out_dir, exist_ok=True)
    
    schemes_processed = set()
    total_generated = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except Exception:
                    continue
                
                if not isinstance(data, list): continue

                for item in data:
                    meta = item.get("metadata", {})
                    name = meta.get("scheme_name", "Unknown_Scheme")
                    text = item.get("text", "")
                    
                    if name in schemes_processed or not text:
                        continue
                        
                    schemes_processed.add(name)
                    safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
                    pdf_path = os.path.join(out_dir, f"{safe_name}.pdf")
                    
                    html_content = f"""
                    <html>
                    <head><style>
                        body {{ font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }}
                        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                        .meta {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                        .content {{ font-size: 14px; color: #34495e; }}
                    </style></head>
                    <body>
                        <h1>{name}</h1>
                        <div class="meta">
                            <strong>Category:</strong> {meta.get('category', 'N/A')}<br>
                            <strong>State/Ministry:</strong> {meta.get('state', meta.get('ministry', 'N/A'))}
                        </div>
                        <div class="content">
                            {text}
                        </div>
                    </body>
                    </html>
                    """
                    
                    await page.set_content(html_content)
                    await page.pdf(path=pdf_path, format="A4")
                    print(f"Generated PDF for: {name}")
                    total_generated += 1

        await browser.close()
        print(f"\\nSuccessfully generated {total_generated} PDFs from JSON files.")

if __name__ == "__main__":
    asyncio.run(generate_pdfs())
