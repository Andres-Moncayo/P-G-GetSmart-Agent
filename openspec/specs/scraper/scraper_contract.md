# Scraper & Ingestion — Functional Specification

> **Artifact:** `scraper_contract.yaml`
> **Repository path:** `openspec/specs/scraper/scraper_contract.yaml`
> **Usage:** Backend ingestion via FastAPI async service
> **Phase:** Phase 1 (Ingestion)
> **Status:** Draft
> **Last Updated:** 2026-06-24

---

## 1. Overview

The Ingestion phase is the **data extraction engine** of the GetSmart pipeline. Its purpose is to collect all relevant information about a confirmed game — both structured (APIs) and unstructured (web search) — and package it into a format that the 4 Macro-Skills can consume efficiently.

The scraper runs as a **single FastAPI service (`ScraperService`)** containing 4 internal async scrapers, one per Macro-Skill. Each scraper operates as an independent **async function** executed in parallel via `asyncio.gather()`, producing a **Mini-Context JSON** that is available immediately to its corresponding Macro-Skill in Phase 3. The Mini-Contexts are also later consolidated into Master-JSON for storage and cross-skill indexing.

**No LLM is used in this phase.** All extraction is deterministic: API calls + Tavily searches with predefined queries.

**Infrastructure:** FastAPI + async/await + BackgroundTasks. No Celery. No Redis. In-memory cache only.

---

## 2. Flow Diagram

```mermaid
flowchart TD
    A[confirmed_game input] --> B[FastAPI POST /scrape]
    B --> C{BackgroundTasks}
    C --> D[asyncio.gather 4 scrapers]
    D --> E[Scraper 1: Design & Art]
    D --> F[Scraper 2: User Experience]
    D --> G[Scraper 3: Technology & Systems]
    D --> H[Scraper 4: Strategy & Market]
    E --> I[context_design_art.json]
    F --> J[context_user_experience.json]
    G --> K[context_technology_systems.json]
    H --> L[context_strategy_market.json]
    I --> M[Consolidate Master-JSON]
    J --> M
    K --> M
    L --> M
    M --> N[master_context.json]
    N --> O[POST /webhook to Phase 3]

Note: Each Mini-Context file is produced independently and can be consumed by
its corresponding Macro-Skill as soon as it is available. The final Master-JSON
is consolidated afterward to create the canonical cross-skill artifact used for
storage, partition index, and synthesis.
```

---

## 3. Input Contract

The scraper receives a `confirmed_game` object produced by Phase 0 (Disambiguation):

```json
{
  "game_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Elden Ring",
  "release_year": 2022,
  "igdb_id": 119133,
  "rawg_id": 326243,
  "steam_app_id": 1245620,
  "aliases": ["ELDEN RING"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `game_id` | UUID | Yes | Internal game UUID in GetSmart |
| `name` | string | Yes | Exact confirmed game title |
| `release_year` | integer | Yes | Confirmed release year |
| `igdb_id` | integer | Yes | IGDB API game ID |
| `rawg_id` | integer | Yes | RAWG API game ID |
| `steam_app_id` | integer | No | Steam App ID if available |
| `aliases` | array<string> | No | Alternative game names for search queries |

### 3.1 Steam App ID Null Handling

When `steam_app_id` is `null`, scrapers that depend on Steam APIs must skip Steam-specific data sources gracefully:

| Scraper | Steam Source Skipped | Impact |
|---------|---------------------|--------|
| **Design & Art** | Steam Web API (achievements) | Low — IGDB/RAWG cover most design data |
| **User Experience** | Steam Storefront + Steam Reviews | Medium — lose platform-specific UX data |
| **Technology & Systems** | Steam Storefront + Steam Web API | Medium — lose system requirements and live player count |
| **Strategy & Market** | Steam Storefront + Steam Web + SteamSpy | **High** — lose pricing, sales estimates, and Steam market data |

**Fallback:** When Steam data is unavailable, rely on IGDB + RAWG + Tavily semantic data to compensate. Reduce `confidence_score` by **0.15**.

---

## 4. Step 1: Fetch Hard Data

Before dispatching scrapers, the system queries direct APIs in parallel to build a `game_metadata.json` with all structured data.

### 4.1 APIs Queried

| Source | Endpoint | Auth | Timeout | Data Extracted |
|--------|----------|------|---------|----------------|
| **IGDB** | `POST /v4/games` | OAuth2 (Twitch) | 5s | genres, themes, modes, engines, companies, platforms, languages, storyline, summary, cover, screenshots, videos, artworks, ratings |
| **RAWG** | `GET /api/games/{id}` | API Key | 5s | description, metacritic, ESRB, ratings distribution, added counts |
| **Steam Storefront** | `GET /appdetails` | None | 5s | prices, requirements, languages, controller support, categories, DLC |
| **Steam Web** | `GET /GetSchemaForGame` | API Key | 5s | achievements schema |
| **Steam Web** | `GET /GetNumberOfCurrentPlayers` | API Key | 5s | **current players only** (NOT peak) |
| **SteamSpy** | `GET /api.php` | None | 5s | sales estimates, tags, CCU, playtime |

### 4.2 Parallel API Calls via asyncio.gather()

```
┌─────────────────┐
│  confirmed_game │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┬────────┬────────┐
    ▼         ▼        ▼        ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  IGDB  │ │  RAWG  │ │ Steam  │ │ Steam  │ │SteamSpy│
│  5s    │ │  5s    │ │Store   │ │ Web    │ │  5s    │
│        │ │        │ │(Schema)│ │(Players│ │        │
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    │          │          │          │          │
    └────┬─────┴──────────┴──────────┴──────────┘
         ▼
┌─────────────────┐
│ game_metadata   │
│   .json         │
└─────────────────┘
```

All API calls execute simultaneously via `asyncio.gather()`. If one fails, the others still contribute data.

### 4.3 Steam Web API — Important Note

The endpoint `GetNumberOfCurrentPlayers` returns **only** the current number of players online. It does **NOT** return `peak_player_count`. For historical peak data, use SteamDB or Steam Charts as semantic sources via Tavily queries.

---

## 5. Step 2: Dispatch 4 Async Scrapers

Once `game_metadata.json` is ready, 4 async scrapers are launched in parallel via `asyncio.gather()` within a FastAPI `BackgroundTask`.

### 5.1 FastAPI Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SCRAPER SERVICE (FastAPI)                  │
│                                                               │
│  POST /scrape ──► 202 Accepted + scrape_id                     │
│       │                                                        │
│       ▼                                                        │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              BackgroundTasks                              │  │
│  │                                                         │  │
│  │  asyncio.gather(                                        │  │
│  │    scrape_design_art(),                                 │  │
│  │    scrape_user_experience(),                            │  │
│  │    scrape_technology_systems(),                         │  │
│  │    scrape_strategy_market()                             │  │
│  │  )                                                      │  │
│  │                                                         │  │
│  │  Each scraper:                                          │  │
│  │  • Receives game_metadata.json                          │  │
│  │  • Calls domain-specific APIs + Tavily queries          │  │
│  │  • Returns Mini-Context JSON                              │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  GET /scrape/{scrape_id}/status ──► Poll for results          │
│  GET /scrape/{scrape_id}/mini-context/{scraper_id}            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Why Parallel by Macro-Skill?

| Aspect | Sequential | Parallel (Current) |
|--------|------------|-------------------|
| **Latency** | ~4× total time | ~1/4 of sequential |
| **Relevance** | Generic queries | Domain-specific queries |
| **Token Efficiency** | All context mixed | Each skill gets only relevant context |
| **Fault Tolerance** | Total failure on error | Isolated failure per scraper |
| **Scalability** | Hard to scale | Add scrapers without architecture changes |

### 5.3 FastAPI Endpoints

#### `POST /scrape`
- **Request:** `confirmed_game` JSON
- **Response:** `202 Accepted`
  ```json
  {
    "scrape_id": "uuid",
    "game_id": "uuid",
    "status": "processing",
    "message": "Scraping initiated. Poll GET /scrape/{scrape_id}/status for results."
  }
  ```
- **Execution:** Validates input → checks cache → fetches hard data → launches BackgroundTask with 4 scrapers → returns immediately.

#### `GET /scrape/{scrape_id}/status`
- **Response:** `200 OK`
  ```json
  {
    "scrape_id": "uuid",
    "game_id": "uuid",
    "status": "processing | completed | failed | partial",
    "progress": {
      "game_metadata": "completed",
      "scraper_design_art": "completed",
      "scraper_user_experience": "completed",
      "scraper_technology_systems": "completed",
      "scraper_strategy_market": "completed",
      "master_json": "completed"
    },
    "results": { ... },
    "errors": []
  }
  ```

---

## 6. Scraper 1: Design & Art

**Macro-Skill:** Design and Art
**Subcategories:** Gameplay, Level Design, Narrative, Art Direction, Sound Design

### 6.1 Hard Data Sources

| Source | Fields Extracted |
|--------|-----------------|
| IGDB | genres, themes, game_modes, player_perspectives, game_engines, franchises, collections, storyline, summary, cover_url, screenshots, videos, artworks |
| RAWG | description_raw, metacritic, esrb_rating, ratings |
| Steam Web | achievements_schema (name, description, icon) — **skipped if steam_app_id is null** |

### 6.2 Tavily Queries

| Category | Example Queries (for "Elden Ring") |
|----------|-----------------------------------|
| **gameplay_mechanics** | `"Elden Ring (2022) gameplay mechanics analysis deep dive"` |
| | `"Elden Ring core gameplay loop design"` |
| | `"Elden Ring combat system mechanics review"` |
| | `"Elden Ring progression system design"` |
| **level_design** | `"Elden Ring level design analysis"` |
| | `"Elden Ring world design open world layout"` |
| | `"Elden Ring level pacing design"` |
| | `"Elden Ring environmental storytelling"` |
| **narrative** | `"Elden Ring story narrative analysis"` |
| | `"Elden Ring plot writing quality"` |
| | `"Elden Ring character development story"` |
| | `"Elden Ring lore worldbuilding depth"` |
| **art_direction** | `"Elden Ring art direction visual style analysis"` |
| | `"Elden Ring graphics art style review"` |
| | `"Elden Ring visual identity design"` |
| | `"Elden Ring concept art direction"` |
| **sound_design** | `"Elden Ring soundtrack music analysis"` |
| | `"Elden Ring sound design audio review"` |
| | `"Elden Ring voice acting quality"` |
| | `"Elden Ring audio atmosphere immersion"` |

### 6.3 Tavily Platforms

| Platform | Purpose | Query Suffix |
|----------|---------|-------------|
| **Reddit** | Player opinions, design analysis | `site:reddit.com/r/gamedev OR r/games OR r/truegaming` |
| **Dynamic Subreddit** | Game-specific community | `r/{game_name_normalized}` — fallback to general Reddit if doesn't exist |
| **YouTube** | Video reviews and deep dives | `site:youtube.com (review OR analysis OR critique)` |
| **Blogs** | Kotaku, Polygon, IGN analysis | `(Kotaku OR Polygon OR IGN OR GameSpot OR Eurogamer)` |
| **Press** | Professional reviews | `(review OR analysis OR critique OR deep dive)` |

**Game Name Normalization Rules:**
- Lowercase
- Remove special characters except alphanumeric and underscore
- Replace spaces with underscores or remove them
- Examples: `"Elden Ring"` → `"eldenring"` or `"elden_ring"`

---

## 7. Scraper 2: User Experience

**Macro-Skill:** User Experience
**Subcategories:** UI/UX, Accessibility, Localization

### 7.1 Hard Data Sources

| Source | Fields Extracted |
|--------|-----------------|
| IGDB | platforms, languages, language_supports |
| Steam Storefront | supported_languages, system_requirements, controller_support, steam_cloud, steam_achievements — **skipped if steam_app_id is null** |
| Steam Reviews | review_text, voted_up, playtime, timestamp, language — **skipped if steam_app_id is null** |

### 7.2 Tavily Queries

| Category | Example Queries |
|----------|-----------------|
| **ui_ux** | `"Elden Ring UI UX design review"` |
| | `"Elden Ring user interface usability"` |
| | `"Elden Ring HUD design analysis"` |
| | `"Elden Ring menu navigation UX"` |
| **accessibility** | `"Elden Ring accessibility options features"` |
| | `"Elden Ring disability support review"` |
| | `"Elden Ring colorblind mode subtitles"` |
| | `"Elden Ring accessibility rating"` |
| **localization** | `"Elden Ring localization quality translation"` |
| | `"Elden Ring language support review"` |
| | `"Elden Ring regional pricing availability"` |
| | `"Elden Ring cultural adaptation localization"` |

### 7.3 Tavily Platforms

| Platform | Purpose |
|----------|---------|
| **Reddit** | r/gamedev, r/games, r/pcgaming |
| **Steam Reviews** | Direct user feedback on UX — **skipped if steam_app_id is null** |
| **StackOverflow** | Technical bugs affecting UX |
| **Forums** | Bug reports and user feedback |

---

## 8. Scraper 3: Technology & Systems

**Macro-Skill:** Technology and Systems
**Subcategories:** Technology/Performance, Multiplayer/Social, Platforms/Distribution

### 8.1 Hard Data Sources

| Source | Fields Extracted |
|--------|-----------------|
| IGDB | game_engines, platforms, multiplayer_modes, online_coop, offline_coop, lan_coop, split_screen, cross_play |
| RAWG | platforms, parent_platforms, requirements |
| Steam Storefront | pc/mac/linux_requirements, categories, developers, publishers — **skipped if steam_app_id is null** |
| Steam Web | current_player_count — **skipped if steam_app_id is null** |

> ⚠️ **Note:** `GetNumberOfCurrentPlayers` returns **only** `current_player_count`. It does NOT return `peak_player_count`.

### 8.2 Tavily Queries

| Category | Example Queries |
|----------|-----------------|
| **technology_performance** | `"Elden Ring game engine technology analysis"` |
| | `"Elden Ring performance optimization review"` |
| | `"Elden Ring technical architecture breakdown"` |
| | `"Elden Ring graphics engine rendering tech"` |
| **multiplayer_social** | `"Elden Ring multiplayer technical implementation"` |
| | `"Elden Ring online infrastructure netcode"` |
| | `"Elden Ring coop multiplayer technical review"` |
| | `"Elden Ring server architecture backend"` |
| **platforms_distribution** | `"Elden Ring platform requirements performance"` |
| | `"Elden Ring console port technical analysis"` |
| | `"Elden Ring cross platform compatibility"` |
| | `"Elden Ring distribution platforms availability"` |

### 8.3 Tavily Platforms

| Platform | Purpose |
|----------|---------|
| **GitHub** | Game repos, mods, tools |
| **StackOverflow** | Technical implementation discussions |
| **Reddit** | r/gamedev, r/pcgaming, r/tech |
| **HackerNews** | Technical and performance discussions |
| **Dev Blogs** | Postmortems and technical deep dives |

---

## 9. Scraper 4: Strategy & Market

**Macro-Skill:** Strategy and Market
**Subcategories:** Audience, Business Model, Retention/Live Ops, Production/Business, Marketing, Cultural Impact

### 9.1 Hard Data Sources

| Source | Fields Extracted |
|--------|-----------------|
| IGDB | involved_companies, developers, publishers, total_rating, total_rating_count, hypes, follows |
| RAWG | ratings, rating_top, ratings_count, added, added_by_status, suggestions_count |
| Steam Storefront | price_overview, is_free, dlc, recommendations, release_date — **skipped if steam_app_id is null** |
| Steam Web | current_player_count — **skipped if steam_app_id is null** |
| **SteamSpy** | owners_range, average_playtime, ccu, tags, positive/negative_reviews, price, discount — **skipped if steam_app_id is null** |

> ⚠️ **SteamSpy Risk:** Third-party service with occasional downtime. If unavailable, fallback to Steam reviews as popularity proxy. All SteamSpy data is estimated, not official.

### 9.2 Tavily Queries

| Category | Example Queries |
|----------|-----------------|
| **audience** | `"Elden Ring target audience demographics"` |
| | `"Elden Ring player base community analysis"` |
| | `"Elden Ring fan engagement social media"` |
| | `"Elden Ring player retention engagement"` |
| **business_model** | `"Elden Ring monetization strategy revenue"` |
| | `"Elden Ring business model DLC microtransactions"` |
| | `"Elden Ring pricing strategy analysis"` |
| | `"Elden Ring free to play premium model"` |
| **retention_live_ops** | `"Elden Ring player retention metrics"` |
| | `"Elden Ring live service updates content"` |
| | `"Elden Ring seasonal events engagement"` |
| | `"Elden Ring long term player loyalty"` |
| **production_business** | `"Elden Ring development budget production cost"` |
| | `"Elden Ring studio behind development team"` |
| | `"Elden Ring publisher deal business"` |
| | `"Elden Ring development timeline crunch"` |
| **marketing** | `"Elden Ring marketing campaign strategy"` |
| | `"Elden Ring launch marketing spend"` |
| | `"Elden Ring influencer marketing promotion"` |
| | `"Elden Ring social media marketing reach"` |
| **cultural_impact** | `"Elden Ring cultural impact influence"` |
| | `"Elden Ring GOTY awards recognition"` |
| | `"Elden Ring industry influence legacy"` |
| | `"Elden Ring community cultural phenomenon"` |

### 9.3 Tavily Platforms

| Platform | Purpose |
|----------|---------|
| **Reddit** | r/gaming, r/games, r/gamedev, r/business |
| **HackerNews** | Business, market, industry discussions |
| **Press** | VentureBeat, GamesIndustry.biz, Polygon, IGN |
| **Twitter/X** | Trending, viral, community sentiment |
| **Forums** | Community opinion and feedback |

---

## 10. Data Sources Summary

### 10.1 Hard Data (APIs Direct)

| Data | Source | Macro-Skill |
|------|--------|-------------|
| Title, year, dev, publisher | IGDB/RAWG | All |
| Genres, themes, game modes | IGDB | Design & Art, Strategy |
| Platforms, system requirements | IGDB/RAWG/Steam | Technology & Systems |
| Cover art, screenshots, videos | IGDB/RAWG | Design & Art |
| Languages supported | IGDB | User Experience |
| Game engines used | IGDB | Technology & Systems |
| Companies involved | IGDB | Strategy & Market |
| Ratings (ESRB/PEGI) | IGDB | Strategy & Market |
| Prices | Steam Storefront | Strategy & Market |
| User reviews | Steam Reviews | All |
| Achievements | Steam Web API | Design & Art |
| Real-time players | Steam Web API | Strategy & Market |
| Sales estimates | **SteamSpy** | Strategy & Market |
| Community tags | **SteamSpy** | Strategy & Market |

### 10.2 Semantic Data (Tavily)

| Macro-Skill | Categories | Platforms |
|-------------|------------|-----------|
| **Design & Art** | gameplay, level_design, narrative, art_direction, sound_design | Reddit, YouTube, Blogs, Press |
| **User Experience** | ui_ux, accessibility, localization | Reddit, Steam Reviews, StackOverflow, Forums |
| **Technology & Systems** | technology_performance, multiplayer_social, platforms_distribution | GitHub, StackOverflow, Reddit, HackerNews, Dev Blogs |
| **Strategy & Market** | audience, business_model, retention_live_ops, production_business, marketing, cultural_impact | Reddit, HackerNews, Press, Twitter, Forums |

---

## 11. Evidence Count & Confidence Score

### 11.1 Evidence Count

Total number of evidence sources collected by each scraper:

```
evidence_count = (
  count(hard_data fields that are not null/empty)
  + count(semantic_data sources across all categories)
)
```

**Example:** If hard_data has 8 populated fields + semantic_data has 12 sources = `evidence_count: 20`

### 11.2 Confidence Score

Normalized score (0.0 - 1.0) indicating data completeness and reliability:

```
confidence_score = min(1.0, (
  (hard_data_completeness * 0.4) +
  (semantic_data_completeness * 0.4) +
  (source_reliability * 0.2)
))
```

Where:
- `hard_data_completeness` = populated_hard_fields / total_expected_hard_fields
- `semantic_data_completeness` = min(1.0, total_semantic_sources / 15)
- `source_reliability` = average reliability of data sources used (official APIs = 1.0, Tavily press = 0.8, Tavily forums = 0.6)

**Adjustments:**
- `steam_app_id` is null: **-0.15**
- IGDB or RAWG unavailable: **-0.10** each
- Tavily unavailable (semantic_data empty): **-0.25**
- SteamSpy unavailable: **-0.05**

**Thresholds:**

| Range | Interpretation |
|-------|---------------|
| 0.90 - 1.00 | Excellent — all major sources available |
| 0.70 - 0.89 | Good — most sources available, minor gaps |
| 0.50 - 0.69 | Fair — some sources missing, significant gaps |
| 0.30 - 0.49 | Poor — major sources unavailable |
| 0.00 - 0.29 | Critical — insufficient data for analysis |

---

## 12. Error Handling & Fallbacks

### 12.1 Scraper Failure Policy

```
If a scraper fails → The other 3 continue
Failed Mini-Context → null in Master-JSON
Corresponding Macro-Skill → Receives empty context, must handle gracefully
Status endpoint → Reflects "partial" with error details per scraper
```

### 12.2 API Failure Fallbacks

| Failed Source | Fallback | Severity |
|---------------|----------|----------|
| IGDB | Use RAWG as primary; if both fail, use Steam only | Medium |
| RAWG | Use IGDB as primary | Medium |
| Steam | Continue with IGDB/RAWG + Tavily | Low |
| SteamSpy | Use Steam reviews as popularity proxy | Low |
| Tavily | Use only hard data; semantic_data empty | **High** |
| Tavily (rate limit) | Reduce to 3 results/query; increase delay | Medium |

### 12.3 Retry Policy

| Parameter | Value |
|-----------|-------|
| Max retries | 3 |
| Backoff | Exponential |
| Initial delay | 1s |
| Max delay | 30s |
| Retryable codes | 429, 500, 502, 503, 504 |

---

## 13. Caching Strategy

### 13.1 Phase 1 Policy

**No LLM cache** in Phase 1. The cache from the previous project (`_response_cache` in `miner_llm.py`) was for avoiding LLM re-calls. In GetSmart:

- **Phase 1 (Scraper):** NO LLM → No LLM cache
- **Phase 3 (Macro-Skills):** YES uses LLM → Cache implemented there

### 13.2 API Response Cache

| Endpoint | TTL | Storage |
|----------|-----|---------|
| IGDB game metadata | 1 hour | **FastAPI in-memory** |
| RAWG game metadata | 1 hour | **FastAPI in-memory** |
| Steam Storefront details | 1 hour | **FastAPI in-memory** |
| SteamSpy app details | 1 hour | **FastAPI in-memory** |
| Tavily search results | **No cache** | — |
| Steam current players | **No cache** | — |

**Cache key format:** `scraper:{game_id}:{api_source}:{endpoint_hash}`

**Implementation:** Uses `fastapi-cache` with `InMemoryBackend` or a custom thread-safe dictionary. Cache persists during application lifetime and clears on restart. No Redis required.

---

## 14. Rate Limiting

### 14.1 Limits by Source

| Source | Limit | Type |
|--------|-------|------|
| Tavily | 1000 req/month | Hard limit (free tier) |
| IGDB | 4 req/second | Soft limit |
| RAWG | 20 req/second | Soft limit |
| Steam Storefront | 100 req/5min | IP-based |
| SteamSpy | 1 req/second | Soft limit |

### 14.2 Tavily Budget per Game

| Calculation | Value |
|-------------|-------|
| Scrapers | 4 |
| Categories per scraper | 3–6 |
| Queries per category | 4 |
| Requests per query | 1 |
| **Total requests per game** | **68** |
| **Free tier capacity** | **~14 games/month** |

**Circuit Breaker:** If approaching 800 requests/month (80% of limit), reduce `max_results_per_query` from 5 to 3 and log an alert.

---

## 15. Architectural Decisions

### ADR-001: Parallelism by Macro-Skill via FastAPI BackgroundTasks

**Context:** Should we search all data at once or split by domain?

**Decision:** 4 parallel scrapers executed via `asyncio.gather()` within FastAPI BackgroundTasks.

**Rationale:**
1. **Latency:** ~4× faster than sequential
2. **Relevance:** Domain-specific queries = better evidence
3. **Token efficiency:** Each skill receives only relevant context
4. **Fault tolerance:** Isolated failure per scraper
5. **Scalability:** Add scrapers without architecture changes

**Trade-offs:**
- Tavily credits similar or slightly higher (offset by fewer LLM tokens in Phase 3)
- More orchestration complexity (mitigated by FastAPI + asyncio)

### ADR-002: No LLM in Phase 1

**Context:** Previous project used Gemini to analyze Tavily results.

**Decision:** Phase 1 uses NO LLM. Only APIs + Tavily.

**Rationale:**
1. **Determinism:** APIs return predictable structured data
2. **Cost:** Avoid unnecessary LLM tokens
3. **Speed:** APIs are faster than LLM calls
4. **Separation of concerns:** Phase 1 extracts, Phase 3 analyzes

### ADR-003: Include SteamSpy

**Context:** SteamSpy provides sales estimates not available in official APIs.

**Decision:** Yes, include SteamSpy as a direct source.

**Rationale:**
1. Sales estimates critical for Strategy & Market
2. Community tags useful for player perception
3. CCU for retention metrics
4. Price history for monetization analysis

**Risks:**
- Estimated data, not official → Document confidence level
- Strict rate limit (1 req/s) → Implement throttling
- API instability → Graceful degradation with fallback

### ADR-004: Single FastAPI Service with 4 Internal Scrapers

**Context:** 4 separate files vs one file with 4 classes?

**Decision:** Single FastAPI `ScraperService` with 4 internal async methods/classes.

**Rationale:**
1. **Cohesion:** Shared base logic (Tavily, rate limiting, caching)
2. **Maintainability:** Single entry point for debugging
3. **Centralized config:** One YAML for all scrapers
4. **Deployment:** One module to deploy

**Trade-offs:**
- Larger file → Document with docstrings
- Less modularity → Use well-separated internal classes

### ADR-005: FastAPI async/await + BackgroundTasks over Celery

**Context:** Need background task execution without Redis infrastructure.

**Decision:** Use FastAPI BackgroundTasks and `asyncio.gather()` instead of Celery workers.

**Rationale:**
1. **No Redis dependency** → Simpler infrastructure
2. **Native async/await** → Better performance for I/O-bound API calls
3. **FastAPI BackgroundTasks** → Built-in background execution
4. **In-memory cache sufficient** for single-instance deployment

**Trade-offs:**
- No distributed task queue → Single node only
- BackgroundTasks fire-and-forget → Use status polling for long operations
- In-memory cache lost on restart → Acceptable for Phase 1

---

## 16. Monitoring & Observability

### 16.1 Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `scraper_latency_seconds` | histogram | scraper_id, game_id | Total execution time per scraper |
| `scraper_api_calls_total` | counter | api_source, status, game_id | API calls by source and status |
| `scraper_tavily_results_total` | counter | scraper_id, category, game_id | Tavily results by scraper and category |
| `scraper_errors_total` | counter | scraper_id, error_type, game_id | Errors by scraper and type |
| `scraper_evidence_count` | gauge | scraper_id, game_id | Evidence sources collected |
| `scraper_confidence_score` | gauge | scraper_id, game_id | Confidence score per scraper output |

### 16.2 Logging

```json
{
  "timestamp": "2026-06-24T15:05:00Z",
  "level": "INFO",
  "scraper_id": "scraper_design_art",
  "game_id": "a1b2c3d4...",
  "message": "Scraper completed successfully",
  "duration_ms": 45000,
  "api_source": "Tavily",
  "error_details": null,
  "evidence_count": 24,
  "confidence_score": 0.87
}
```

---

## 17. Security & Data Privacy

| Aspect | Policy |
|--------|--------|
| API key storage | Environment variables only |
| Key rotation | Every 90 days |
| Raw Tavily retention | 7 days |
| Mini-Contexts retention | 90 days |
| Master-JSON retention | 1 year |
| PII scrubbing | User names, emails, IPs |

---

## 18. Recommended Code Structure

```
scraper_service/
├── scraper_service.py          # FastAPI app, endpoints, BackgroundTasks
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py           # Abstract base with shared logic
│   ├── design_art_scraper.py     # Scraper 1
│   ├── user_experience_scraper.py # Scraper 2
│   ├── technology_systems_scraper.py # Scraper 3
│   └── strategy_market_scraper.py    # Scraper 4
├── clients/
│   ├── __init__.py
│   ├── igdb_client.py            # Async IGDB with OAuth2
│   ├── rawg_client.py            # Async RAWG
│   ├── steam_client.py           # Async Steam Storefront + Web
│   ├── steamspy_client.py        # Async SteamSpy with rate limit
│   └── tavily_client.py          # Async Tavily with query builder
├── cache/
│   └── memory_cache.py           # In-memory cache implementation
├── models/
│   └── schemas.py                # Pydantic models
└── config/
    └── scraper_contract.yaml     # This specification
```

---

*Document updated 2026-06-24 as part of GetSmart v3.1*
*Version: 1.1.0*
