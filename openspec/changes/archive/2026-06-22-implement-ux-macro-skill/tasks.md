## 1. Dependencies and configuration

- [x] 1.1 Add `google-genai>=2.0.0`, `jinja2>=3.1.0`, `tenacity>=8.2.0`, `redis>=5.0.0`, `celery[redis]` to `requirements.txt`.
- [x] 1.2 Add `GEMINI_API_KEY` and `REDIS_URL` to `config.py`. Use `find_dotenv()` for automatic `.env` loading.

## 2. BaseMacroSkill

- [x] 2.1 Create `backend/app/services/macro_skills/base_skill.py` with abstract base class.
- [x] 2.2 Implement `genai.Client` + `types.GenerateContentConfig` with `response_mime_type="application/json"`.
- [x] 2.3 Implement `_call_model()` with `AsyncRetrying` (3 attempts, exponential backoff 1s → 2s → 4s).
- [x] 2.4 Implement `analyze()` with cache check → model call → cache set → return. Separate try/except blocks.
- [x] 2.5 Implement `_cache_key()` and `_input_hash()` helpers.

## 3. User Experience Skill

- [x] 3.1 Create `backend/app/services/macro_skills/user_experience/schemas.py` with `UXMiniContext` and `UXAnalysisOutput` Pydantic models.
- [x] 3.2 Create `backend/app/services/macro_skills/user_experience/skill.py` implementing `UserExperienceSkill`.
- [x] 3.3 Implement `system_prompt` with full analyst persona and JSON output schema with enums.
- [x] 3.4 Implement `build_user_prompt()` formatting hard_data + semantic_data + Steam reviews as structured text.
- [x] 3.5 Implement `_fallback_output()` returning minimal valid structure with `error: true` on all categories.

## 4. Celery integration

- [x] 4.1 Create `backend/app/celery_app.py` with Redis broker/backend and `task_acks_late=True`.
- [x] 4.2 Create `backend/app/tasks/skill_tasks.py` with `run_ux_skill` Celery task using `asyncio.run()` bridge.

## 5. FastAPI endpoints

- [x] 5.1 Create `backend/app/api/skills_routes.py` with `POST /skills/user-experience` (async Celery dispatch).
- [x] 5.2 Add `GET /skills/jobs/{job_id}` generic polling endpoint.
- [x] 5.3 Add `POST /skills/user-experience/sync` for local development without Redis.
- [x] 5.4 Register `skills_router` in `main.py` and initialize `CacheManager` on startup.

## 6. Reorganization

- [x] 6.1 Move skill code from `app/skills/` to `app/services/macro_skills/`.
- [x] 6.2 Update all import paths: `..skills.*` → `..services.macro_skills.*` in `skill_tasks.py` and `skills_routes.py`.
- [x] 6.3 Update `base_skill.py` imports: `..core.config` → `...core.config` (3 dots, deeper nesting).
- [x] 6.4 Delete old `app/skills/` folder.

## 7. Bug fixes

- [x] 7.1 Fix `fastapi_cache.backends.memory` → `fastapi_cache.backends.inmemory`.
- [x] 7.2 Fix `backend.set(expire=timedelta(...))` → `backend.set(expire=int)`.
- [x] 7.3 Migrate from deprecated `google-generativeai` to `google-genai>=2.0.0`.

## 8. Validation

- [x] 8.1 `GET /api/health` → `{ "status": "ok" }`.
- [x] 8.2 `GET /docs` → Swagger UI loads "GetSmart API v3.0.0".
- [x] 8.3 `POST /api/skills/user-experience/sync` → Full Gemini analysis returned for Elden Ring test payload.
