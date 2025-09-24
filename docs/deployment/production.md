# Production Deployment Guide

## Overview

This guide covers production deployment of QCanvas with focus on security, performance, and reliability.

## Prerequisites

- **Server**: 8+ cores, 16GB+ RAM, 100GB+ storage
- **Domain**: SSL certificate for your domain
- **Monitoring**: Prometheus, Grafana, or similar
- **Backup**: Automated backup solution

## Quick Production Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure

```bash
git clone https://github.com/qcanvas/qcanvas.git
cd qcanvas

# Create production environment
cp environment.env .env.prod
nano .env.prod
```

### 3. Production Environment Variables

```bash
# Security
SECRET_KEY=your_very_secure_secret_key_here
DEBUG=false

# Database
POSTGRES_PASSWORD=secure_database_password
DATABASE_URL=postgresql://qcanvas:secure_database_password@postgres:5432/qcanvas_prod

# URLs
API_URL=https://api.yourdomain.com
WS_URL=wss://api.yourdomain.com/ws

# Monitoring
GRAFANA_PASSWORD=secure_grafana_password
```

### 4. SSL Certificate Setup

```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com
```

### 5. Deploy Production

```bash
# Start production services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## Security Configuration

### Firewall Setup

```bash
# Configure UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### SSL/TLS Configuration

```nginx
# nginx.prod.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
}
```

### Rate Limiting

```nginx
# Rate limiting configuration
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=ws:10m rate=100r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://backend;
}
```

## Performance Optimization

### Backend Optimization

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    environment:
      - WORKERS=4
      - MAX_CONNECTIONS=1000
```

### Database Optimization

```sql
-- PostgreSQL optimization
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### Caching Strategy

```python
# Redis caching configuration
CACHE_TTL = 3600  # 1 hour
CACHE_MAX_SIZE = 1000
CACHE_PREFIX = "qcanvas:"
```

## Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'qcanvas-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboards

Create dashboards for:
- API response times
- Error rates
- Resource usage
- Database performance
- WebSocket connections

### Alerting Rules

```yaml
# alerting.yml
groups:
  - name: qcanvas_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
```

## Backup Strategy

### Database Backup

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U qcanvas qcanvas_prod > backup_$DATE.sql
gzip backup_$DATE.sql
aws s3 cp backup_$DATE.sql.gz s3://your-backup-bucket/
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /path/to/backup.sh
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend services
docker-compose -f docker-compose.prod.yml up -d --scale backend=8

# Scale frontend services
docker-compose -f docker-compose.prod.yml up -d --scale frontend=4
```

### Load Balancer Configuration

```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
    server backend4:8000;
}
```

## Maintenance

### Health Checks

```bash
# Check service health
curl -f https://api.yourdomain.com/api/health

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Updates

```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Zero-downtime deployment
docker-compose -f docker-compose.prod.yml up -d --no-deps backend
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**: Increase memory limits or optimize code
2. **Database Connection Issues**: Check connection pool settings
3. **SSL Certificate Expiry**: Set up automatic renewal
4. **Performance Issues**: Monitor and optimize bottlenecks

### Debug Commands

```bash
# Check resource usage
docker stats

# View logs
docker-compose -f docker-compose.prod.yml logs backend

# Access container
docker-compose -f docker-compose.prod.yml exec backend bash
```

## Conclusion

This production deployment ensures QCanvas runs securely, efficiently, and reliably. Regular monitoring and maintenance are essential for optimal performance.
