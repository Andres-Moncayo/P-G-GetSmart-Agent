# Backend

FastAPI backend placeholder.

Quick start (local):

- Create a Python virtual environment: `python -m venv .venv`
- Activate and install dependencies: `pip install -r requirements.txt`
- Set `DATABASE_URL` to your Neon Postgres connection string (export or use `.env`).
- Run the app: `uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000`

Developer focus:

- `backend/app/main.py` — FastAPI app entrypoint
- `backend/app/api/routes.py` — API routes
- `backend/app/db/connection.py` — database connection layer
- `backend/app/core/config.py` — environment configuration
- `backend/app/models/` — domain model definitions
- `backend/app/services/` — business logic services
- `backend/app/tasks/` — background and pipeline tasks
- `backend/app/workers/` — worker orchestration

Related OpenSpec contracts:

- `openspec/specs/scraper/scraper_contract.yaml`
- `openspec/specs/scraper/master_json_schema.yaml`
- `openspec/specs/macro_skills/`
- `openspec/specs/synthesis/synthesis_skill.yaml`
