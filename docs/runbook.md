# Local development

Install Python 3.12+, uv, and Docker with Docker Compose.

The local `.env` contains database settings and is ignored by Git. For a new
checkout, copy `.env.example` to `.env` and replace the example password.
The Compose database uses these settings on its first initialization; changing
the password in `.env` later does not change the existing database password.

```bash
uv sync --locked
docker compose up -d --wait database
uv run fastapi dev creator/main.py
```

Open http://127.0.0.1:8000. `/health` checks the web process; `/ready` checks
PostgreSQL with a three-second timeout.

Run the readiness smoke check with the database running:

```bash
uv run python scripts/check_readiness.py
```

Stop the database without deleting its stored data:

```bash
docker compose stop database
```

Database storage lives in the Compose named volume. PostgreSQL is exposed only
on localhost. This setup is for local development; migrations, database sessions,
and production deployment are still outstanding.
