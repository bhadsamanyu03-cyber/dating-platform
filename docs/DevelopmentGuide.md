# Development Guide

Prerequisites: Docker Desktop and Docker Compose v2. Copy `.env.example` to `.env`, replace all development secrets, then run:

```sh
docker compose up --build
```

The API is proxied at `http://localhost:8080`. Use `/api/v1/health/live` for process health, `/api/v1/health/ready` to verify PostgreSQL and Redis, `/docs` for OpenAPI, and `/api/v1/metrics` for Prometheus scraping. Stop with `docker compose down`; add `-v` only when intentionally discarding local database and Redis data.

The backend container applies Alembic migrations before starting Uvicorn. To inspect the current revision, run `docker compose exec backend alembic current`.

The development email provider writes verification and reset tokens to backend JSON logs. Never use it outside local development.

For backend-only development, use Python 3.13, install `pip install -e '.[dev]'` in `apps/backend`, then run `pytest`, `ruff check .`, and `black --check .`.
