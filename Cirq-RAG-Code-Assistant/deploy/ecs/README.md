# Deploying Cirq-RAG-Code-Assistant on ECS Fargate

This directory ships the minimum viable deployment artefacts for the Cirq
RAG service on AWS ECS Fargate. Everything here is a template: placeholders
are wrapped in angle brackets (e.g. `<REGION>`, `<ACCOUNT_ID>`, `<TAG>`).

Files:

- [`cirq-agent.taskdef.json`](cirq-agent.taskdef.json) - Fargate task
  definition (1 container, port 8000, secrets pulled from Secrets Manager,
  logs to CloudWatch).
- [`task-role-policy.json`](task-role-policy.json) - IAM policy for the
  *task role* (Bedrock InvokeModel, read-only).
- [`execution-role-policy.json`](execution-role-policy.json) - IAM policy
  for the *execution role* (ECR pull, CloudWatch logs, Secrets Manager).

## Prerequisites

1. A VPC with at least two private subnets (one per AZ) and NAT egress.
2. An RDS Postgres 15.5+ or Aurora Postgres instance in the same VPC with
   the `vector` extension enabled (run `scripts/sql/001_init_pgvector.sql`
   once against the target database).
3. ElastiCache Redis or a self-hosted Redis reachable from the task subnets.
4. Bedrock model access granted in the target region for every model used
   in `config/config.json` (Claude Sonnet / Opus / Haiku, Nova embeddings).
5. Secrets Manager entries for everything listed in the task definition's
   `secrets` block.

> Do NOT put this service behind API Gateway. API Gateway has a 29s hard
> timeout; the Cirq pipeline routinely takes 15-60s.

## One-time setup

### 1. Create the ECR repository and push the image

```bash
AWS_REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws ecr create-repository --repository-name cirq-agent --region "$AWS_REGION"

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Build the slim production image.
docker build -t cirq-agent:latest -f Cirq-RAG-Code-Assistant/Dockerfile Cirq-RAG-Code-Assistant

# Tag and push.
docker tag cirq-agent:latest "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/cirq-agent:latest"
docker push "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/cirq-agent:latest"
```

### 2. Create IAM roles

```bash
# Trust policy used by both roles.
cat > /tmp/ecs-trust.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "ecs-tasks.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
JSON

# Execution role (pulls ECR image, writes CW logs, reads Secrets Manager).
aws iam create-role \
  --role-name cirq-agent-task-execution-role \
  --assume-role-policy-document file:///tmp/ecs-trust.json

aws iam put-role-policy \
  --role-name cirq-agent-task-execution-role \
  --policy-name cirq-agent-exec \
  --policy-document file://Cirq-RAG-Code-Assistant/deploy/ecs/execution-role-policy.json

# Task role (what the running container can do: Bedrock).
aws iam create-role \
  --role-name cirq-agent-task-role \
  --assume-role-policy-document file:///tmp/ecs-trust.json

aws iam put-role-policy \
  --role-name cirq-agent-task-role \
  --policy-name cirq-agent-task \
  --policy-document file://Cirq-RAG-Code-Assistant/deploy/ecs/task-role-policy.json
```

### 3. Populate Secrets Manager

```bash
aws secretsmanager create-secret --name cirq-agent/api-key     --secret-string "$(openssl rand -hex 32)"
aws secretsmanager create-secret --name cirq-agent/db-url      --secret-string "postgresql://USER:PASS@<rds-endpoint>:5432/<db>"
aws secretsmanager create-secret --name cirq-agent/redis-url   --secret-string "redis://<elasticache-endpoint>:6379/1"

aws secretsmanager create-secret --name cirq-agent/bedrock-designer    --secret-string "arn:aws:bedrock:$AWS_REGION:$ACCOUNT_ID:inference-profile/..."
aws secretsmanager create-secret --name cirq-agent/bedrock-optimizer   --secret-string "arn:aws:bedrock:$AWS_REGION:$ACCOUNT_ID:inference-profile/..."
aws secretsmanager create-secret --name cirq-agent/bedrock-validator   --secret-string "arn:aws:bedrock:$AWS_REGION:$ACCOUNT_ID:inference-profile/..."
aws secretsmanager create-secret --name cirq-agent/bedrock-educational --secret-string "arn:aws:bedrock:$AWS_REGION:$ACCOUNT_ID:inference-profile/..."
```

### 4. Apply the pgvector schema (one-shot Fargate task or bastion)

```bash
psql "$(aws secretsmanager get-secret-value --secret-id cirq-agent/db-url --query SecretString --output text)" \
  -f Cirq-RAG-Code-Assistant/scripts/sql/001_init_pgvector.sql
```

### 5. Seed the knowledge base

Run the ingestion script once - either locally with the RDS DSN exported, or
as a one-off Fargate task using the same image.

```bash
export CIRQ_RAG_DB_URL=$(aws secretsmanager get-secret-value --secret-id cirq-agent/db-url --query SecretString --output text)
python Cirq-RAG-Code-Assistant/scripts/ingest_kb_to_pgvector.py
```

The script is idempotent (sha256 content hashing) so it is safe to re-run.

### 6. Register the task definition and create the service

Edit `cirq-agent.taskdef.json` to substitute `<ACCOUNT_ID>`, `<REGION>`,
`<TAG>`, and the Secrets Manager ARNs, then:

```bash
aws ecs register-task-definition \
  --cli-input-json file://Cirq-RAG-Code-Assistant/deploy/ecs/cirq-agent.taskdef.json

aws ecs create-cluster --cluster-name cirq-agent

aws ecs create-service \
  --cluster cirq-agent \
  --service-name cirq-agent \
  --task-definition cirq-agent \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=cirq-agent,containerPort=8000" \
  --health-check-grace-period-seconds 180
```

### 7. ALB configuration

- Target group: HTTP, port 8000, health check path `/health`, healthy
  threshold 2, interval 30s, timeout 5s.
- **Important**: raise ALB *idle timeout* to at least 180s
  (`aws elbv2 modify-load-balancer-attributes`), because the pipeline
  frequently takes 15-60s per request.
- Listener: HTTPS 443 -> target group.
- WAF rules (recommended but out of scope): rate limiting + IP allowlist
  restricted to the QCanvas backend's public egress.

## Day-2 operations

- **Deploy a new image**: push the new tag, `aws ecs update-service
  --force-new-deployment`.
- **Re-seed the knowledge base**: re-run the ingestion script; the
  idempotency layer skips unchanged rows.
- **Rotate the API key**: update the Secrets Manager secret, then
  `aws ecs update-service --force-new-deployment` to pick up the new value.
- **Inspect logs**: CloudWatch log group `/ecs/cirq-agent`. The log lines
  are JSON (`CIRQ_RAG_LOG_FORMAT=json`) so CloudWatch Logs Insights queries
  like `fields @timestamp, level, message | filter level = "ERROR"` work.
