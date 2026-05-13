"""
generation/generator.py
Policy Intelligence - Cited Answer Generator

Produces grounded, hallucination-resistant answers using reranked policy chunks.
Supports OpenAI (GPT-4o-mini) and Anthropic (Claude Haiku) via env vars.
"""

import os
from typing import List, Dict, Any
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY


SYSTEM_PROMPT = """You are an expert Indian Government Policy Advisor.
Your role is to answer questions about government schemes using ONLY the provided context.

Rules:
1. Base your answer STRICTLY on the context provided. Do NOT use outside knowledge.
2. Always cite the scheme name, ministry, and source URL at the end.
3. If the context does not contain enough information, say: "The available documents do not cover this query."
4. Structure answers clearly: use bullet points for eligibility/benefits, numbered steps for processes.
5. Keep answers concise but complete — 150-300 words max.
"""

def format_context(chunks: List[Any]) -> str:
    """Format reranked chunks into a readable context block."""
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.metadata
        header = f"[Source {i}] {meta.get('scheme_name', 'Unknown')} | {meta.get('section', 'general').upper()} | {meta.get('ministry', '')}"
        context_parts.append(f"{header}\n{chunk.page_content}")
    return "\n\n---\n\n".join(context_parts)


def format_citations(chunks: List[Any]) -> List[Dict[str, str]]:
    """Extract citation metadata from chunks."""
    seen = set()
    citations = []
    for chunk in chunks:
        meta = chunk.metadata
        key = meta.get("scheme_name", "")
        if key not in seen:
            seen.add(key)
            citations.append({
                "scheme_name": meta.get("scheme_name", "N/A"),
                "ministry": meta.get("ministry", "N/A"),
                "state": meta.get("state", "Central"),
                "section": meta.get("section", "general"),
                "source_url": meta.get("source_url", "N/A"),
                "rerank_score": round(meta.get("rerank_score", 0.0), 4)
            })
    return citations


class PolicyGenerator:
    def __init__(self):
        self.provider = None
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        if OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                self.provider = "openai"
                print("Generator initialized: OpenAI GPT-4o-mini")
            except ImportError:
                print("openai package not installed. Run: pip install openai")

        if not self.client and ANTHROPIC_API_KEY:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                self.provider = "anthropic"
                print("Generator initialized: Anthropic Claude Haiku")
            except ImportError:
                print("anthropic package not installed. Run: pip install anthropic")

        if not self.client and GROQ_API_KEY:
            try:
                from groq import Groq
                self.client = Groq(api_key=GROQ_API_KEY)
                self.provider = "groq"
                print("Generator initialized: Groq Llama-3-70b")
            except ImportError:
                print("groq package not installed. Run: pip install groq")

        if not self.client:
            print("WARNING: No LLM API key found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GROQ_API_KEY in .env")
            print("Running in RETRIEVAL-ONLY mode (no generation).")

    def generate(self, query: str, chunks: List[Any]) -> Dict[str, Any]:
        """
        Generate a cited answer from reranked policy chunks.
        Returns: {answer, citations, provider, chunks_used}
        """
        if not chunks:
            return {
                "answer": "No relevant policy information found for your query.",
                "citations": [],
                "provider": None,
                "chunks_used": 0
            }

        context = format_context(chunks)
        citations = format_citations(chunks)

        user_message = f"""Context:
{context}

Question: {query}

Answer (cite scheme names and ministry):"""

        answer = self._call_llm(user_message)

        return {
            "answer": answer,
            "citations": citations,
            "provider": self.provider,
            "chunks_used": len(chunks)
        }

    def _call_llm(self, user_message: str) -> str:
        if not self.client:
            return "[LLM not configured] Retrieved context is available but no answer was generated."

        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=500
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model="claude-haiku-20240307",
                max_tokens=500,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text

        elif self.provider == "groq":
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=500
            )
            return response.choices[0].message.content

        return "LLM provider not recognized."


if __name__ == "__main__":
    # Quick test (retrieval-only if no API key)
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from retrieval.engine import CitizenRetrievalEngine

    engine = CitizenRetrievalEngine()
    generator = PolicyGenerator()

    test_query = "What is the subsidy amount for PMEGP and who is eligible?"
    print(f"\nQuery: {test_query}\n")

    chunks = engine.retrieve(test_query)
    result = generator.generate(test_query, chunks)

    print(f"Answer:\n{result['answer'].encode('ascii', 'ignore').decode('ascii')}\n")
    print("Citations:")
    for c in result['citations']:
        print(f"  - {c['scheme_name']} | {c['ministry']} | {c['source_url']}")
