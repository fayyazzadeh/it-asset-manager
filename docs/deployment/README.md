# Deployment

Initial target:
- Debian 13 or Ubuntu Server LTS
- 8 vCPU
- 24 GB RAM
- 500 GB SSD

Compose services:
- PostgreSQL
- Redis
- FastAPI
- Celery worker
- Next.js
- Nginx

Production secrets must be supplied through environment configuration and must not be committed.