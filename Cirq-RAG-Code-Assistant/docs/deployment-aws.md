# Deploying Cirq-RAG-Code-Assistant on AWS

This document walks through a production deployment of the Cirq RAG service
on AWS ECS Fargate, backed by RDS Postgres (pgvector) and ElastiCache Redis.
It is a higher-level companion to [`deploy/ecs/README.md`](../deploy/ecs/README.md),
which contains the copy-paste CLI commands.

## Target topology

```
          ┌────────────┐
          │ QCanvas FE │  HTTPS + X-API-Key
          └─────┬──────┘
                │
                ▼
         ┌─────────────┐       ┌──────────────────────┐
         │    ALB      │──────▶│ ECS Fargate service  │
         │ idle 180s   │       │ cirq-agent (Nx tasks)│
         └─────────────┘       └─────────┬────────────┘
                                         │
                ┌────────────────────────┼─────────────────────────┐
                ▼                        ▼                         ▼
         ┌────────────┐          ┌──────────────┐         ┌────────────────┐
         │ RDS/Aurora │          │ ElastiCache  │         │ AWS Bedrock    │
         │ Postgres + │          │    Redis     │         │ Claude, Nova   │
         │ pgvector   │          │ run history  │         │ (LLM + embed)  │
         └────────────┘          └──────────────┘         └────────────────┘
                                         ▲
                                         │
                                   ┌──────────────┐
                                   │ Secrets Mgr  │
                                   │ DB / Redis / │
                                   │ API keys /   │
                                   │ Bedrock ARNs │
                                   └──────────────┘
```

## Component responsibilities

| Component | Responsibility |
|-----------|----------------|
| ALB | HTTPS termination, `/health` target-group check, raise idle timeout to ≥ 180 s. |
| ECS Fargate | Runs the slim `Dockerfile` image, scales horizontally, pulls secrets at task boot via Secrets Manager. |
| RDS / Aurora Postgres 15.5+ | Authoritative store for the RAG knowledge base via `pgvector` (schema `cirq_rag`). |
| ElastiCache Redis | Shared run-history store with 24 h TTL and a ZSET index. |
| Bedrock | All four agent LLMs + Amazon Nova embeddings. The task role grants `bedrock:InvokeModel`. |
| Secrets Manager | DB URL, Redis URL, API key, Bedrock inference-profile ARNs. |
| CloudWatch Logs | JSON-line logs from `CIRQ_RAG_LOG_FORMAT=json`, log group `/ecs/cirq-agent`. |

## Request flow

1. Browser -> ALB -> ECS task (port 8000).
2. `require_api_key` FastAPI dependency validates `X-API-Key` via
   `hmac.compare_digest` against `CIRQ_RAG_API_KEY` (from Secrets Manager).
3. `generate_code` runs the Designer / Validator / Optimizer / Final-Validator /
   Educational pipeline. RAG retrieval hits `cirq_rag.rag_knowledge_base` in
   Postgres via pgvector cosine distance.
4. Each Bedrock call is IAM-authenticated via the task role.
5. A successful run is serialized and `ZADD`'d into Redis (`cirq_rag:runs:index`)
   and `SETEX`'d at `cirq_rag:run:{run_id}` with a 24 h TTL.

## What the slim image does NOT contain

To keep cold-start fast and the image small:

- `torch`
- `transformers`
- `sentence-transformers`
- `faiss-cpu`
- `chromadb`

The production stack uses Bedrock for embeddings (`aws.embeddings.model_id`)
and pgvector for retrieval, so none of those are needed at runtime. They
remain available in `Dockerfile.dev` for local experiments.

## Required env vars (prod)

The server refuses to start with `ENVIRONMENT=production` if any of these are
missing:

| Env var | Source | Purpose |
|---------|--------|---------|
| `AWS_DEFAULT_REGION` | task env | Bedrock region |
| `CIRQ_RAG_API_KEY` | Secrets Manager | API auth |
| `CIRQ_RAG_DB_URL` | Secrets Manager | Postgres libpq DSN (required when `CIRQ_RAG_VECTOR_STORE_TYPE=pgvector`) |
| `CIRQ_RAG_REDIS_URL` | Secrets Manager | Redis URL (required when `CIRQ_RAG_RUN_HISTORY_BACKEND=redis`) |

Plus whichever Bedrock inference-profile ARN env vars your
`config/config.json` references (see `agents.*.model.inference_profile_arn`).

## Health endpoints

- `GET /health` - 200 OK as soon as the process is up. Used as the ALB target
  group health-check path.
- `GET /readiness` - probes Redis and (when pgvector is configured) runs
  `SELECT 1` against Postgres. Returns a 503 JSON envelope if any dependency
  is unreachable.

## Operational runbook

- **Deploy**: push new tag to ECR, `aws ecs update-service --force-new-deployment`.
- **Rotate API key**: update `cirq-agent/api-key` secret, `--force-new-deployment`.
- **Re-seed KB**: run `scripts/ingest_kb_to_pgvector.py` with the prod DSN
  exported. It is idempotent via `sha256(content)`.
- **Throttle from Bedrock**: clients see HTTP 503 with `Retry-After: 15`. Work
  around by requesting quota increases; do NOT add more replicas, they share
  the same Bedrock quota.
- **Log queries** (CloudWatch Logs Insights):

  ```text
  fields @timestamp, level, name, message
  | filter level in ["ERROR", "WARNING"]
  | sort @timestamp desc
  | limit 100
  ```

## What is intentionally NOT included

- Terraform / CDK / CloudFormation stacks (the task definition + policy JSONs
  are enough to get started; IaC belongs in a separate PR if wanted).
- Autoscaling policies (tune after you measure real traffic).
- WAF rules (recommended but deployment-specific).
- Multi-region failover (Bedrock quotas and model availability vary per
  region).
