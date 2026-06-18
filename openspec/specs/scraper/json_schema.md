# Master-JSON Schema — Functional Specification

> **Artifact:** `master_json_schema.yaml`  
> **Repository path:** `openspec/specs/scraper/master_json_schema.yaml`  
> **Usage:** Backend consolidation schema document, reference for Macro-Skills  
> **Phase:** Phase 2 (Consolidation)  
> **Status:** Draft  
> **Last Updated:** 2026-06-17

---

## 1. Overview

The **Master-JSON** (also called **Super-JSON**) is the central artifact of the GetSmart pipeline. It consolidates all information collected in Phase 1 (Scraper) into a single structured JSON document that feeds simultaneously into the 4 Macro-Skills of analysis in Phase 3.

**Key characteristics:**
- **Deterministic:** Same Phase 1 input → same Master-JSON
- **Partitioned:** Direct mapping to the 17 thematic categories
- **Traceable:** Every semantic datum includes source (URL, platform)
- **Fault-tolerant:** Failed workers produce `null` sections

---

## 2. Structure

```
Master-JSON
├── metadata                    # Generation info
├── game_metadata               # Consolidated hard data (IGDB + RAWG + Steam + SteamSpy)
│   ├── game_id
│   ├── name
│   ├── release_year
│   ├── aliases
│   ├── igdb                    # IGDB API data
│   ├── rawg                    # RAWG API data
│   ├── steam                   # Steam APIs data
│   └── steamspy                # SteamSpy estimated data
├── mini_contexts               # 4 worker contexts
│   ├── design_art              # Worker 1: Design & Art
│   ├── user_experience         # Worker 2: UX
│   ├── technology_systems      # Worker 3: Tech & Systems
│   └── strategy_market         # Worker 4: Strategy & Market
└── partitions                  # Index mapping 17 categories
    ├── gameplay
    ├── level_design
    ├── narrative
    ├── art_direction
    ├── sound_design
    ├── ui_ux
    ├── accessibility
    ├── localization
    ├── technology_performance
    ├── multiplayer_social
    ├── platforms_distribution
    ├── audience
    ├── business_model
    ├── retention_live_ops
    ├── production_business
    ├── marketing
    └── cultural_impact
```

---

## 3. Metadata

Metadata about the Master-JSON generation itself.

| Field | Type | Description |
|-------|------|-------------|
| `game_id` | UUID | Internal game UUID in GetSmart |
| `game_name` | string | Exact game name |
| `generated_at` | ISO 8601 | Generation timestamp |
| `version` | semver | Schema version (e.g., "1.0.0") |
| `workers_executed` | array<string> | Successfully executed workers |
| `workers_failed` | array<string> | Failed workers (empty = total success) |
| `total_evidence_count` | integer | Sum of all collected sources |
| `overall_confidence_score` | float [0-1] | Weighted average confidence |

**Example:**

```json
{
  "game_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "game_name": "Elden Ring",
  "generated_at": "2026-06-17T15:10:00Z",
  "version": "1.0.0",
  "workers_executed": ["design_art", "user_experience", "technology_systems", "strategy_market"],
  "workers_failed": [],
  "total_evidence_count": 87,
  "overall_confidence_score": 0.82
}
```

---

## 4. Game Metadata

Structured data extracted directly from APIs. This section is the **single source of truth** for hard data.

### 4.1 IGDB

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | IGDB game ID |
| `genres` | array<string> | Game genres |
| `themes` | array<string> | Themes (fantasy, sci-fi, etc.) |
| `game_modes` | array<string> | Modes (single, multiplayer, coop) |
| `player_perspectives` | array<string> | Perspective (first-person, third-person) |
| `game_engines` | array<object> | Engines used (id, name) |
| `involved_companies` | array<object> | Companies with role (developer, publisher, etc.) |
| `platforms` | array<string> | Supported platforms |
| `languages` | array<string> | Available languages |
| `language_supports` | array<object> | Detailed support per language (interface, audio, subtitles) |
| `multiplayer_modes` | array<string> | Multiplayer modes |
| `online_coop` | boolean | Online coop? |
| `offline_coop` | boolean | Offline coop? |
| `lan_coop` | boolean | LAN coop? |
| `split_screen` | boolean | Split screen? |
| `cross_play` | boolean | Cross-play? |
| `storyline` | string\|null | Game synopsis |
| `summary` | string\|null | Summary |
| `cover_url` | URI\|null | Cover image URL |
| `screenshots` | array<object> | Screenshots with dimensions |
| `videos` | array<object> | Videos with name |
| `artworks` | array<object> | Artworks with dimensions |
| `total_rating` | float [0-100]\|null | Average rating |
| `total_rating_count` | integer | Number of ratings |
| `hypes` | integer | Pre-launch hypes |
| `follows` | integer | Followers |

### 4.2 RAWG

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | RAWG game ID |
| `description_raw` | string\|null | Plain text description |
| `metacritic` | integer [0-100]\|null | Metacritic score |
| `esrb_rating` | string\|null | ESRB rating |
| `ratings` | array<object> | Distribution by title (exceptional, recommended, etc.) |
| `ratings_count` | integer | Total ratings |
| `reviews_text_count` | integer | Text reviews |
| `added` | integer | Times added to lists |
| `added_by_status` | object | Distribution by status (owned, playing, etc.) |
| `suggestions_count` | integer | Related game suggestions |

### 4.3 Steam

| Field | Type | Description |
|-------|------|-------------|
| `app_id` | integer | Steam App ID |
| `price_overview` | object\|null | Price, currency, discount |
| `is_free` | boolean | Is free? |
| `dlc_count` | integer | Number of DLCs |
| `packages` | array<object> | Available packages |
| `recommendations` | integer\|null | Steam recommendations count |
| `release_date` | string\|null | Steam release date |
| `coming_soon` | boolean | Coming soon? |
| `supported_languages` | string\|null | Language list (plain string) |
| `system_requirements` | object | Minimum and recommended |
| `controller_support` | boolean | Controller support? |
| `full_controller_support` | boolean | Full controller support? |
| `steam_cloud` | boolean | Steam Cloud? |
| `steam_achievements` | boolean | Has achievements? |
| `categories` | array<string> | Steam categories |
| `developers` | array<string> | Steam developers |
| `publishers` | array<string> | Steam publishers |
| `pc_requirements` | object\|null | PC requirements |
| `mac_requirements` | object\|null | Mac requirements |
| `linux_requirements` | object\|null | Linux requirements |
| `current_player_count` | integer\|null | Current players |

### 4.4 SteamSpy

| Field | Type | Description |
|-------|------|-------------|
| `owners_range` | string\|null | Estimated owners (e.g., "5M .. 10M") |
| `average_playtime` | integer\|null | Average playtime in minutes |
| `median_playtime` | integer\|null | Median playtime in minutes |
| `ccu` | integer\|null | Concurrent users |
| `tags` | array<string> | Community tags |
| `positive_reviews` | integer\|null | Positive reviews |
| `negative_reviews` | integer\|null | Negative reviews |
| `price` | integer\|null | Current price in cents |
| `discount` | integer\|null | Current discount % |

---

## 5. Mini-Contexts

Each Mini-Context follows the same base structure:

```
mini_context_X
├── metadata              # Worker info
├── hard_data             # Relevant subset of game_metadata
├── semantic_data         # Tavily data organized by category
├── evidence_count        # Total sources
└── confidence_score      # [0.0 - 1.0]
```

### 5.1 Base Metadata

| Field | Type | Description |
|-------|------|-------------|
| `game_id` | UUID | Game UUID |
| `game_name` | string | Game name |
| `macro_skill` | enum | "Design and Art" \| "User Experience" \| "Technology and Systems" \| "Strategy and Market" |
| `worker_id` | enum | "scraper_design_art" \| "scraper_user_experience" \| "scraper_technology_systems" \| "scraper_strategy_market" |
| `generated_at` | ISO 8601 | Timestamp |
| `data_sources` | array<string> | Sources used (IGDB, RAWG, Steam, SteamSpy, Tavily) |

### 5.2 Semantic Source

Every Tavily source is represented as:

| Field | Type | Description |
|-------|------|-------------|
| `url` | URI | Source URL |
| `title` | string | Article/post title |
| `snippet` | string | Raw content or summary |
| `platform` | enum | reddit \| youtube \| blogs \| press \| steam_reviews \| stackoverflow \| forums \| github \| hackernews \| twitter \| dev_blogs |
| `published_at` | ISO 8601\|null | Publication date |
| `author` | string\|null | Author |

### 5.3 Semantic Category

| Field | Type | Description |
|-------|------|-------------|
| `sources` | array<semantic_source> | Tavily sources |
| `summary` | string\|null | Optional summary (NOT LLM-generated) |

### 5.4 Design & Art Mini-Context

**Macro-Skill:** Design and Art  
**Subcategories:** Gameplay, Level Design, Narrative, Art Direction, Sound Design

#### Hard Data

| Field | Source in game_metadata |
|-------|------------------------|
| `genres` | `game_metadata.igdb.genres` |
| `themes` | `game_metadata.igdb.themes` |
| `game_modes` | `game_metadata.igdb.game_modes` |
| `player_perspectives` | `game_metadata.igdb.player_perspectives` |
| `game_engines` | `game_metadata.igdb.game_engines[].name` |
| `franchises` | `game_metadata.igdb.franchises` |
| `collections` | `game_metadata.igdb.collections` |
| `storyline` | `game_metadata.igdb.storyline` |
| `summary` | `game_metadata.igdb.summary` |
| `cover_url` | `game_metadata.igdb.cover_url` |
| `screenshots` | `game_metadata.igdb.screenshots` |
| `videos` | `game_metadata.igdb.videos` |
| `artworks` | `game_metadata.igdb.artworks` |
| `description_raw` | `game_metadata.rawg.description_raw` |
| `metacritic` | `game_metadata.rawg.metacritic` |
| `esrb_rating` | `game_metadata.rawg.esrb_rating` |
| `ratings_distribution` | `game_metadata.rawg.ratings` |
| `achievements_schema` | `game_metadata.steam.achievements` |

#### Semantic Data

| Category | Tavily Queries | Platforms |
|----------|---------------|-----------|
| `gameplay_mechanics` | gameplay, combat, progression | Reddit, YouTube, Blogs, Press |
| `level_design` | level design, world design, pacing | Reddit, YouTube, Blogs, Press |
| `narrative` | story, plot, character, lore | Reddit, YouTube, Blogs, Press |
| `art_direction` | art style, visual identity, graphics | Reddit, YouTube, Blogs, Press |
| `sound_design` | soundtrack, music, audio, voice acting | Reddit, YouTube, Blogs, Press |

### 5.5 User Experience Mini-Context

**Macro-Skill:** User Experience  
**Subcategories:** UI/UX, Accessibility, Localization

#### Hard Data

| Field | Source in game_metadata |
|-------|------------------------|
| `platforms` | `game_metadata.igdb.platforms` |
| `languages_supported` | `game_metadata.igdb.languages` |
| `system_requirements` | `game_metadata.steam.system_requirements` |
| `controller_support` | `game_metadata.steam.controller_support` |
| `full_controller_support` | `game_metadata.steam.full_controller_support` |
| `steam_cloud` | `game_metadata.steam.steam_cloud` |
| `steam_achievements` | `game_metadata.steam.steam_achievements` |

#### Semantic Data

| Category | Tavily Queries | Platforms |
|----------|---------------|-----------|
| `ui_ux` | UI design, usability, HUD, menus | Reddit, Steam Reviews, StackOverflow |
| `accessibility` | accessibility, disability, colorblind | Reddit, Steam Reviews, Forums |
| `localization` | translation, language, regional | Reddit, Steam Reviews, Forums |

**Extra:** `steam_reviews_sample` — Steam review sample with metadata (voted_up, playtime, language).

### 5.6 Technology & Systems Mini-Context

**Macro-Skill:** Technology and Systems  
**Subcategories:** Technology/Performance, Multiplayer/Social, Platforms/Distribution

#### Hard Data

| Field | Source in game_metadata |
|-------|------------------------|
| `game_engines` | `game_metadata.igdb.game_engines[].name` |
| `platforms` | `game_metadata.igdb.platforms` |
| `multiplayer_modes` | `game_metadata.igdb.multiplayer_modes` |
| `online_coop` | `game_metadata.igdb.online_coop` |
| `offline_coop` | `game_metadata.igdb.offline_coop` |
| `lan_coop` | `game_metadata.igdb.lan_coop` |
| `split_screen` | `game_metadata.igdb.split_screen` |
| `cross_play` | `game_metadata.igdb.cross_play` |
| `pc_requirements` | `game_metadata.steam.pc_requirements` |
| `mac_requirements` | `game_metadata.steam.mac_requirements` |
| `linux_requirements` | `game_metadata.steam.linux_requirements` |
| `current_player_count` | `game_metadata.steam.current_player_count` |

#### Semantic Data

| Category | Tavily Queries | Platforms |
|----------|---------------|-----------|
| `technology_performance` | engine, performance, rendering, optimization | GitHub, StackOverflow, Reddit, HackerNews |
| `multiplayer_social` | netcode, servers, coop technical | GitHub, StackOverflow, Reddit, Dev Blogs |
| `platforms_distribution` | ports, requirements, cross-platform | GitHub, StackOverflow, Reddit, HackerNews |

### 5.7 Strategy & Market Mini-Context

**Macro-Skill:** Strategy and Market  
**Subcategories:** Audience, Business Model, Retention/Live Ops, Production/Business, Marketing, Cultural Impact

#### Hard Data

| Field | Source in game_metadata |
|-------|------------------------|
| `involved_companies` | `game_metadata.igdb.involved_companies` |
| `developers` | `game_metadata.igdb.involved_companies` (role=developer) |
| `publishers` | `game_metadata.igdb.involved_companies` (role=publisher) |
| `franchises` | `game_metadata.igdb.franchises` |
| `total_rating` | `game_metadata.igdb.total_rating` |
| `total_rating_count` | `game_metadata.igdb.total_rating_count` |
| `ratings_distribution` | `game_metadata.rawg.ratings` |
| `price_overview` | `game_metadata.steam.price_overview` |
| `is_free` | `game_metadata.steam.is_free` |
| `dlc_count` | `game_metadata.steam.dlc_count` |
| `recommendations` | `game_metadata.steam.recommendations` |
| `release_date` | `game_metadata.steam.release_date` |
| `owners_range` | `game_metadata.steamspy.owners_range` |
| `average_playtime` | `game_metadata.steamspy.average_playtime` |
| `median_playtime` | `game_metadata.steamspy.median_playtime` |
| `ccu` | `game_metadata.steamspy.ccu` |
| `steamspy_tags` | `game_metadata.steamspy.tags` |
| `positive_reviews` | `game_metadata.steamspy.positive_reviews` |
| `negative_reviews` | `game_metadata.steamspy.negative_reviews` |
| `current_player_count` | `game_metadata.steam.current_player_count` |

#### Semantic Data

| Category | Tavily Queries | Platforms |
|----------|---------------|-----------|
| `audience` | demographics, player base, community | Reddit, HackerNews, Press, Twitter |
| `business_model` | monetization, pricing, DLC, microtransactions | Reddit, HackerNews, Press |
| `retention_live_ops` | retention, updates, seasonal events | Reddit, Press, Forums |
| `production_business` | budget, studio, publisher deal, timeline | Press, HackerNews, Reddit |
| `marketing` | campaign, influencers, social media | Press, Twitter, Reddit |
| `cultural_impact` | GOTY, awards, influence, legacy | Press, Reddit, Twitter |

---

## 6. Partitions (17 Categories)

Partitions are an **access index** that maps each thematic category to its exact location within the Mini-Contexts. This allows Macro-Skills to access relevant evidence directly without navigating the full structure.

### 6.1 Design & Art (5 categories)

| Category | `source_macro_skill` | `source_path` |
|----------|---------------------|---------------|
| `gameplay` | "design_art" | `mini_contexts.design_art.semantic_data.gameplay_mechanics` |
| `level_design` | "design_art" | `mini_contexts.design_art.semantic_data.level_design` |
| `narrative` | "design_art" | `mini_contexts.design_art.semantic_data.narrative` |
| `art_direction` | "design_art" | `mini_contexts.design_art.semantic_data.art_direction` |
| `sound_design` | "design_art" | `mini_contexts.design_art.semantic_data.sound_design` |

### 6.2 User Experience (3 categories)

| Category | `source_macro_skill` | `source_path` |
|----------|---------------------|---------------|
| `ui_ux` | "user_experience" | `mini_contexts.user_experience.semantic_data.ui_ux` |
| `accessibility` | "user_experience" | `mini_contexts.user_experience.semantic_data.accessibility` |
| `localization` | "user_experience" | `mini_contexts.user_experience.semantic_data.localization` |

### 6.3 Technology & Systems (3 categories)

| Category | `source_macro_skill` | `source_path` |
|----------|---------------------|---------------|
| `technology_performance` | "technology_systems" | `mini_contexts.technology_systems.semantic_data.technology_performance` |
| `multiplayer_social` | "technology_systems" | `mini_contexts.technology_systems.semantic_data.multiplayer_social` |
| `platforms_distribution` | "technology_systems" | `mini_contexts.technology_systems.semantic_data.platforms_distribution` |

### 6.4 Strategy & Market (6 categories)

| Category | `source_macro_skill` | `source_path` |
|----------|---------------------|---------------|
| `audience` | "strategy_market" | `mini_contexts.strategy_market.semantic_data.audience` |
| `business_model` | "strategy_market" | `mini_contexts.strategy_market.semantic_data.business_model` |
| `retention_live_ops` | "strategy_market" | `mini_contexts.strategy_market.semantic_data.retention_live_ops` |
| `production_business` | "strategy_market" | `mini_contexts.strategy_market.semantic_data.production_business` |
| `marketing` | "strategy_market" | `mini_contexts.strategy_market.semantic_data.marketing` |
| `cultural_impact` | "strategy_market" | `mini_contexts.strategy_market.semantic_data.cultural_impact` |

### 6.5 Partition Structure

```json
{
  "source_macro_skill": "design_art",
  "source_path": "mini_contexts.design_art.semantic_data.gameplay_mechanics",
  "evidence_count": 12,
  "confidence_score": 0.85
}
```

---

## 7. Validation

### 7.1 Validation Rules

| Rule | Application | Description |
|------|-------------|-------------|
| `evidence_count_non_negative` | `mini_contexts.*.evidence_count` | Must be >= 0 |
| `confidence_score_range` | `mini_contexts.*.confidence_score`, `metadata.overall_confidence_score` | Must be [0.0, 1.0] |
| `semantic_source_required_fields` | `mini_contexts.*.semantic_data.*.sources.*` | url, title, snippet, platform required |
| `partition_mapping_consistency` | `partitions.*.source_path` | Must map to existing path |
| `worker_failure_handling` | `mini_contexts.*` | May be null if worker failed |

### 7.2 Pydantic Validation

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class SemanticSource(BaseModel):
    url: str
    title: str
    snippet: str
    platform: str  # enum validation
    published_at: Optional[datetime] = None
    author: Optional[str] = None

class SemanticCategory(BaseModel):
    sources: List[SemanticSource]
    summary: Optional[str] = None

class MiniContextMetadata(BaseModel):
    game_id: str
    game_name: str
    macro_skill: str  # 4-value enum
    worker_id: str    # 4-value enum
    generated_at: datetime
    data_sources: List[str]

class MiniContext(BaseModel):
    metadata: MiniContextMetadata
    hard_data: dict
    semantic_data: dict
    evidence_count: int = Field(ge=0)
    confidence_score: float = Field(ge=0.0, le=1.0)

class MasterJSON(BaseModel):
    metadata: dict
    game_metadata: dict
    mini_contexts: dict  # 4 keys
    partitions: dict     # 17 keys
```

---

## 8. Example: Complete Master-JSON for "Elden Ring"

```json
{
  "metadata": {
    "game_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "game_name": "Elden Ring",
    "generated_at": "2026-06-17T15:10:00Z",
    "version": "1.0.0",
    "workers_executed": ["design_art", "user_experience", "technology_systems", "strategy_market"],
    "workers_failed": [],
    "total_evidence_count": 87,
    "overall_confidence_score": 0.82
  },
  "game_metadata": {
    "game_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Elden Ring",
    "release_year": 2022,
    "aliases": ["ELDEN RING"],
    "igdb": {
      "id": 119133,
      "genres": ["RPG", "Action"],
      "themes": ["Fantasy", "Dark Fantasy", "Open World"],
      "game_modes": ["Single player", "Multiplayer", "Co-operative"],
      "player_perspectives": ["Third person"],
      "game_engines": [{"id": 437, "name": "Proprietary Engine"}],
      "involved_companies": [
        {"name": "FromSoftware", "role": "developer", "type": "company"},
        {"name": "Bandai Namco Entertainment", "role": "publisher", "type": "company"}
      ],
      "platforms": ["PC", "PS4", "PS5", "Xbox One", "Xbox Series X|S"],
      "languages": ["English", "French", "German", "Italian", "Japanese", "Korean", "Polish", "Portuguese", "Russian", "Spanish", "Thai", "Chinese"],
      "storyline": "THE NEW FANTASY ACTION RPG. Rise, Tarnished...",
      "summary": "Elden Ring is an action RPG which takes place in the Lands Between...",
      "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co4jni.png",
      "screenshots": [{"url": "https://images.igdb.com/...", "width": 1920, "height": 1080}],
      "total_rating": 96.5,
      "total_rating_count": 2847
    },
    "rawg": {
      "id": 326243,
      "description_raw": "Elden Ring is an action RPG which takes place...",
      "metacritic": 96,
      "esrb_rating": "Mature",
      "ratings": [
        {"title": "exceptional", "count": 1200, "percent": 65.0},
        {"title": "recommended", "count": 400, "percent": 22.0},
        {"title": "meh", "count": 150, "percent": 8.0},
        {"title": "skip", "count": 90, "percent": 5.0}
      ],
      "ratings_count": 1840,
      "reviews_text_count": 1200,
      "added": 45000,
      "suggestions_count": 350
    },
    "steam": {
      "app_id": 1245620,
      "price_overview": {"currency": "USD", "initial": 5999, "final": 5999, "discount_percent": 0},
      "is_free": false,
      "dlc_count": 1,
      "recommendations": 1200000,
      "release_date": "2022-02-25",
      "coming_soon": false,
      "supported_languages": "English, French, Italian, German, Spanish - Spain, Japanese, Korean, Polish, Portuguese - Brazil, Russian, Simplified Chinese, Thai, Traditional Chinese",
      "system_requirements": {"minimum": "OS: Windows 10...", "recommended": "OS: Windows 10/11..."},
      "controller_support": true,
      "full_controller_support": true,
      "steam_cloud": true,
      "steam_achievements": true,
      "categories": ["Single-player", "Online Co-op", "Steam Achievements", "Full Controller Support", "Steam Cloud"],
      "developers": ["FromSoftware Inc."],
      "publishers": ["FromSoftware Inc.", "Bandai Namco Entertainment"],
      "current_player_count": 45000
    },
    "steamspy": {
      "owners_range": "5,000,000 .. 10,000,000",
      "average_playtime": 98760,
      "median_playtime": 54320,
      "ccu": 45000,
      "tags": ["Souls-like", "Open World", "RPG", "Difficult", "Action RPG", "Dark Fantasy", "Exploration"],
      "positive_reviews": 950000,
      "negative_reviews": 50000,
      "price": 5999,
      "discount": 0
    }
  },
  "mini_contexts": {
    "design_art": {
      "metadata": {
        "game_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "game_name": "Elden Ring",
        "macro_skill": "Design and Art",
        "worker_id": "scraper_design_art",
        "generated_at": "2026-06-17T15:05:00Z",
        "data_sources": ["IGDB", "RAWG", "Steam", "Tavily"]
      },
      "hard_data": {
        "genres": ["RPG", "Action"],
        "themes": ["Fantasy", "Dark Fantasy", "Open World"],
        "storyline": "THE NEW FANTASY ACTION RPG...",
        "cover_url": "https://images.igdb.com/...",
        "screenshots": [{"url": "...", "width": 1920, "height": 1080}],
        "achievements_schema": [{"name": "Elden Lord", "description": "...", "icon": "..."}]
      },
      "semantic_data": {
        "gameplay_mechanics": {
          "sources": [
            {
              "url": "https://www.reddit.com/r/games/comments/...",
              "title": "Elden Ring's combat system is a masterpiece",
              "snippet": "The stagger system, weapon arts, and spirit ashes create a deep combat experience...",
              "platform": "reddit",
              "published_at": null,
              "author": null
            }
          ],
          "summary": null
        },
        "level_design": {"sources": [], "summary": null},
        "narrative": {"sources": [], "summary": null},
        "art_direction": {"sources": [], "summary": null},
        "sound_design": {"sources": [], "summary": null}
      },
      "evidence_count": 25,
      "confidence_score": 0.85
    },
    "user_experience": {
      "metadata": {
        "game_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "game_name": "Elden Ring",
        "macro_skill": "User Experience",
        "worker_id": "scraper_user_experience",
        "generated_at": "2026-06-17T15:05:00Z",
        "data_sources": ["IGDB", "Steam", "Tavily"]
      },
      "hard_data": {
        "platforms": ["PC", "PS4", "PS5", "Xbox One", "Xbox Series X|S"],
        "languages_supported": ["English", "French", "German", "Italian", "Japanese", "Korean", "Polish", "Portuguese", "Russian", "Spanish", "Thai", "Chinese"],
        "system_requirements": {"minimum": "...", "recommended": "..."},
        "controller_support": true,
        "full_controller_support": true,
        "steam_cloud": true,
        "steam_achievements": true
      },
      "semantic_data": {
        "ui_ux": {"sources": [], "summary": null},
        "accessibility": {"sources": [], "summary": null},
        "localization": {"sources": [], "summary": null},
        "steam_reviews_sample": {
          "positive_count": 950000,
          "negative_count": 50000,
          "review_score": 0.95,
          "sample_reviews": [
            {"review": "Best game I've ever played...", "voted_up": true, "playtime_hours": 120.5, "language": "english"}
          ]
        }
      },
      "evidence_count": 18,
      "confidence_score": 0.78
    },
    "technology_systems": {
      "metadata": {
        "game_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "game_name": "Elden Ring",
        "macro_skill": "Technology and Systems",
        "worker_id": "scraper_technology_systems",
        "generated_at": "2026-06-17T15:05:00Z",
        "data_sources": ["IGDB", "RAWG", "Steam", "Tavily"]
      },
      "hard_data": {
        "game_engines": ["Proprietary Engine"],
        "platforms": ["PC", "PS4", "PS5", "Xbox One", "Xbox Series X|S"],
        "multiplayer_modes": ["Online Co-op", "Online PvP"],
        "online_coop": true,
        "offline_coop": false,
        "lan_coop": false,
        "split_screen": false,
        "cross_play": false,
        "pc_requirements": {"minimum": "...", "recommended": "..."},
        "current_player_count": 45000
      },
      "semantic_data": {
        "technology_performance": {"sources": [], "summary": null},
        "multiplayer_social": {"sources": [], "summary": null},
        "platforms_distribution": {"sources": [], "summary": null}
      },
      "evidence_count": 22,
      "confidence_score": 0.80
    },
    "strategy_market": {
      "metadata": {
        "game_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "game_name": "Elden Ring",
        "macro_skill": "Strategy and Market",
        "worker_id": "scraper_strategy_market",
        "generated_at": "2026-06-17T15:05:00Z",
        "data_sources": ["IGDB", "RAWG", "Steam", "SteamSpy", "Tavily"]
      },
      "hard_data": {
        "involved_companies": [
          {"name": "FromSoftware", "role": "developer", "type": "company"},
          {"name": "Bandai Namco Entertainment", "role": "publisher", "type": "company"}
        ],
        "developers": ["FromSoftware Inc."],
        "publishers": ["FromSoftware Inc.", "Bandai Namco Entertainment"],
        "total_rating": 96.5,
        "total_rating_count": 2847,
        "price_overview": {"currency": "USD", "initial": 5999, "final": 5999},
        "is_free": false,
        "dlc_count": 1,
        "recommendations": 1200000,
        "owners_range": "5,000,000 .. 10,000,000",
        "ccu": 45000,
        "steamspy_tags": ["Souls-like", "Open World", "RPG", "Difficult", "Action RPG"],
        "positive_reviews": 950000,
        "negative_reviews": 50000
      },
      "semantic_data": {
        "audience": {"sources": [], "summary": null},
        "business_model": {"sources": [], "summary": null},
        "retention_live_ops": {"sources": [], "summary": null},
        "production_business": {"sources": [], "summary": null},
        "marketing": {"sources": [], "summary": null},
        "cultural_impact": {"sources": [], "summary": null}
      },
      "evidence_count": 22,
      "confidence_score": 0.85
    }
  },
  "partitions": {
    "gameplay": {
      "source_macro_skill": "design_art",
      "source_path": "mini_contexts.design_art.semantic_data.gameplay_mechanics",
      "evidence_count": 5,
      "confidence_score": 0.85
    },
    "level_design": {
      "source_macro_skill": "design_art",
      "source_path": "mini_contexts.design_art.semantic_data.level_design",
      "evidence_count": 5,
      "confidence_score": 0.85
    },
    "narrative": {
      "source_macro_skill": "design_art",
      "source_path": "mini_contexts.design_art.semantic_data.narrative",
      "evidence_count": 5,
      "confidence_score": 0.85
    },
    "art_direction": {
      "source_macro_skill": "design_art",
      "source_path": "mini_contexts.design_art.semantic_data.art_direction",
      "evidence_count": 5,
      "confidence_score": 0.85
    },
    "sound_design": {
      "source_macro_skill": "design_art",
      "source_path": "mini_contexts.design_art.semantic_data.sound_design",
      "evidence_count": 5,
      "confidence_score": 0.85
    },
    "ui_ux": {
      "source_macro_skill": "user_experience",
      "source_path": "mini_contexts.user_experience.semantic_data.ui_ux",
      "evidence_count": 6,
      "confidence_score": 0.78
    },
    "accessibility": {
      "source_macro_skill": "user_experience",
      "source_path": "mini_contexts.user_experience.semantic_data.accessibility",
      "evidence_count": 6,
      "confidence_score": 0.78
    },
    "localization": {
      "source_macro_skill": "user_experience",
      "source_path": "mini_contexts.user_experience.semantic_data.localization",
      "evidence_count": 6,
      "confidence_score": 0.78
    },
    "technology_performance": {
      "source_macro_skill": "technology_systems",
      "source_path": "mini_contexts.technology_systems.semantic_data.technology_performance",
      "evidence_count": 7,
      "confidence_score": 0.80
    },
    "multiplayer_social": {
      "source_macro_skill": "technology_systems",
      "source_path": "mini_contexts.technology_systems.semantic_data.multiplayer_social",
      "evidence_count": 7,
      "confidence_score": 0.80
    },
    "platforms_distribution": {
      "source_macro_skill": "technology_systems",
      "source_path": "mini_contexts.technology_systems.semantic_data.platforms_distribution",
      "evidence_count": 8,
      "confidence_score": 0.80
    },
    "audience": {
      "source_macro_skill": "strategy_market",
      "source_path": "mini_contexts.strategy_market.semantic_data.audience",
      "evidence_count": 4,
      "confidence_score": 0.85
    },
    "business_model": {
      "source_macro_skill": "strategy_market",
      "source_path": "mini_contexts.strategy_market.semantic_data.business_model",
      "evidence_count": 4,
      "confidence_score": 0.85
    },
    "retention_live_ops": {
      "source_macro_skill": "strategy_market",
      "source_path": "mini_contexts.strategy_market.semantic_data.retention_live_ops",
      "evidence_count": 4,
      "confidence_score": 0.85
    },
    "production_business": {
      "source_macro_skill": "strategy_market",
      "source_path": "mini_contexts.strategy_market.semantic_data.production_business",
      "evidence_count": 3,
      "confidence_score": 0.85
    },
    "marketing": {
      "source_macro_skill": "strategy_market",
      "source_path": "mini_contexts.strategy_market.semantic_data.marketing",
      "evidence_count": 4,
      "confidence_score": 0.85
    },
    "cultural_impact": {
      "source_macro_skill": "strategy_market",
      "source_path": "mini_contexts.strategy_market.semantic_data.cultural_impact",
      "evidence_count": 3,
      "confidence_score": 0.85
    }
  }
}
```

---

## 9. Glossary

| Term | Definition |
|------|------------|
| **Master-JSON** | Central artifact consolidating all game data |
| **Super-JSON** | Synonym of Master-JSON |
| **Mini-Context** | Structured JSON produced by a scraper worker |
| **Hard Data** | Structured data from direct APIs |
| **Semantic Data** | Unstructured data from web searches (Tavily) |
| **Partition** | Mapping of a thematic category to its location in Mini-Contexts |
| **Macro-Skill** | Analysis cluster: Design & Art, UX, Tech & Systems, Strategy & Market |
| **Evidence Count** | Number of semantic sources collected |
| **Confidence Score** | [0-1] metric indicating evidence quality/quantity |
| **Semantic Source** | Tavily source object with URL, title, snippet, platform |

---

*Document generated 2026-06-17 as part of GetSmart v3.0*
