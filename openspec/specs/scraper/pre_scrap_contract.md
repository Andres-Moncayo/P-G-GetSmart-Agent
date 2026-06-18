# Pre-Scrap & Disambiguation — Functional Specification

> **Artifact:** `pre_scrap_contract.yaml`  
> **Repository path:** `openspec/specs/scraper/pre_scrap_contract.yaml`  
> **Usage:** Frontend disambiguation flow + backend validation of confirmed game input  
> **Phase:** Phase 0 (Disambiguation)  
> **Status:** Draft  
> **Last Updated:** 2026-06-17

---

## 1. Overview

The Disambiguation phase is the **entry gate** of the GetSmart pipeline. Its sole purpose is to resolve homonym collisions — when a game title matches multiple entries (e.g., "Elden Ring" base game vs. DLC vs. spin-off).

The user types a game title, the system queries multiple data sources in parallel, merges and deduplicates results, and presents a ranked list of candidates. The user **must** select one before the "Run Pipeline" button activates.

This deterministic step prevents the pipeline from processing the wrong game, ensuring the final report is accurate and relevant.

---

## 2. Flow Diagram

```mermaid
flowchart TD
    A[User types game title] --> B{Input valid?}
    B -->|No| C[Show validation error]
    C --> A
    B -->|Yes| D[Query IGDB API]
    D --> E[Query RAWG API]
    E --> F{Any results?}
    F -->|No| G[Show "No games found"]
    G --> A
    F -->|Yes| H[Merge & deduplicate candidates]
    H --> I[Render disambiguation list]
    I --> J[User selects game]
    J --> K{Selection valid?}
    K -->|No| I
    K -->|Yes| L[Confirm game_id + year]
    L --> M[Enable "Run Pipeline" button]
    M --> N[User clicks Run Pipeline]
    N --> O[POST /api/v1/pipeline/run]
    O --> P[Return pipeline_id]
    P --> Q[Show Pipeline Modal]
```

---

## 3. Data Sources

### 3.1 Primary Sources

| Source | Endpoint | Auth | Timeout | Query |
|--------|----------|------|---------|-------|
| **IGDB** | `POST /v4/games` | OAuth2 (Twitch) | 5s | `search "{query}"; fields id, name, first_release_date, platforms.name, involved_companies.company.name, genres.name, cover.url, summary; limit 10;` |
| **RAWG** | `GET /api/games` | API Key | 5s | `?search={query}&key=${RAWG_API_KEY}&page_size=10` |

### 3.2 Fallback Source

| Source | Endpoint | Auth | Timeout | When Used |
|--------|----------|------|---------|-----------|
| **Steam** | `GET /api/storesearch/` | None | 3s | When both IGDB and RAWG return empty |

### 3.3 Parallel Execution

```
┌─────────────────┐
│  User Search    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│  IGDB  │ │  RAWG  │
│  5s    │ │  5s    │
└───┬────┘ └───┬────┘
    │          │
    └────┬─────┘
         ▼
┌─────────────────┐
│ Merge & Deduplicate│
└────────┬────────┘
         ▼
┌─────────────────┐
│ Rank by Confidence│
└─────────────────┘
```

Both queries execute simultaneously via `Promise.allSettled()`. If one fails, the other still contributes results.

---

## 4. Candidate Merging Logic

### 4.1 Deduplication Key

Candidates are considered the same game if they share:
- **Exact title match** (case-insensitive, normalized)
- **Same release year** (±1 year tolerance)

### 4.2 Confidence Scoring

| Factor | Weight | Description |
|--------|--------|-------------|
| Title exact match | 40% | Exact string match after normalization |
| Title fuzzy match | 25% | Levenshtein distance < 3 |
| Same year | 20% | Release year matches |
| Same developer | 10% | Developer/publisher match |
| Has cover image | 5% | Visual confirmation |

### 4.3 Merged Candidate Structure

```json
{
  "id": "119388",
  "name": "Elden Ring",
  "slug": "elden-ring",
  "release_year": 2022,
  "release_date": "2022-02-25",
  "developer": "FromSoftware",
  "publisher": "Bandai Namco",
  "platforms": ["PC", "PlayStation 5", "Xbox Series X|S"],
  "genres": ["Action RPG", "RPG"],
  "cover_url": "https://images.igdb.com/...",
  "summary": "THE NEW FANTASY ACTION RPG...",
  "sources": [
    { "provider": "igdb", "external_id": "119388", "confidence": 0.98 },
    { "provider": "rawg", "external_id": "326243", "confidence": 0.95 }
  ],
  "igdb_id": "119388",
  "rawg_id": "326243",
  "steam_app_id": "1245620"
}
```

---

## 5. UI: Disambiguation Modal

### 5.1 Trigger

Modal opens when user submits a search query (Enter key or Search button click).

### 5.2 Layout

```
┌─────────────────────────────────────────────────────────┐
│  ← Back to Dashboard                                    │
│  Searching for "Elden Ring"...                        │
│  We found 3 matches. Please select the correct game:  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  [🎮] Elden Ring                                │   │
│  │      FromSoftware · 2022 · Action RPG           │   │
│  │      igdb: 119388                    ○          │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  [🧩] Elden Ring: Shadow of the Erdtree       │   │
│  │      FromSoftware · 2024 · DLC · Action RPG     │   │
│  │      igdb: 284834                    ○          │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  [🌙] Elden Ring Nightreign                     │   │
│  │      FromSoftware · 2025 · Spin-off            │   │
│  │      igdb: 342156                    ○          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Can't find your game? Search with different terms   │
│                              [Run Pipeline] (disabled)│
└─────────────────────────────────────────────────────────┘
```

### 5.3 Candidate Card

Each candidate is a selectable card:

- **Thumbnail:** `64x64px` rounded-lg. Fallback: gradient background with genre icon
- **Title:** `font-semibold text-base text-primary`
- **Metadata:** `{developer} · {year} · {genre}` — `text-sm text-muted`
- **ID chip:** `igdb: {id}` — monospace, `text-xs text-disabled`, `bg-surface` badge
- **Radio:** `20px` circle. Unchecked: `border-border`. Checked: `border-accent bg-accent` with white dot

**Hover state:** Border transitions to `accent`, background to `accent/5`.
**Selected state:** Same as hover, radio filled.

### 5.4 "Run Pipeline" Button

- **Disabled:** `bg-text-disabled text-text-disabled cursor-not-allowed`
- **Enabled (on selection):** `bg-accent text-white hover:bg-accent-dark shadow-lg shadow-accent/25`

---

## 6. Pipeline Token

When a game is selected, the backend generates a **one-time pipeline token**:

- **TTL:** 5 minutes
- **One-time use:** Invalidated after first use
- **Scope:** Authorizes exactly one pipeline run for the confirmed game

This prevents replay attacks and ensures the pipeline runs only for explicitly confirmed games.

---

## 7. Pipeline Status Polling

After triggering the pipeline, the frontend polls for status:

```typescript
// Every 2 seconds, up to 10 minutes
const pollInterval = setInterval(async () => {
  const status = await fetch(`/api/v1/pipeline/${pipeline_id}/status`);
  if (status === 'completed' || status === 'failed') {
    clearInterval(pollInterval);
    // Update UI accordingly
  }
}, 2000);
```

### 7.1 Status Response

```json
{
  "pipeline_id": "uuid",
  "status": "running",
  "current_phase": 3,
  "phases": [
    { "phase_id": 0, "name": "disambiguation", "status": "completed", "progress_percent": 100 },
    { "phase_id": 1, "name": "ingestion", "status": "completed", "progress_percent": 100 },
    { "phase_id": 2, "name": "consolidation", "status": "completed", "progress_percent": 100 },
    { "phase_id": 3, "name": "parallel_analysis", "status": "running", "progress_percent": 60 },
    { "phase_id": 4, "name": "synthesis", "status": "pending", "progress_percent": 0 }
  ],
  "overall_progress_percent": 60,
  "estimated_completion": "2026-06-17T12:20:00Z"
}
```

---

## 8. Validation Rules

### 8.1 Search Query

| Rule | Value | Error |
|------|-------|-------|
| Min length | 2 chars | "Query too short" |
| Max length | 100 chars | "Query too long" |
| Pattern | `^[a-zA-Z0-9\s\-_:.'()]+$` | "Invalid characters" |
| Forbidden | `script`, `javascript`, `<`, `>`, `{`, `}` | "Potentially harmful query" |

### 8.2 Candidate Selection

- Must be from the returned results list
- Must have a valid `igdb_id`
- Candidates older than 7 days must be re-fetched

---

## 9. Rate Limits

| Endpoint | Window | Max | Per |
|----------|--------|-----|-----|
| `GET /api/v1/games/search` | 1 minute | 10 | User |
| `POST /api/v1/pipeline/run` | 1 hour | 5 | User |

---

## 10. Error Handling

| Scenario | HTTP | Code | User Message |
|----------|------|------|-------------|
| No results found | 200 | — | "No games found. Try a different search term." |
| Invalid query | 400 | SEARCH_001 | "Search query is invalid" |
| Rate limit | 429 | — | "Too many searches. Please wait." |
| IGDB down | 200 | — | Results from RAWG only, with warning |
| Invalid pipeline token | 401 | PIPE_001 | "Selection expired. Please search again." |
| Pipeline already running | 409 | PIPE_002 | "A report for this game is already being generated." |
