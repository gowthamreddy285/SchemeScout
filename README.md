# 🚀 SchemeScout: High-Precision Indian Policy RAG

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-05998b?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-10%20Passed-brightgreen.svg)](tests/test_pipeline.py)

**SchemeScout** is a production-grade Retrieval-Augmented Generation (RAG) system built to navigate the complexity of 400+ Indian Government schemes. It delivers high-fidelity, cited answers by combining semantic search with state-of-the-art reranking.

---

## ✨ Key Features

- **🎯 High-Precision Retrieval**: Hybrid search (Vector + BM25) coupled with `BAAI/bge-reranker-base` for extreme accuracy.
- **📑 Verifiable Citations**: Every answer includes direct links to official government PDFs and source portals.
- **🇮🇳 State-Aware Intelligence**: Specialized boosting for state-specific policies (starting with Karnataka).
- **🛡️ Hallucination Guardrails**: Multi-stage validation to ensure the LLM strictly adheres to provided policy context.
- **🐳 One-Command Setup**: Fully dockerized environment for instant local deployment.

---

## 🏗️ Architecture

SchemeScout uses a multi-stage pipeline designed for precision over speed:

1.  **Ingestion**: Recursive chunking of PDF guidelines and structured JSON data.
2.  **Retrieval**: Two-stage retrieval (Vector + BM25) followed by a **BGE Cross-Encoder** reranker.
3.  **Generation**: **Llama 3.3 (70B)** via Groq for sophisticated reasoning and cited report generation.

> [!TIP]
> Check out [ARCHITECTURE.md](./ARCHITECTURE.md) for a deep dive into our technical implementation.

---

## 🚀 Quick Start

### Option A: Using Docker (Recommended)
```bash
docker-compose up --build
```
- Frontend: `http://localhost:80`
- API: `http://localhost:8000`

### Option B: Manual Setup

#### 1. Backend
```bash
cd backend
pip install -r requirements.txt
# Add your GROQ_API_KEY to .env
python ingestion/embedder.py  # Index the data
python -m api.main             # Start the API
```

#### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Systematic Evaluation

We maintain a strict evaluation pipeline to prevent regression:
- **Unit Tests**: 10 core tests covering dimension validation, retrieval hits, and API fallbacks.
- **Benchmarking**: [scripts/evaluate.py](./scripts/evaluate.py) runs systematic tests across 15+ complex policy queries.

Run tests:
```bash
pytest tests/ -v
```

---

## 📂 Project Structure

```text
├── backend/
│   ├── api/            # FastAPI Endpoints
│   ├── ingestion/      # Data Embedder & PDF Parsers
│   ├── retrieval/      # Hybrid Search & Reranking logic
│   └── generation/     # LLM Prompt Engineering & Guardrails
├── frontend/           # React + Tailwind Dashboard
├── results/            # Historical Evaluation Data
├── tests/              # Pytest Suite (10/10 Passed)
└── ARCHITECTURE.md     # Technical Deep-Dive
```

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙌 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
