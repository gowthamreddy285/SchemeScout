# SchemeScout 🛰️
### Policy Intelligence, Simply Delivered.

SchemeScout is a production-grade **RAG (Retrieval-Augmented Generation)** platform designed to provide Indian citizens with instant, accurate, and verifiable information on government schemes. It bridges the gap between complex official documents and citizen needs through a high-fidelity intelligence layer.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![React](https://img.shields.io/badge/react-18-61dafb.svg)

---

## 🚀 Key Features

- **500+ Scheme Library**: Deep knowledge across Central and State-level policies (Karnataka, TN, Maharashtra, Gujarat, Delhi).
- **State-Aware Retrieval**: Intelligently boosts results based on the user's jurisdiction (e.g., searching for "scholarships" in Karnataka prioritizes regional SSP policies).
- **Hybrid Search Engine**: Combines **ChromaDB Vector Search** for semantic meaning with **BM25 Keyword Search** for exact terminology.
- **Expert Reranking**: Uses `BAAI/bge-reranker-base` to ensure the most relevant policy text is always prioritized for the LLM.
- **Human-Centric UI**: An ultra-minimalist React interface focused on speed, clarity, and verifiable citations.
- **Evidence Layer**: Direct links to official government guidelines and a growing library of flagship PDF sources.

---

## 🛠️ Technical Stack

- **Frontend**: React (Vite), Tailwind CSS, Framer Motion, Lucide Icons.
- **Backend**: FastAPI (Python), Uvicorn.
- **Vector DB**: ChromaDB (persistent storage).
- **Embeddings**: `BAAI/bge-small-en-v1.5` (HuggingFace).
- **LLM**: Groq (Llama-3 70B) for high-speed, grounded generation.
- **Data**: 300+ JSON structured scheme batches + Flagship PDF guidelines.

---

## 📂 Project Structure

```text
citizen-rag/
├── frontend/             # React/Vite Application
│   └── src/              # UI Components & App Logic
├── backend/              # FastAPI Intelligence Layer
│   ├── api/              # API Endpoints
│   ├── retrieval/        # Hybrid Search & Reranking Engine
│   ├── ingestion/        # Document Embedding Pipeline
│   ├── generation/       # LLM Prompting & Formatting
│   ├── data/             # Raw Policy Data (JSON & PDF)
│   └── chroma_db/        # Persistent Vector Storage
└── config.py             # Unified Project Configuration
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Node.js & npm
- API Keys: Groq (for generation)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file in the root:
```env
GROQ_API_KEY=your_key_here
```

### 3. Data Ingestion
Populate the vector database with the 500+ scheme library:
```bash
python -m ingestion.embedder
```

### 4. Running the App
**Start Backend:**
```bash
python -m api.main
```

**Start Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🤝 Contributing
SchemeScout is built for the public good. Contributions to scheme data, regional support, or UI improvements are welcome. Please open an issue or submit a PR.

---

## 📄 License
This project is licensed under the MIT License.
