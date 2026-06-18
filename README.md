# GetSmart

Deterministic Parallel Analysis Pipeline for game intelligence reports.

Quick start (local development):

- Ensure you have a PostgreSQL instance (Neon) and populate `DATABASE_URL` in a `.env` file or environment.
- Backend: see `backend/requirements.txt` and run with Uvicorn.
- Frontend: use Vite (see `frontend/package.json`).

Specs and contracts live in `openspec/`.

Onboarding flow for developers:
1. Read this root README and the OpenSpec configuration in `openspec/config.yaml`.
2. Do not run `openspec init` unless you are the contract owner or explicitly redesigning the OpenSpec structure.
3. Validate the spec files before working on implementation:
   ```powershell
   npx @fission-ai/openspec@latest validate openspec/
   ```
4. Backend developers should focus on:
   - `backend/app/main.py` — FastAPI app entrypoint
   - `backend/app/api/routes.py` — API routes
   - `backend/app/db/connection.py` — database connection
   - `backend/app/core/config.py` — environment configuration
   - OpenSpec contracts in:
     - `openspec/specs/scraper/`
     - `openspec/specs/macro_skills/`
     - `openspec/specs/synthesis/`
5. Frontend developers should focus on:
   - `frontend/src/index.tsx` — app entrypoint
   - `frontend/src/modules/auth/login/index.tsx` — login module
   - `frontend/src/modules/dashboard/index.tsx` — dashboard module
   - `frontend/src/modules/reports/index.tsx` — reports module
   - `frontend/src/modules/pipeline/index.tsx` — pipeline control module
   - OpenSpec UI contract in:
     - `openspec/specs/ui_and_login/ui_login_contract.md`
6. After implementation, rerun validation and update the OpenSpec docs only if the contract itself changes.
