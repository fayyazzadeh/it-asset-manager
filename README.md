# IT Asset Manager

A modular IT Asset Management, Discovery, Monitoring, and IT Operations platform.

## Stack

- Python / FastAPI
- PostgreSQL / SQLAlchemy 2.x / Alembic
- Redis / Celery
- Next.js / React / TypeScript
- Docker Compose

## Architecture

Consolidated Architecture v2 is documented under `docs/`.

## Development

Copy `.env.example` to `.env`, then run:

```bash
docker compose up --build
```

API health endpoint:

`GET /health`