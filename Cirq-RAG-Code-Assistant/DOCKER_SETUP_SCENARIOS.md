# Cirq-RAG Docker Setup Scenarios

This guide explains how to run Cirq-RAG in different scenarios, with exact Docker commands for build and run.

## 0) Before You Start (Windows)

1. Start Docker Desktop and wait until it shows "Engine running".
2. Open a terminal at the workspace root:
   - `D:/Study Material/FYP/Practice/Test8/QCanvas`
3. Verify Docker daemon is reachable:

```powershell
docker version
docker info
```

If daemon is not running, any `docker images` or `docker compose` command will fail.

---

## 1) Scenario A (Recommended): Bedrock + pgvector (Lightweight)

Use this when:
- You are using AWS Bedrock keys.
- You want a much smaller image.
- You do not need local FAISS / sentence-transformers / torch workflows.

This uses:
- `docker-compose.prod.yml`
- `Cirq-RAG-Code-Assistant/Dockerfile` (slim)
- `requirements-base.txt`

### Required env vars

Set these in your environment or in `.env` used by compose:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`
- `BEDROCK_INFERENCE_PROFILE_ARN_DESIGNER`
- `BEDROCK_INFERENCE_PROFILE_ARN_OPTIMIZER`
- `BEDROCK_INFERENCE_PROFILE_ARN_VALIDATOR`
- `BEDROCK_INFERENCE_PROFILE_ARN_EDUCATIONAL`
- `CIRQ_RAG_API_KEY`

Optional defaults:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `CIRQ_RAG_ALLOWED_ORIGINS`

### Build and run

```powershell
# from workspace root
docker compose -f docker-compose.prod.yml build cirq_agent
docker compose -f docker-compose.prod.yml up -d postgres redis cirq_agent
```

### Verify

```powershell
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f cirq_agent
```

Health check:

```powershell
curl http://localhost:8001/health
```

### Stop

```powershell
docker compose -f docker-compose.prod.yml down
```

---

## 2) Scenario B: Full Development Stack (Heavy)

Use this when:
- You need local RAG experiments with FAISS/Chroma.
- You need sentence-transformers/torch and extra research dependencies.
- You need hot-reload with bind mounts.

This uses:
- `docker-compose.yml`
- `Cirq-RAG-Code-Assistant/Dockerfile.dev`
- `requirements-dev.txt` (heavy)

### Build and run

```powershell
# from workspace root
docker compose build cirq_agent
docker compose up -d cirq_agent
```

If you also want full app integration in dev:

```powershell
docker compose up -d postgres redis cirq_agent backend
```

### Verify

```powershell
docker compose ps
docker compose logs -f cirq_agent
```

Health check:

```powershell
curl http://localhost:8001/health
```

### Stop

```powershell
docker compose down
```

---

## 3) Scenario C: Build/Run Without Compose (Slim Image Only)

Use this for quick local smoke testing of the lightweight image.

### Build image

```powershell
# from workspace root
docker build -t cirq-rag:slim -f ./Cirq-RAG-Code-Assistant/Dockerfile ./Cirq-RAG-Code-Assistant
```

### Run container

```powershell
docker run --rm -p 8001:8000 \
  -e ENVIRONMENT=production \
  -e AWS_ACCESS_KEY_ID=$env:AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$env:AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e CIRQ_RAG_API_KEY=replace_with_secure_key \
  -e CIRQ_RAG_VECTOR_STORE_TYPE=pgvector \
  -e CIRQ_RAG_DB_URL=postgresql://postgres:postgres@host.docker.internal:5433/qcanvas_db \
  cirq-rag:slim
```

### Verify

```powershell
curl http://localhost:8001/health
```

---

## 4) Scenario D: Rebuild Fast After Small Changes

When only app source changed (not dependencies), rebuild the target service only:

```powershell
# prod stack
docker compose -f docker-compose.prod.yml build cirq_agent
docker compose -f docker-compose.prod.yml up -d cirq_agent

# dev stack
docker compose build cirq_agent
docker compose up -d cirq_agent
```

---

## 5) Disk Cleanup (If Docker Consumes Too Much Space)

Check current usage:

```powershell
docker system df
```

Remove stopped containers, dangling images, and unused networks:

```powershell
docker system prune -f
```

Aggressive cleanup (removes all unused images and build cache):

```powershell
docker image prune -a -f
docker builder prune -a -f
```

Use aggressive cleanup carefully if you need cached layers for speed.

---

## 6) Which Scenario Should You Use?

- If you are now using AWS Bedrock keys for normal QCanvas flow: use **Scenario A**.
- If you are doing local embedding/model experiments: use **Scenario B**.
- If you just need a quick sanity run of Cirq-RAG container: use **Scenario C**.

For your current setup and image-size concerns, Scenario A is the correct default.

---

## 7) Expected Storage Per Scenario

These are practical ranges for a typical Windows laptop with Docker Desktop, based on your current dependency layout.

| Scenario | What is built | Expected image size | Typical total Docker usage during/after build |
|---|---|---:|---:|
| A: Bedrock + pgvector (lightweight) | `Cirq-RAG-Code-Assistant/Dockerfile` | ~0.5 GB to 1.2 GB | ~1 GB to 3 GB |
| B: Full dev (heavy) | `Cirq-RAG-Code-Assistant/Dockerfile.dev` | ~3 GB to 7 GB | ~6 GB to 15+ GB |
| C: Slim without compose | Same as Scenario A Dockerfile | ~0.5 GB to 1.2 GB | ~1 GB to 3 GB |

Notes:
- The "Expected image size" is what `docker images` usually reports for the final image.
- "Typical total Docker usage" includes layers, build cache, and intermediate images, which is why it is much higher.
- Rebuilding Scenario B multiple times without cleanup can quickly push usage toward the higher end (including ~11 GB or more).

Quick check commands:

```powershell
docker images
docker system df
docker builder prune -a -f
```
