# Deployment Guide

## Docker Compose

```bash
docker-compose up -d
```

## Kubernetes

```bash
helm install schema-platform ./helm
```

## Configuration

Environment variables:
- DATABASE_URL
- REDIS_URL
- SECRET_KEY
