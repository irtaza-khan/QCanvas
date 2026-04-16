# Cirq-RAG-Code-Assistant: production image (slim).
#
# This image intentionally excludes torch, sentence-transformers, FAISS and
# ChromaDB. The prod runtime uses AWS Bedrock for embeddings and pgvector for
# retrieval (config.json sets models.embedding.provider = "aws" and
# rag.vector_store.type = "pgvector" via env override).
#
# For local development with FAISS / sentence-transformers, use Dockerfile.dev.

# --- Stage 1: build wheels for base deps ------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /wheels

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-base.txt .

RUN pip wheel --wheel-dir /wheels -r requirements-base.txt

# --- Stage 2: runtime -------------------------------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    CIRQ_RAG_LOG_MODE=stdout \
    CIRQ_RAG_LOG_FORMAT=json

# libpq for psycopg runtime; curl kept for container health-check one-liners.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 1000 app \
    && useradd  --system --uid 1000 --gid app --home-dir /app --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements-base.txt ./
RUN pip install --no-index --find-links=/wheels -r requirements-base.txt \
    && rm -rf /wheels

# Only copy what the server actually needs at runtime. Heavy or irrelevant
# directories (notebooks, docs, sample dataset, data/models/vector_index, .cache)
# are excluded via .dockerignore.
COPY config ./config
COPY src ./src
COPY scripts ./scripts
COPY data/knowledge_base ./data/knowledge_base

# Drop privileges.
RUN chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
