# Docker Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying QCanvas using Docker and Docker Compose. Docker provides a consistent, isolated environment for running QCanvas across different platforms and environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Development Deployment](#development-deployment)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

## Prerequisites

### Required Software

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository

### System Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB available space
- **Network**: Internet connection for pulling images

### Verify Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Verify Docker is running
docker info
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/qcanvas/qcanvas.git
cd qcanvas
```

### 2. Configure Environment

```bash
# Copy environment template (Docker Compose)
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Start Services

```bash
# Start lean stack (postgres + redis + backend)
docker compose up -d --build

# Check service status
docker compose ps
```

### 4. Access QCanvas

- **Backend API (FastAPI)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

If you are running the frontend locally, configure it with:\n+`NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000`

Optional services:\n+- **SonarQube** (profile `metrics`): http://localhost:9000

### 5. Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

### SonarQube (optional profile)

Run SonarQube only when you need it:

```bash
docker compose --profile metrics up -d
```

## Development Deployment

## Verification (backend-in-Docker, frontend-local workflow)

After `docker compose up -d --build`:

```bash
# API root
curl http://localhost:8000/

# Health (compat)
curl http://localhost:8000/health

# Health (router)
curl http://localhost:8000/api/health/
```

If you want to validate that the backend can reach Postgres/Redis, the simplest check is to hit an endpoint that persists or reads data (e.g. auth/projects/files). If you don’t have a known DB-touching endpoint handy, you can at least confirm the containers are healthy:

```bash
docker compose ps
docker compose logs -f backend
```

### Development Configuration

The development deployment includes all services with hot-reload capabilities:

```yaml
# docker-compose.yml (development)
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: qcanvas_dev
      POSTGRES_USER: qcanvas
      POSTGRES_PASSWORD: qcanvas_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U qcanvas"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build:
      context: .
      dockerfile: config/docker/Dockerfile.backend
      target: development
    environment:
      - DATABASE_URL=postgresql://qcanvas:qcanvas_pass@postgres:5432/qcanvas_dev
      - REDIS_URL=redis://redis:6379
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    volumes:
      - ./backend:/app/backend
      - ./quantum_converters:/app/quantum_converters
      - ./quantum_simulator:/app/quantum_simulator
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: ../config/docker/Dockerfile.frontend
      target: development
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    depends_on:
      - backend
    command: npm run dev

  nginx:
    image: nginx:alpine
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - frontend
      - backend

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus

volumes:
  postgres_data:
  grafana_data:
```

### Development Commands

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build

# Access service shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Run tests
docker-compose exec backend pytest
docker-compose exec frontend npm test

# Run database migrations
docker-compose exec backend alembic upgrade head
```

## Production Deployment

### Production Configuration

The production deployment is optimized for performance and security:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: qcanvas_prod
      POSTGRES_USER: qcanvas
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U qcanvas"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: config/docker/Dockerfile.backend
      target: production
    environment:
      - DATABASE_URL=postgresql://qcanvas:${POSTGRES_PASSWORD}@postgres:5432/qcanvas_prod
      - REDIS_URL=redis://redis:6379
      - DEBUG=false
      - LOG_LEVEL=INFO
      - SECRET_KEY=${SECRET_KEY}
      - WORKERS=4
    volumes:
      - backend_logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  frontend:
    build:
      context: ./frontend
      dockerfile: ../config/docker/Dockerfile.frontend
      target: production
    environment:
      - NEXT_PUBLIC_API_URL=${API_URL}
      - NEXT_PUBLIC_WS_URL=${WS_URL}
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    volumes:
      - ./config/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./config/ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  backend_logs:
  prometheus_data:
  grafana_data:
```

### Production Environment Variables

Create a `.env.prod` file for production:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password_here

# Security
SECRET_KEY=your_secret_key_here

# URLs
API_URL=https://api.qcanvas.com
WS_URL=wss://api.qcanvas.com/ws

# Grafana
GRAFANA_PASSWORD=your_grafana_password_here

# Monitoring
PROMETHEUS_RETENTION_DAYS=30
```

### Production Deployment Commands

```bash
# Deploy production environment
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Scale backend services
docker-compose -f docker-compose.prod.yml up -d --scale backend=5

# Update services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Backup database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U qcanvas qcanvas_prod > backup.sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U qcanvas qcanvas_prod < backup.sql
```

## Configuration

### Environment Variables

#### Backend Configuration

```bash
# Application
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_here
WORKERS=4

# Database
DATABASE_URL=postgresql://user:password@host:port/database
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://host:port/database
REDIS_POOL_SIZE=10

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://qcanvas.com"]
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# Quantum Simulation
MAX_QUBITS=32
MAX_SHOTS=10000
DEFAULT_BACKEND=statevector

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=["py", "qasm", "txt"]

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

#### Frontend Configuration

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_DEBUG_MODE=false

# External Services
NEXT_PUBLIC_SENTRY_DSN=
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=
```

### Nginx Configuration

#### Development Nginx

```nginx
# config/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name localhost;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### Production Nginx

```nginx
# config/nginx.prod.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=ws:10m rate=100r/s;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    server {
        listen 80;
        server_name qcanvas.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name qcanvas.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API with rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket with rate limiting
        location /ws {
            limit_req zone=ws burst=50 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Prometheus Configuration

```yaml
# config/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'qcanvas-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'qcanvas-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

## Monitoring

### Health Checks

All services include health checks:

```bash
# Check service health
docker-compose ps

# Check specific service health
docker-compose exec backend curl -f http://localhost:8000/api/health

# View health check logs
docker-compose logs backend | grep health
```

### Logging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View logs with timestamps
docker-compose logs -f -t backend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Metrics

Access metrics endpoints:

- **Backend Metrics**: http://localhost:8000/metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001

### Performance Monitoring

```bash
# Monitor resource usage
docker stats

# Monitor specific container
docker stats backend

# Check disk usage
docker system df

# Clean up unused resources
docker system prune
```

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check service logs
docker-compose logs service_name

# Check service status
docker-compose ps

# Restart service
docker-compose restart service_name

# Rebuild service
docker-compose up -d --build service_name
```

#### Database Connection Issues

```bash
# Check database status
docker-compose exec postgres pg_isready -U qcanvas

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### Port Conflicts

```bash
# Check port usage
netstat -tulpn | grep :8000

# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead of 8000
```

#### Memory Issues

```bash
# Check memory usage
docker stats

# Increase memory limits
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 8G
```

### Debug Commands

```bash
# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Check environment variables
docker-compose exec backend env

# Check network connectivity
docker-compose exec backend ping postgres

# Check file permissions
docker-compose exec backend ls -la /app

# View running processes
docker-compose exec backend ps aux
```

### Log Analysis

```bash
# Search for errors
docker-compose logs backend | grep -i error

# Search for specific patterns
docker-compose logs backend | grep "conversion"

# Export logs to file
docker-compose logs backend > backend.log

# Follow logs in real-time
docker-compose logs -f backend | grep -E "(ERROR|WARN)"
```

## Advanced Configuration

### Custom Docker Images

#### Backend Dockerfile

```dockerfile
# config/docker/Dockerfile.backend
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Development stage
FROM python:3.11-slim as development

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r qcanvas && useradd -r -g qcanvas qcanvas

# Set working directory
WORKDIR /app

# Copy application code
COPY backend/ ./backend/
COPY quantum_converters/ ./quantum_converters/
COPY quantum_simulator/ ./quantum_simulator/

# Switch to non-root user
USER qcanvas

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/simple || exit 1

# Development command
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python:3.11-slim as production

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r qcanvas && useradd -r -g qcanvas qcanvas

# Set working directory
WORKDIR /app

# Copy application code
COPY backend/ ./backend/
COPY quantum_converters/ ./quantum_converters/
COPY quantum_simulator/ ./quantum_simulator/

# Create logs directory
RUN mkdir -p /app/logs && chown -R qcanvas:qcanvas /app

# Switch to non-root user
USER qcanvas

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/simple || exit 1

# Production command
CMD ["gunicorn", "backend.app.main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
```

#### Frontend Dockerfile

```dockerfile
# config/docker/Dockerfile.frontend
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Development stage
FROM node:18-alpine as development

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies)
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Development command
CMD ["npm", "start"]

# Production stage
FROM nginx:alpine as production

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1
```

### Multi-Stage Builds

```yaml
# docker-compose.build.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: config/docker/Dockerfile.backend
      target: production
      args:
        BUILDKIT_INLINE_CACHE: 1
    image: qcanvas/backend:latest

  frontend:
    build:
      context: ./frontend
      dockerfile: ../config/docker/Dockerfile.frontend
      target: production
      args:
        BUILDKIT_INLINE_CACHE: 1
    image: qcanvas/frontend:latest
```

### Docker Swarm Deployment

```yaml
# docker-stack.yml
version: '3.8'

services:
  backend:
    image: qcanvas/backend:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    environment:
      - DATABASE_URL=postgresql://qcanvas:password@postgres:5432/qcanvas
      - REDIS_URL=redis://redis:6379
    networks:
      - qcanvas-network

  frontend:
    image: qcanvas/frontend:latest
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 2G
    networks:
      - qcanvas-network

  postgres:
    image: postgres:15
    deploy:
      placement:
        constraints:
          - node.role == manager
    environment:
      POSTGRES_DB: qcanvas
      POSTGRES_USER: qcanvas
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - qcanvas-network

  redis:
    image: redis:7-alpine
    deploy:
      placement:
        constraints:
          - node.role == manager
    networks:
      - qcanvas-network

networks:
  qcanvas-network:
    driver: overlay

volumes:
  postgres_data:
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qcanvas-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qcanvas-backend
  template:
    metadata:
      labels:
        app: qcanvas-backend
    spec:
      containers:
      - name: qcanvas-backend
        image: qcanvas/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: qcanvas-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: qcanvas-secrets
              key: redis-url
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
          requests:
            cpu: "1"
            memory: "2Gi"
        livenessProbe:
          httpGet:
            path: /api/health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: qcanvas-backend-service
spec:
  selector:
    app: qcanvas-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Conclusion

This Docker deployment guide provides comprehensive instructions for deploying QCanvas in various environments. The configuration is designed to be flexible and scalable, allowing you to adapt it to your specific needs.

For production deployments, remember to:

- Use strong passwords and secrets
- Enable SSL/TLS encryption
- Configure proper monitoring and alerting
- Set up regular backups
- Implement proper logging and log rotation
- Use resource limits and health checks
- Follow security best practices

For additional help or questions, please refer to the troubleshooting section or reach out to the QCanvas community.
