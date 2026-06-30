# Scraper Architecture (Phase 1)

This module implements the `scraper` pipeline using **Domain-Driven Design (DDD)** inside `src/scraper/` with these layers:

- `domain/`: business rules and models (e.g. `MasterContext` in Pydantic).
- `application/`: orchestrators connecting infrastructure with domain (`orchestrator.py`).
- `infrastructure/`: external adapters (APIs, LLM clients, DB).
- `presentation/`: API routes exposing functionality.

## Why DDD here?
- Clear separation between data gathering and LLM logic.
- Lower complexity for initial deployment (single-node).
- Excellent fit for I/O-bound tasks (HTTP calls to external APIs).
- Native integration with FastAPI for background tasks.

Accepted trade-off: no distributed queue; state lives in the process memory.

## The Pipeline Step-by-Step

### Phase 0: Disambiguation (Trigger)
Input: `POST /scrape` with `confirmed_game` payload.
- Connects to IGDB/RAWG/Steam to find the exact game ID and basic metadata.

### Phase 1: Data Scraping (Parallel)
1. A background task is queued using `BackgroundTasks`.
2. The orchestrator runs 4 scrapers in parallel via `asyncio.gather()`:
   - `Design & Art Scraper`
   - `User Experience Scraper`
   - `Technology & Systems Scraper`
   - `Strategy & Market Scraper`

Each scraper extracts **Hard Data** (APIs) and **Semantic Data** (Web Search/News).
**Important**: no LLM is used in this phase.

### Phase 2: Parallel Analysis (LLM)
Once Phase 1 completes successfully:
1. 4 asynchronous AI workers run in parallel (`asyncio.gather()`).
2. Each worker calls Gemini `gemini-2.5-flash` with a strict prompt.
3. The response is strictly requested in structured JSON.

If an AI worker fails (timeout/error), a fallback generates a valid JSON with an "error" flag and minimal data so the pipeline doesn't break.

### Phase 3: Assembly (Master-JSON)
With the 4 JSON responses collected:
1. They are assembled into a `MasterContext` object (Pydantic).
2. Saved to PostgreSQL for vector indexing (future) or cache.

Output: Final `Master-JSON` ready for synthesis.

### Phase 4: Synthesis
1. The `MasterContext` is passed to the final `gemini-1.5-flash` model.
2. A professional Markdown output is requested.
3. The final markdown is returned for persistence/delivery.

Output: final report in Markdown.
