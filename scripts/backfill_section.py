"""
Backfill script: Adds 'section' field to all scheme JSON metadata.
Maps document_type → clean section values and adds section field.
"""

import os
import json
import glob

SCHEMES_DIR = r"c:\Users\gowtham\Desktop\citizen-rag\data\raw\schemes"

# Map existing document_type values → clean section names
SECTION_MAP = {
    "eligibility_guidelines": "eligibility",
    "benefits_summary":       "benefits",
    "application_guide":      "application",
    "summary":                "overview",
    "overview":               "overview",
    "general":                "overview",
    "scheme_overview":        "overview",
    "guidelines":             "overview",
    "faq":                    "faq",
    "funding":                "benefits",
    "subsidy":                "benefits",
    "loan_details":           "benefits",
}

def infer_section_from_text(text: str) -> str:
    """Infer section from text content if document_type is missing or unmapped."""
    text_lower = text.lower()
    if any(k in text_lower for k in ["eligib", "who can apply", "criteria"]):
        return "eligibility"
    elif any(k in text_lower for k in ["benefit", "subsidy", "grant", "amount", "loan", "financial"]):
        return "benefits"
    elif any(k in text_lower for k in ["apply", "application", "process", "document", "how to"]):
        return "application"
    else:
        return "overview"

def backfill(json_path: str) -> int:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    modified = 0
    for item in data:
        meta = item.get("metadata", {})
        doc_type = meta.get("document_type", "")
        
        # Map to clean section name
        section = SECTION_MAP.get(doc_type)
        if not section:
            section = infer_section_from_text(item.get("text", ""))
        
        # Add section field (keep document_type for backward compat)
        meta["section"] = section
        item["metadata"] = meta
        modified += 1

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return modified

if __name__ == "__main__":
    json_files = glob.glob(os.path.join(SCHEMES_DIR, "*.json"))
    # Exclude download scripts accidentally matched
    json_files = [f for f in json_files if not f.endswith("download_pdfs.py")]
    
    total = 0
    for path in sorted(json_files):
        count = backfill(path)
        total += count
        print(f"  [{count} chunks] {os.path.basename(path)}")

    print(f"\nDone. Backfilled 'section' field across {total} chunks in {len(json_files)} files.")
