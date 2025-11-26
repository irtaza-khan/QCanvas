# QCanvas Deployment Documentation

This directory contains comprehensive deployment diagrams and documentation for the QCanvas quantum computing platform.

## 📊 Deployment Diagrams

### 1. Complete Deployment Architecture
- **File**: `deployment-diagram.md`
- **Description**: Comprehensive deployment diagram with detailed documentation
- **Includes**: All system components, network configurations, security layers, monitoring, CI/CD pipeline, and scaling strategies

### 2. Visual Mermaid Diagrams
- **File**: `qcanvas-deployment-diagram.mmd`
- **Description**: Full detailed Mermaid diagram with all components
- **Use**: Copy content to Mermaid Live Editor or compatible tools

- **File**: `qcanvas-core-deployment.mmd`
- **Description**: Simplified core deployment diagram
- **Use**: Easier to read and understand the main architecture

## 🏗️ Architecture Overview

QCanvas uses a hybrid architecture combining:
- **Frontend**: Next.js with SSR/SSG capabilities
- **Backend**: FastAPI for complex quantum operations
- **Quantum Processing**: Multi-framework converters and simulators
- **Data Layer**: PostgreSQL with Redis caching
- **Monitoring**: Prometheus + Grafana observability stack
- **Security**: JWT authentication, rate limiting, WAF
- **Orchestration**: Docker Swarm/Kubernetes container management

## 🚀 Deployment Environments

### Development
- Single instance deployment
- Hot reloading enabled
- Local database and cache
- Basic monitoring

### Staging
- 2+ instances with load balancing
- Database replication
- Full monitoring stack
- Security hardening

### Production
- 3+ instances with auto-scaling
- High availability database
- Complete observability
- Enterprise security

## 📋 Key Components

### Frontend Layer
- **Next.js Instances**: 3+ instances for high availability
- **SSR/SSG**: Server-side rendering and static generation
- **API Routes**: Simple backend operations
- **WebSocket**: Real-time communication

### Backend Layer
- **FastAPI Instances**: 3+ instances with load balancing
- **WebSocket Manager**: Real-time updates
- **REST API**: Circuit conversion and simulation endpoints

### Quantum Processing
- **Converters**: Cirq, Qiskit, PennyLane support
- **Simulators**: Statevector, Density Matrix, Stabilizer backends
- **OpenQASM 3.0**: Standardized intermediate representation

### Data Layer
- **PostgreSQL**: Master-slave replication
- **Redis Cluster**: Caching and session management
- **File Storage**: Circuit files and assets

### Monitoring & Security
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **AlertManager**: Alerting and notifications
- **JWT Auth**: Authentication and authorization
- **Rate Limiting**: DDoS protection

## 🔧 Configuration

### Port Configuration
| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| Frontend | 3000 | HTTP | Next.js application |
| Backend API | 8000 | HTTP | FastAPI REST API |
| WebSocket | 8000 | WS | WebSocket connections |
| PostgreSQL | 5432 | TCP | Database server |
| Redis | 6379 | TCP | Cache server |
| Prometheus | 9090 | HTTP | Metrics collection |
| Grafana | 3001 | HTTP | Monitoring dashboard |
| Nginx | 80/443 | HTTP/HTTPS | Load balancer |

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `DEBUG`: Debug mode flag
- `NEXT_PUBLIC_API_URL`: Frontend API endpoint

## 📈 Scaling Strategy

### Horizontal Scaling
- **Frontend**: Scale based on CPU/memory usage
- **Backend**: Scale based on request queue length
- **Database**: Add read replicas for read-heavy workloads
- **Cache**: Scale Redis cluster nodes

### Vertical Scaling
- **CPU**: Increase cores for quantum simulation
- **Memory**: Increase RAM for large circuits
- **Storage**: Increase disk space for data

## 🔒 Security Considerations

### Network Security
- SSL/TLS termination at load balancer
- Internal network segmentation
- Database network isolation
- WebSocket connection encryption

### Application Security
- JWT-based authentication
- Role-based access control
- Input validation and sanitization
- Rate limiting and DDoS protection

### Data Security
- Database encryption at rest
- Redis data encryption
- Secure file storage
- Regular security audits

## 📊 Monitoring & Alerting

### Key Metrics
- **Performance**: Response time, throughput, error rate
- **Resources**: CPU, memory, disk, network usage
- **Business**: Conversion count, simulation count, user activity
- **Security**: Failed login attempts, suspicious activity

### Alerting Rules
- High error rate (>5%)
- High response time (>2s)
- Resource usage >80%
- Database connection failures
- Service unavailability

## 💾 Backup & Recovery

### Database Backups
- Automated daily backups
- Point-in-time recovery
- Cross-region replication
- Regular restore testing

### Application Backups
- Container image backups
- Configuration backups
- Circuit file backups
- Disaster recovery procedures

## 💰 Cost Optimization

### Resource Optimization
- Right-sizing instances
- Auto-scaling policies
- Reserved instances for predictable workloads
- Spot instances for batch processing

### Storage Optimization
- Data lifecycle policies
- Compression and deduplication
- CDN for static assets
- Efficient caching strategies

## 🛠️ Deployment Commands

### Development (Docker)
```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Local Linux Development (Helper Scripts)

For a non‑Docker local Linux setup, QCanvas includes helper scripts in the repository root:

- `setup.sh` – **one-time** installation script
  - Installs core system packages via `apt` (Node.js, npm, Python venv tooling, build tools)
  - Creates and activates a Python virtual environment
  - Installs backend requirements from `requirements.txt`
  - Installs frontend dependencies in `frontend/`

- `run.sh` – service manager for local development
  - `./run.sh start`: builds and starts the Next.js frontend and FastAPI backend in the background
    - Writes logs to `logs/frontend.log` and `logs/backend.log`
    - Tracks processes via `frontend.pid` and `backend.pid`
  - `./run.sh stop`: stops all QCanvas services (kills node/next/uvicorn) and clears PID files

> These scripts are intended for Linux environments with `bash`, `sudo`, and `apt`. On Windows or other platforms, use Docker or the manual commands in the main README.

### Production
```bash
# Deploy production environment
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=5

# Update services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Additional Resources

- [Docker Deployment Guide](docker.md)
- [Production Deployment Guide](production.md)
- [API Documentation](../api/)
- [Architecture Documentation](../developer/architecture.md)

---

*For questions or support regarding deployment, please refer to the troubleshooting section or contact the development team.*
