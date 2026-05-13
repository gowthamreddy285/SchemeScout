import asyncio
import json
import os
from playwright.async_api import async_playwright
from datetime import datetime

class SchemeScraper:
    def __init__(self, output_dir="data/raw/schemes/automated"):
        self.output_dir = output_dir
        self.base_url = "https://www.myscheme.gov.in"
        os.makedirs(self.output_dir, exist_ok=True)

    async def get_scheme_urls(self, search_query):
        """Discovers scheme detail URLs using a search trigger."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            search_url = f"{self.base_url}/search"
            print(f"Triggering search for: {search_query}")
            await page.goto(search_url, wait_until="networkidle", timeout=60000)
            
            # Input query and press Enter
            await page.fill("input[placeholder*='Search']", search_query)
            await page.keyboard.press("Enter")
            
            # Wait for results to hydrate
            print("  Waiting 5s for search results...")
            await asyncio.sleep(5)
            
            # Extract links
            links = await page.eval_on_selector_all(
                "a", 
                "elements => elements.map(el => el.href).filter(h => h && h.includes('/schemes/') && !h.includes('/search'))"
            )
            
            unique_links = list(set([link for link in links if '/schemes/' in link]))
            print(f"Found {len(unique_links)} potential schemes.")
            await browser.close()
            return unique_links

    async def scrape_scheme_details(self, url):
        """Extracts detailed information from a single scheme page."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                print(f"Scraping: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                # Wait for the main heading to ensure page is at least partially loaded
                await page.wait_for_selector("h1", timeout=20000)
                name = await page.inner_text("h1")
                
                # Try to get breadcrumb safely
                breadcrumb = ""
                try: breadcrumb = await page.inner_text(".breadcrumb")
                except: pass
                
                # Extract Ministry & Category from breadcrumbs or meta
                ministry = "Central Government" # Default
                if "Ministry" in breadcrumb:
                    parts = breadcrumb.split(">")
                    for p_part in parts:
                        if "Ministry" in p_part:
                            ministry = p_part.strip()
                            break

                # Extract Tab Content (Eligibility, Benefits, etc.)
                # myScheme uses clickable tabs. We'll click each to ensure content is loaded/visible
                tabs = {
                    "details": "Details",
                    "benefits": "Benefits",
                    "eligibility": "Eligibility",
                    "exclusion": "Exclusion",
                    "application": "Application Process",
                    "documents": "Documents Required"
                }
                
                content_blocks = []
                
                for key, label in tabs.items():
                    try:
                        # Try to find and click the tab
                        tab_selector = f"text='{label}'"
                        if await page.query_selector(tab_selector):
                            await page.click(tab_selector)
                            await asyncio.sleep(0.5) # Wait for animation
                            
                            # Extract text from the active panel
                            text = await page.inner_text(".tab-content") # Common selector for panels
                            if text:
                                content_blocks.append({
                                    "text": f"{label}: {text}",
                                    "metadata": {
                                        "scheme_name": name,
                                        "ministry": ministry,
                                        "state": "Central", # Adjust if state-specific breadcrumb found
                                        "section": key,
                                        "source_url": url,
                                        "scraped_at": datetime.now().isoformat()
                                    }
                                })
                    except Exception as e:
                        print(f"  Error scraping tab {label}: {e}")

                return content_blocks

            except Exception as e:
                print(f"  Critical error on {url}: {e}")
                return []
            finally:
                await browser.close()

    async def run_batch(self, category_urls):
        all_data = []
        for cat_url in category_urls:
            urls = await self.get_scheme_urls(cat_url)
            for url in urls:
                details = await self.scrape_scheme_details(url)
                all_data.extend(details)
                
                # Save incrementally to avoid data loss
                batch_file = os.path.join(self.output_dir, f"batch_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
                with open(batch_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=2, ensure_ascii=False)
                
                print(f"Saved {len(details)} chunks for {url}")
                await asyncio.sleep(2) # Politeness delay

if __name__ == "__main__":
    scraper = SchemeScraper()
    # Targeting the requested domains via search queries
    target_queries = ["Housing", "Women", "Child"]
    asyncio.run(scraper.run_batch(target_queries))
