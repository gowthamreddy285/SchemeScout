# ── Backend Dockerfile ────────────────────────────────────────────────────────
# Uses CPU-only PyTorch to keep image size small (~2 GB vs ~6 GB with CUDA).
# Install only production dependencies (requirements.txt, not requirements-dev.txt).
FROM python:3.11-slim

WORKDIR /app

# System deps: build tools for chromadb C extensions + libgomp for ONNX/torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ── Install Python dependencies ───────────────────────────────────────────────
COPY requirements.txt .

# 1. Install CPU-only PyTorch first (avoids pulling the massive CUDA wheels)
RUN pip install --no-cache-dir \
    torch==2.3.0+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

# 2. Install remaining production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ─────────────────────────────────────────────────────
COPY . .

# Non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Workers: use 1 for dev/small; scale via docker-compose replicas in prod
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
