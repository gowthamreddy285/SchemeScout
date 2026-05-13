"""
generation/generator.py
Policy Intelligence - Cited Answer Generator

Produces grounded, hallucination-resistant answers using reranked policy chunks.
Supports OpenAI (GPT-4o-mini) and Anthropic (Claude Haiku) via env vars.
"""

import os
from typing import List, Dict, Any
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, GROQ_MODEL


SYSTEM_PROMPT = """You are an expert, proactive Indian Government Policy Advisor.
Your goal is to provide high-fidelity, comprehensive, and grounded reports on government schemes.

Output Format:
1. Header: Use a clear, bold title for the query.
2. Structure: Group related schemes into categories (e.g., "Five Guarantees," "Education & Skills," "Startup Support").
3. For Each Scheme:
   - Provide a bold Scheme Name.
   - List Eligibility and Benefits clearly using bullet points.
   - Mention the Application Process or Seva Sindhu links if available.
4. Summary: End with a proactive note on how to apply or what the next steps are.

Rules:
1. Base your answer ONLY on the provided context.
2. If the context is broad (e.g., "Karnataka schemes"), provide a detailed breakdown of all relevant results.
3. If no information is found, admit it clearly without hallucinating.
4. Use a professional, human-like, and helpful tone.
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
                "text": chunk.page_content,
                "rerank_score": round(meta.get("rerank_score", 0.0), 4)
            })
    return citations


class PolicyGenerator:
    def __init__(self):
        self.provider = None
        self.client = None
        self.model = GROQ_MODEL
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
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.1,
                    max_tokens=1500
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI Error: {e}")
                return "[Error] Generation failed. Here is the raw context for your reference:\n\n" + user_message[:500] + "..."

        elif self.provider == "anthropic":
            try:
                response = self.client.messages.create(
                    model="claude-haiku-20240307",
                    max_tokens=1500,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_message}]
                )
                return response.content[0].text
            except Exception as e:
                print(f"Anthropic Error: {e}")
                return "[Error] Generation failed. Please try again."

        elif self.provider == "groq":
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.1,
                    max_tokens=1500
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Groq Error: {e}")
                return "[Error] Generation failed. Please try again."

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
