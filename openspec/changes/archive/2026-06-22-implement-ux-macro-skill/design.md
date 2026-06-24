## Context

Phase 3 of the GetSmart pipeline requires the 4 Macro-Skills to execute in parallel, each receiving a
mini_context slice of the Master-JSON and returning a structured intelligence dict to the Phase 4 Synthesizer.

The User Experience Macro-Skill is the first implementation. It uses Google Gemini 2.5 Flash with
`response_mime_type="application/json"` to force structured output, validated by Pydantic models.

## Goals / Non-Goals

**Goals:**
- Implement `UserExperienceSkill` following `ux_skill.yaml` exactly.
- Create `BaseMacroSkill` to centralize all shared logic (cache, retries, model call) so the other 3 skills only need to implement 3 methods: `system_prompt`, `build_user_prompt()`, `_fallback_output()`.
- Support both async execution (Celery + Redis) and sync execution (FastAPI direct) for development flexibility.
- Migrate from deprecated `google-generativeai` SDK to `google-genai>=2.0.0`.

**Non-Goals:**
- Do not implement Design & Art, Technology & Systems, or Strategy & Market skills in this change.
- Do not implement the Phase 4 Synthesizer.
- Do not modify scraper or ingestion contracts.

## Decisions

### `BaseMacroSkill` abstract class
All 4 skills share identical cache, retry, and model-call logic. Centralizing it in a base class ensures
a single change (e.g., adjusting exponential backoff) applies to all skills automatically.

### `asyncio.run()` bridge in Celery task
`analyze()` is async (uses `await` for Gemini). Celery workers are synchronous by default.
`asyncio.run()` creates a temporary event loop without requiring async worker configuration,
keeping the Celery setup simple.

### `app/services/macro_skills/` location
Skills belong in the `services/` layer (business logic), not in a standalone top-level `skills/` folder.
This aligns with the existing `services/__init__.py` and the project's layered architecture.

### Cache: fastapi-cache2 InMemoryBackend (not Redis)
Redis is the Celery broker/backend only. The skill result cache uses fastapi-cache2 in-memory,
which is sufficient for 24h TTL results and avoids coupling the cache layer to the task queue.

### Separate try/except for cache set
If `CacheManager.set()` fails (e.g., cache not initialized), the Gemini response should still be
returned. Separating the cache set from the model call prevents a cache failure from discarding a
valid LLM response.

## Risks / Trade-offs

- **In-memory cache resets on restart**: Acceptable for now. The Celery result in Redis still persists per job_id.
- **503 from Gemini under load**: Handled by `tenacity.AsyncRetrying` (3 attempts, exponential backoff).
- **`asyncio.run()` in Celery**: Creates a new event loop per task. If concurrency increases, consider `gevent` or `asyncio` Celery mode in the future.
