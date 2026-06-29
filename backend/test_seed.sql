-- =============================================================
-- GetSmart — Test Seed Data v1.0
-- Tablas: analysis, reports
-- Usuario base: 00000000-0000-0000-0000-000000000001 (demo)
--
-- Cubre todos los endpoints implementados:
--   GET  /api/v1/reports                  (lista, facets, filtros)
--   GET  /api/v1/reports/facets           (counts por genre/platform/developer/status)
--   GET  /api/v1/reports/{id}             (detalle con JSONB sections)
--   GET  /api/v1/reports/{id}/content     (markdown/json/json_rag/pdf)
--   PATCH /api/v1/reports/{id}            (tags, notes)
--   DELETE /api/v1/reports/{id}           (eliminación)
--   GET  /api/v1/games/pipeline/{id}/status
--
-- Datos cubiertos:
--   8 reports: 5 completed · 1 processing · 1 failed · 1 con PDF
--   10 analysis rows vinculadas a 2 reports (Elden Ring + Disco Elysium)
--   Géneros variados: Action RPG · RPG · Open World · Metroidvania · Roguelike
--   Plataformas variadas: PC · PS5 · Xbox · Switch · iOS
--   Desarrolladores: FromSoftware · ZA/UM · CD Projekt Red · Larian · Santa Monica
--   Tags, notas, bookmarks y view/download counts para probar PATCH y analytics
-- =============================================================

BEGIN;

-- Activar RLS para el usuario demo (requerido por las políticas de la DB)
SELECT set_config('app.current_user_id', '00000000-0000-0000-0000-000000000001', true);

-- =============================================================
-- MAPA DE UUIDs FIJOS (para reproducibilidad en pruebas)
-- =============================================================
-- USUARIO
--   demo               = 00000000-0000-0000-0000-000000000001

-- GAME IDs (game_id — referencia cruzada, no hay tabla games)
--   Elden Ring         = a1111111-1111-1111-1111-111111111111
--   Hollow Knight      = a2222222-2222-2222-2222-222222222222
--   Cyberpunk 2077     = a3333333-3333-3333-3333-333333333333
--   Baldur's Gate 3    = a4444444-4444-4444-4444-444444444444
--   God of War Ragnarök= a5555555-5555-5555-5555-555555555555
--   Dead Cells (pipe)  = a6666666-6666-6666-6666-666666666666
--   Starfield (failed) = a7777777-7777-7777-7777-777777777777
--   Disco Elysium      = a8888888-8888-8888-8888-888888888888

-- ANALYSIS IDs — Elden Ring (prefijo b)
--   design_art         = b1111111-1111-1111-1111-111111111111
--   user_experience    = b2222222-2222-2222-2222-222222222222
--   technology_systems = b3333333-3333-3333-3333-333333333333
--   strategy_market    = b4444444-4444-4444-4444-444444444444
--   synthesis          = b5555555-5555-5555-5555-555555555555

-- ANALYSIS IDs — Disco Elysium (prefijo c)
--   design_art         = c1111111-1111-1111-1111-111111111111
--   user_experience    = c2222222-2222-2222-2222-222222222222
--   technology_systems = c3333333-3333-3333-3333-333333333333
--   strategy_market    = c4444444-4444-4444-4444-444444444444
--   synthesis          = c5555555-5555-5555-5555-555555555555

-- REPORT IDs (prefijo d)
--   Elden Ring         = d1111111-1111-1111-1111-111111111111
--   Hollow Knight      = d2222222-2222-2222-2222-222222222222
--   Cyberpunk 2077     = d3333333-3333-3333-3333-333333333333
--   Baldur's Gate 3    = d4444444-4444-4444-4444-444444444444
--   God of War         = d5555555-5555-5555-5555-555555555555
--   Dead Cells (pipe)  = d6666666-6666-6666-6666-666666666666
--   Starfield (failed) = d7777777-7777-7777-7777-777777777777
--   Disco Elysium      = d8888888-8888-8888-8888-888888888888

-- =============================================================
-- PASO 1: ANALYSIS
-- (debe insertarse antes que reports porque reports.analysis_*
--  son FKs → analysis.id)
-- =============================================================

INSERT INTO analysis (
    id, user_id, game_id,
    analysis_type, status, confidence_score,
    query_params, target_game_filters, pipeline_config,
    input_data_jsonb, raw_output_jsonb, processed_output_jsonb,
    metrics_jsonb, error_details_jsonb,
    started_at, completed_at, processing_time_ms, priority
) VALUES

-- ── Elden Ring · Design & Art ─────────────────────────────────────────────
(
    'b1111111-1111-1111-1111-111111111111',
    '00000000-0000-0000-0000-000000000001',
    'a1111111-1111-1111-1111-111111111111',
    'design_art', 'completed', 0.95,
    '{"q": "Elden Ring", "sources": ["igdb", "rawg"]}',
    '{"genres": ["Action RPG"], "platforms": ["PC", "PlayStation 5"], "release_year_range": [2022, 2022]}',
    '{"skill_version": "2.1", "model": "gemini-2.5-pro", "timeout_s": 120}',
    '{"game_name": "Elden Ring", "developer": "FromSoftware", "raw_reviews": 248, "metacritic_score": 96}',
    '{"score": 9.5, "summary": "Exceptional environmental storytelling with diverse biomes", "strengths": ["World design", "Enemy art direction", "Architecture"], "weaknesses": ["Occasional visual repetition underground"]}',
    '{"score": 9.5, "tag": "World-Class Art Direction", "summary": "Six distinct biomes — each with its own architectural language and enemy faction.", "strengths": ["Breathtaking open-world vistas", "Iconic enemy designs", "Seamless lore-through-design"], "weaknesses": ["Some underground area visual repetition"]}',
    '{"data_sources": ["igdb", "rawg", "metacritic"], "reviews_processed": 248, "processing_ms": 4230, "token_usage": 18500}',
    '{}',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '10 days' + INTERVAL '5 seconds',
    4230, 8
),

-- ── Elden Ring · User Experience ──────────────────────────────────────────
(
    'b2222222-2222-2222-2222-222222222222',
    '00000000-0000-0000-0000-000000000001',
    'a1111111-1111-1111-1111-111111111111',
    'user_experience', 'completed', 0.90,
    '{"q": "Elden Ring", "sources": ["igdb", "rawg"]}',
    '{"genres": ["Action RPG"], "platforms": ["PC", "PlayStation 5"], "release_year_range": [2022, 2022]}',
    '{"skill_version": "2.1", "model": "gemini-2.5-pro", "timeout_s": 120}',
    '{"game_name": "Elden Ring", "user_review_count": 42000, "avg_playtime_h": 68}',
    '{"score": 8.8, "summary": "Minimalist UI respects player intelligence", "strengths": ["Clean HUD", "Co-op system"], "weaknesses": ["No quest markers", "High newcomer barrier"]}',
    '{"score": 8.8, "tag": "Intentional Minimalism", "summary": "Minimalist HUD defines franchise identity — polarizing but uniquely empowering.", "strengths": ["Optional HUD elements", "Organic lore discovery", "Co-op reduces difficulty spikes"], "weaknesses": ["Steep learning curve", "No map legend"]}',
    '{"data_sources": ["rawg", "steam_reviews"], "reviews_processed": 42000, "processing_ms": 5100, "token_usage": 21000}',
    '{}',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '10 days' + INTERVAL '6 seconds',
    5100, 8
),

-- ── Elden Ring · Technology & Systems ─────────────────────────────────────
(
    'b3333333-3333-3333-3333-333333333333',
    '00000000-0000-0000-0000-000000000001',
    'a1111111-1111-1111-1111-111111111111',
    'technology_systems', 'completed', 0.88,
    '{"q": "Elden Ring", "sources": ["igdb", "rawg", "steam"]}',
    '{"genres": ["Action RPG"], "platforms": ["PC", "PlayStation 5"], "release_year_range": [2022, 2022]}',
    '{"skill_version": "2.1", "model": "gemini-2.5-pro", "timeout_s": 120}',
    '{"game_name": "Elden Ring", "steam_app_id": 1245620, "pc_reviews": 280000}',
    '{"score": 9.1, "summary": "600+ weapons with unique movesets", "strengths": ["Build variety", "Online infrastructure"], "weaknesses": ["No cross-play"]}',
    '{"score": 9.1, "tag": "Deep Systems Engineering", "summary": "Hundreds of build combinations through deeply interconnected combat systems.", "strengths": ["600+ weapons with unique movesets", "Robust PvP/co-op infrastructure", "Physics-based interactions"], "weaknesses": ["No native cross-play between platforms"]}',
    '{"data_sources": ["steam", "igdb"], "reviews_processed": 280000, "processing_ms": 3900, "token_usage": 16200}',
    '{}',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '10 days' + INTERVAL '4 seconds',
    3900, 8
),

-- ── Elden Ring · Strategy & Market ────────────────────────────────────────
(
    'b4444444-4444-4444-4444-444444444444',
    '00000000-0000-0000-0000-000000000001',
    'a1111111-1111-1111-1111-111111111111',
    'strategy_market', 'completed', 0.96,
    '{"q": "Elden Ring market performance", "sources": ["igdb", "rawg"]}',
    '{"genres": ["Action RPG"], "platforms": ["PC", "PlayStation 5", "Xbox Series X"], "release_year_range": [2022, 2022]}',
    '{"skill_version": "2.1", "model": "gemini-2.5-pro", "timeout_s": 120}',
    '{"game_name": "Elden Ring", "publisher": "Bandai Namco", "launch_sales_3wk": 12000000}',
    '{"score": 9.6, "summary": "21M+ copies — FromSoftware transcended niche gaming"}',
    '{"score": 9.6, "tag": "Market Benchmark", "summary": "21M+ copies in 12 months; G.R.R. Martin collaboration drove mainstream coverage.", "strengths": ["Record FromSoftware launch", "GOTY 127+ awards", "IP collaboration expanded audience"], "weaknesses": ["No recurring revenue model at launch"]}',
    '{"data_sources": ["bandai_namco_pr", "metacritic"], "processing_ms": 2800, "token_usage": 11000}',
    '{}',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '10 days' + INTERVAL '3 seconds',
    2800, 8
),

-- ── Elden Ring · Synthesis ────────────────────────────────────────────────
(
    'b5555555-5555-5555-5555-555555555555',
    '00000000-0000-0000-0000-000000000001',
    'a1111111-1111-1111-1111-111111111111',
    'synthesis', 'completed', 0.93,
    '{"q": "Elden Ring", "synthesis": true}',
    '{"genres": ["Action RPG"], "platforms": ["PC", "PlayStation 5", "Xbox Series X"], "release_year_range": [2022, 2022]}',
    '{"skill_version": "2.1", "model": "gemini-2.5-pro", "timeout_s": 180, "input_skills": ["design_art", "user_experience", "technology_systems", "strategy_market"]}',
    '{"macro_skill_scores": {"design_art": 9.5, "user_experience": 8.8, "technology_systems": 9.1, "strategy_market": 9.6}}',
    '{"overall_score": 9.4, "tag": "GOTY 2022"}',
    '{"overall_score": 9.4, "tag": "GOTY 2022", "synthesis_complete": true, "report_ready": true}',
    '{"data_sources": ["design_art", "user_experience", "technology_systems", "strategy_market"], "processing_ms": 6700, "token_usage": 28000}',
    '{}',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '10 days' + INTERVAL '7 seconds',
    6700, 8
),

-- ── Disco Elysium · Design & Art ──────────────────────────────────────────
(
    'c1111111-1111-1111-1111-111111111111',
    '00000000-0000-0000-0000-000000000001',
    'a8888888-8888-8888-8888-888888888888',
    'design_art', 'completed', 0.94,
    '{"q": "Disco Elysium", "sources": ["igdb", "rawg"]}',
    '{"genres": ["RPG"], "platforms": ["PC"], "release_year_range": [2019, 2019]}',
    '{"skill_version": "2.1", "model": "gemini-2.5-pro", "timeout_s": 120}',
    '{"game_name": "Disco Elysium", "developer": "ZA/UM", "art_style": "painterly expressionist"}',
    '{"score": 9.6, "summary": "1920s European expressionist art — unique in the medium"}',
    '{"score": 9.6, "tag": "Expressionist Masterwork", "summary": "Disco Elysium''s painterly style is singular in the medium.", "strengths": ["Unique hand-painted environments", "Expressive character design through clothing and posture", "Emotional palette use"], "weaknesses": ["Most of the game takes place in one district"]}',
    '{"data_sources": ["igdb", "rawg"], "reviews_processed": 1200, "processing_ms": 3100, "token_usage": 13000}',
    '{}',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days' + INTERVAL '4 seconds',
    3100, 7
),

-- ── Disco Elysium · User Experience ───────────────────────────────────────
(
    'c2222222-2222-2222-2222-222222222222',
    '00000000-0000-0000-0000-000000000001',
    'a8888888-8888-8888-8888-888888888888',
    'user_experience', 'completed', 0.97,
    '{"q": "Disco Elysium", "sources": ["rawg", "steam"]}',
    '{"genres": ["RPG"], "platforms": ["PC"], "release_year_range": [2019, 2019]}',
    '{"skill_version": "2.1", "model": "gemini-2.5-pro", "timeout_s": 120}',
    '{"game_name": "Disco Elysium", "steam_reviews_positive_pct": 97}',
    '{"score": 9.9, "summary": "The finest writing in video game history"}',
    '{"score": 9.9, "tag": "Writing Pinnacle", "summary": "Dozens of distinct skill voices create a genuine internal chorus; no combat — pure dialogue.", "strengths": ["Failure states produce interesting content", "Skill voices feel like real characters", "No dead ends — every path is authored"], "weaknesses": ["Absence of traditional RPG combat alienates genre fans"]}',
    '{"data_sources": ["steam", "rawg"], "reviews_processed": 89000, "processing_ms": 5200, "token_usage": 24000}',
    '{}',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days' + INTERVAL '6 seconds',
    5200, 7
),

-- ── Disco Elysium · Technology & Systems ──────────────────────────────────
(
    'c3333333-3333-3333-3333-333333333333',
    '00000000-0000-0000-0000-000000000001',
    'a8888888-8888-8888-8888-888888888888',
    'technology_systems', 'completed', 0.86,
    '{"q": "Disco Elysium", "sources": ["igdb", "steam"]}',
    '{"genres": ["RPG"], "platforms": ["PC"], "release_year_range": [2019, 2019]}',
    '{"skill_version": "2.1", "model": "gemini-2.5-pro", "timeout_s": 120}',
    '{"game_name": "Disco Elysium", "engine": "custom Unity-based"}',
    '{"score": 8.5, "summary": "Custom RPG engine prioritizing dialogue over action"}',
    '{"score": 8.5, "tag": "Narrative Engine", "summary": "Bespoke RPG engine that prioritizes dialogue systems over action with unpredictable skill checks.", "strengths": ["Unpredictable skill-check outcomes", "Full voice acting in Final Cut", "Branch-safe save system"], "weaknesses": ["Switch port had significant performance issues"]}',
    '{"data_sources": ["steam", "igdb"], "reviews_processed": 5000, "processing_ms": 2900, "token_usage": 10500}',
    '{}',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days' + INTERVAL '3 seconds',
    2900, 7
),

-- ── Disco Elysium · Strategy & Market ─────────────────────────────────────
(
    'c4444444-4444-4444-4444-444444444444',
    '00000000-0000-0000-0000-000000000001',
    'a8888888-8888-8888-8888-888888888888',
    'strategy_market', 'completed', 0.92,
    '{"q": "Disco Elysium ZA/UM market analysis"}',
    '{"genres": ["RPG"], "platforms": ["PC"], "release_year_range": [2019, 2019]}',
    '{"skill_version": "2.1", "model": "gemini-2.5-pro", "timeout_s": 120}',
    '{"game_name": "Disco Elysium", "price": 39.99, "awards_won": 5}',
    '{"score": 9.4, "summary": "Won Game Awards GOTY 2019 — redefined RPG storytelling commercially"}',
    '{"score": 9.4, "tag": "Critical Phenomenon", "summary": "GOTY + Narrative + RPG triple crown at Game Awards 2019 from a first-time studio.", "strengths": ["Won 3 Game Awards 2019 simultaneously", "1M+ copies at $39.99", "Unprecedented critical acclaim for debut studio"], "weaknesses": ["ZA/UM implosion removed all sequel potential"]}',
    '{"data_sources": ["igdb", "steam"], "processing_ms": 2200, "token_usage": 8800}',
    '{}',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days' + INTERVAL '3 seconds',
    2200, 7
),

-- ── Disco Elysium · Synthesis ─────────────────────────────────────────────
(
    'c5555555-5555-5555-5555-555555555555',
    '00000000-0000-0000-0000-000000000001',
    'a8888888-8888-8888-8888-888888888888',
    'synthesis', 'completed', 0.94,
    '{"q": "Disco Elysium", "synthesis": true}',
    '{"genres": ["RPG"], "platforms": ["PC"], "release_year_range": [2019, 2019]}',
    '{"skill_version": "2.1", "model": "gemini-2.5-pro", "timeout_s": 180, "input_skills": ["design_art", "user_experience", "technology_systems", "strategy_market"]}',
    '{"macro_skill_scores": {"design_art": 9.6, "user_experience": 9.9, "technology_systems": 8.5, "strategy_market": 9.4}}',
    '{"overall_score": 9.5, "tag": "Genre-Defining"}',
    '{"overall_score": 9.5, "tag": "Genre-Defining", "synthesis_complete": true, "report_ready": true}',
    '{"data_sources": ["design_art", "user_experience", "technology_systems", "strategy_market"], "processing_ms": 7100, "token_usage": 30000}',
    '{}',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days' + INTERVAL '8 seconds',
    7100, 7
)
ON CONFLICT (id) DO NOTHING;

-- =============================================================
-- PASO 2: REPORTS
-- =============================================================

INSERT INTO reports (
    id, user_id, game_id,
    game_name, game_slug, developer_name, release_year,
    primary_genre, all_genres,
    primary_platform, all_platforms,
    report_status, report_type, confidence_score,
    search_query, tags,
    current_phase, pipeline_progress,
    cover_url,
    created_at, updated_at, completed_at,
    markdown_content, markdown_summary,
    url_json, url_json_rag, url_markdown, url_pdf,
    json_generated, markdown_generated, pdf_generated, json_rag_generated,
    processing_time_ms,
    report_metadata_jsonb,
    executive_summary_jsonb,
    thematic_analysis_jsonb,
    strategic_recommendations_jsonb,
    risk_assessment_jsonb,
    game_data_jsonb,
    pipeline_data_jsonb,
    user_metadata_jsonb,
    analysis_design_art,
    analysis_user_experience,
    analysis_technology_systems,
    analysis_strategy_market,
    analysis_synthesis
) VALUES

-- ═════════════════════════════════════════════════════════════
-- 1. ELDEN RING — completed · full content · linked analysis
--    Prueba: detalle JSONB · markdown download · analysis FKs
-- ═════════════════════════════════════════════════════════════
(
    'd1111111-1111-1111-1111-111111111111',
    '00000000-0000-0000-0000-000000000001',
    'a1111111-1111-1111-1111-111111111111',
    'Elden Ring', 'elden-ring', 'FromSoftware', 2022,
    'Action RPG',
    ARRAY['Action RPG', 'RPG', 'Adventure'],
    'PC',
    ARRAY['PC', 'PlayStation 5', 'Xbox Series X', 'PlayStation 4', 'Xbox One'],
    'completed', 'comprehensive', 0.93,
    'Elden Ring FromSoftware open world action RPG 2022',
    ARRAY['souls-like', 'open-world', 'fromsoftware', 'goty-2022'],
    'synthesis', 100,
    'https://media.rawg.io/media/games/b29/b294fad322b74c38f4c6dbbe2c54699c.jpg',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '10 days' + INTERVAL '30 seconds',
    NOW() - INTERVAL '10 days' + INTERVAL '30 seconds',

    -- markdown_content — prueba GET /content?format=markdown
    $md$# Elden Ring — GetSmart Market Intelligence Report

## Executive Summary

Elden Ring represents a watershed moment in the action-RPG genre. FromSoftware's collaboration with George R.R. Martin produced a world of unparalleled depth that simultaneously appealed to veteran Souls fans and a mainstream global audience. 21M+ copies in 12 months. Metacritic 96.

## Design & Art · 9.5

Six distinct biomes each with unique architectural language and enemy factions. Environmental storytelling replaces explicit narrative delivery.

**Strengths:** Breathtaking vistas · iconic boss designs · lore through design.
**Weaknesses:** Some underground visual repetition.

## User Experience · 8.8

Intentionally minimalist UI defines the franchise. No quest markers. Discovery-driven design polarizes audiences but creates unique agency.

**Strengths:** Optional HUD · organic lore discovery · co-op reduces spikes.
**Weaknesses:** No quest markers · steep newcomer barrier.

## Technology & Systems · 9.1

600+ weapons with unique movesets. Hundreds of viable build paths. Physics-based combat interactions reward mastery across hundreds of hours.

**Strengths:** Deep build variety · robust PvP/co-op · physics combat.
**Weaknesses:** No native cross-play.

## Strategy & Market · 9.6

| Metric | Value |
|---|---|
| Copies Sold | 21M+ in 12 months |
| Metacritic | 96/100 |
| Revenue Est. | $1.5B+ |
| GOTY Awards | 127+ |

## Strategic Recommendations

1. Monitor open-world competitors (TotK, Horizon) for design response.
2. DLC (Shadow of the Erdtree) should expand lore depth over difficulty loops.
3. Explore cross-media IP — G.R.R. Martin collaboration as template.

## Risk Assessment

- **High:** Souls-like sub-genre saturation (15+ competitors 2022-2024).
- **Medium:** Player burnout on difficulty as primary selling point.
- **Low:** Console exclusivity pressure.
$md$,

    'Elden Ring — 21M+ copies, 96 Metacritic, 127+ GOTY awards. Redefined action-RPG open-world design and FromSoftware''s commercial ceiling.',

    '/api/v1/reports/d1111111-1111-1111-1111-111111111111/content?format=json',
    '/api/v1/reports/d1111111-1111-1111-1111-111111111111/content?format=json_rag',
    '/api/v1/reports/d1111111-1111-1111-1111-111111111111/content?format=markdown',
    '/api/v1/reports/d1111111-1111-1111-1111-111111111111/content?format=pdf',
    TRUE, TRUE, FALSE, TRUE,
    22730,

    '{"pipeline_version": "3.0.0", "synthesis_model": "gemini-2.5-pro", "schema_version": "1.0", "input_skills": ["design_art", "user_experience", "technology_systems", "strategy_market"], "generated_at": "2026-06-16T10:00:00Z"}',

    '{"game_identity": "Elden Ring — FromSoftware open-world action RPG with George R.R. Martin world-building", "market_position": "21M+ copies in 12 months; 96 Metacritic; category-defining launch", "key_insights": ["Successfully mainstreamed challenging gameplay to a global audience", "First FromSoftware title with true open-world design", "G.R.R. Martin collaboration drove mainstream media coverage beyond gaming press"], "critical_risks": ["Souls-like market saturation from competitors", "Player burnout on high-difficulty formula"], "recommended_actions": ["Monitor open-world competitor design responses", "Use DLC to expand lore depth rather than recycle difficulty loops"], "overall_confidence": 0.93, "overall_score": 9.4, "tag": "GOTY 2022"}',

    '{"design_art": {"score": 9.5, "tag": "World-Class Art Direction", "summary": "Six biomes with distinct visual languages; lore communicated through environment."}, "user_experience": {"score": 8.8, "tag": "Intentional Minimalism", "summary": "Minimalist HUD creates discovery-driven tension — controversial but franchise-defining."}, "technology_systems": {"score": 9.1, "tag": "Deep Systems Engineering", "summary": "600+ weapons, hundreds of build paths, physics-based combat interactions."}, "strategy_market": {"score": 9.6, "tag": "Market Benchmark", "summary": "21M+ copies; 127+ GOTY awards; FromSoftware achieved mainstream recognition."}}',

    '{"short_term": ["Release Shadow of the Erdtree with meaningful lore expansion", "Improve PC port for DLSS/frame-gen support"], "long_term": ["Explore cross-media IP expansion (animated series, tabletop)", "Consider co-op focused title given multiplayer engagement metrics"], "market_opportunities": ["Asian market crossover with JRPG audience", "Speedrunning community as organic free marketing"]}',

    '{"high": ["Souls-like genre saturation — 15+ competitors launched 2022-2024"], "medium": ["Player fatigue on difficulty as core selling point", "PC optimization reputation from Dark Souls II era"], "low": ["Console exclusivity pressure from PlayStation"], "mitigation": ["Diversify catalogue with Armored Core VI", "Invest in better PC launch QA pipeline"]}',

    '{"igdb_id": "119133", "rawg_id": "452638", "steam_app_id": "1245620", "metacritic": 96, "launch_sales_3wk": 12000000, "lifetime_sales": 21000000, "publisher": "Bandai Namco Entertainment", "release_date": "2022-02-25"}',

    '{"phases": {"scraping": {"status": "completed", "duration_ms": 8200}, "analysis": {"status": "completed", "duration_ms": 16030}, "synthesis": {"status": "completed", "duration_ms": 6700}, "storage": {"status": "completed", "duration_ms": 830}}, "total_tokens": 93700}',

    '{"user_rating": null, "user_notes": null, "bookmarked": false}',

    'b1111111-1111-1111-1111-111111111111',
    'b2222222-2222-2222-2222-222222222222',
    'b3333333-3333-3333-3333-333333333333',
    'b4444444-4444-4444-4444-444444444444',
    'b5555555-5555-5555-5555-555555555555'
),

-- ═════════════════════════════════════════════════════════════
-- 2. HOLLOW KNIGHT — completed · indie · Switch platform
--    Prueba: filtro por plataforma Switch · géneros Metroidvania
-- ═════════════════════════════════════════════════════════════
(
    'd2222222-2222-2222-2222-222222222222',
    '00000000-0000-0000-0000-000000000001',
    'a2222222-2222-2222-2222-222222222222',
    'Hollow Knight', 'hollow-knight', 'Team Cherry', 2017,
    'Metroidvania',
    ARRAY['Metroidvania', 'Platformer', 'Indie', 'Action'],
    'PC',
    ARRAY['PC', 'PlayStation 4', 'Xbox One', 'Nintendo Switch'],
    'completed', 'comprehensive', 0.91,
    'Hollow Knight Team Cherry indie Metroidvania 2017',
    ARRAY['indie', 'metroidvania', 'hand-drawn', 'team-cherry'],
    'synthesis', 100,
    'https://media.rawg.io/media/games/4cf/4cfc6b7f1850590a4634b08bfab308ab.jpg',
    NOW() - INTERVAL '8 days',
    NOW() - INTERVAL '8 days' + INTERVAL '22 seconds',
    NOW() - INTERVAL '8 days' + INTERVAL '22 seconds',

    $md$# Hollow Knight — GetSmart Market Intelligence Report

## Executive Summary

Hollow Knight is arguably the finest indie game ever made — a Metroidvania of astonishing scale and melancholic beauty built by a team of three people on a $57,000 Kickstarter budget. 6M+ copies sold at $15 redefined what independent studios could achieve commercially and artistically.

| Metric | Value |
|---|---|
| Copies Sold | 6M+ |
| Budget | $57,000 Kickstarter |
| Price | $14.99 |
| Metacritic | 90/100 |
$md$,

    'Hollow Knight — 6M+ copies at $15 by a 3-person team. Defined Metroidvania genre quality for a generation.',

    '/api/v1/reports/d2222222-2222-2222-2222-222222222222/content?format=json',
    '/api/v1/reports/d2222222-2222-2222-2222-222222222222/content?format=json_rag',
    '/api/v1/reports/d2222222-2222-2222-2222-222222222222/content?format=markdown',
    NULL,
    TRUE, TRUE, FALSE, TRUE,
    18400,

    '{"pipeline_version": "3.0.0", "synthesis_model": "gemini-2.5-pro", "schema_version": "1.0"}',

    '{"game_identity": "Hollow Knight — hand-drawn Metroidvania by 3-person Team Cherry, $57K Kickstarter", "market_position": "Benchmark indie title; 6M+ copies at $15", "key_insights": ["Proved indie studios can match AAA quality at 1/1000th the budget", "Four free DLC packs extended lifespan significantly", "Silksong anticipation sustains community engagement 7+ years later"], "overall_score": 9.1, "tag": "Indie Pinnacle"}',

    '{"design_art": {"score": 9.8, "tag": "Hand-Drawn Masterwork", "summary": "5000+ frames of unique animation; each area with distinct emotional palette."}, "user_experience": {"score": 9.0, "tag": "Exploration-First Design", "summary": "Map-purchase mechanic rewards curiosity; charm system enables deep build customization."}, "technology_systems": {"score": 9.2, "tag": "Unity Perfected", "summary": "Stable 60fps on all platforms; four free DLC packs; seamless loading disguised by gates."}, "strategy_market": {"score": 9.5, "tag": "Indie Commercial Benchmark", "summary": "6M+ copies at $15 by 3 developers — the single greatest ROI story in indie gaming."}}',

    '{"short_term": ["Release Silksong to capitalize on 7+ years of anticipation"], "long_term": ["Animated series or graphic novel given the rich lore depth"]}',

    '{"high": ["Silksong delays eroding community goodwill and goodwill capital"], "low": ["No direct Metroidvania competitor at this quality tier"]}',

    '{"rawg_id": "617", "metacritic": 90, "launch_price": 14.99, "lifetime_sales": 6000000, "developer_size": 3, "kickstarter_budget": 57000}',

    '{"phases": {"scraping": {"status": "completed"}, "analysis": {"status": "completed"}, "synthesis": {"status": "completed"}, "storage": {"status": "completed"}}}',

    '{"user_rating": null, "user_notes": null, "bookmarked": false}',
    NULL, NULL, NULL, NULL, NULL
),

-- ═════════════════════════════════════════════════════════════
-- 3. CYBERPUNK 2077 — completed · bookmarked · user_notes
--    Prueba: PATCH tags/notes · filtro developer CD Projekt Red
-- ═════════════════════════════════════════════════════════════
(
    'd3333333-3333-3333-3333-333333333333',
    '00000000-0000-0000-0000-000000000001',
    'a3333333-3333-3333-3333-333333333333',
    'Cyberpunk 2077', 'cyberpunk-2077', 'CD Projekt Red', 2020,
    'Open World',
    ARRAY['Open World', 'RPG', 'Action', 'Sci-Fi'],
    'PC',
    ARRAY['PC', 'PlayStation 5', 'Xbox Series X', 'PlayStation 4', 'Xbox One'],
    'completed', 'comprehensive', 0.84,
    'Cyberpunk 2077 CD Projekt Red launch comeback brand recovery',
    ARRAY['open-world', 'sci-fi', 'comeback', 'cdpr', 'phantom-liberty'],
    'synthesis', 100,
    'https://media.rawg.io/media/games/26d/26d4437715bee60138dab4a7c8c59c92.jpg',
    NOW() - INTERVAL '15 days',
    NOW() - INTERVAL '15 days' + INTERVAL '27 seconds',
    NOW() - INTERVAL '15 days' + INTERVAL '27 seconds',

    $md$# Cyberpunk 2077 — GetSmart Market Intelligence Report

## Executive Summary

Cyberpunk 2077 is gaming's greatest comeback story. A catastrophic launch was followed by a 3-year redemption arc — the 2.0 overhaul rebuilt core systems from scratch, and Phantom Liberty proved the IP still had commercial momentum.

| Metric | Value |
|---|---|
| Pre-orders | 13M (record at release) |
| Lifetime Sales | 25M+ |
| Metacritic PC | 86/100 |
| Peak Steam (2.0) | 1M concurrent |
$md$,

    'Cyberpunk 2077 — 25M lifetime sales; gaming''s greatest comeback via 2.0 overhaul and Phantom Liberty after a catastrophic launch.',

    '/api/v1/reports/d3333333-3333-3333-3333-333333333333/content?format=json',
    '/api/v1/reports/d3333333-3333-3333-3333-333333333333/content?format=json_rag',
    '/api/v1/reports/d3333333-3333-3333-3333-333333333333/content?format=markdown',
    NULL,
    TRUE, TRUE, FALSE, TRUE,
    19800,

    '{"pipeline_version": "3.0.0", "synthesis_model": "gemini-2.5-pro", "schema_version": "1.0"}',

    '{"game_identity": "Cyberpunk 2077 — CD Projekt Red open-world RPG in Night City", "market_position": "25M+ lifetime sales after launch crisis and 2.0 brand recovery", "key_insights": ["Edgerunners anime reversed community sentiment in 2022", "2.0 overhaul rebuilt police AI and skill trees from scratch", "Phantom Liberty DLC achieved standalone critical acclaim"], "overall_score": 8.1, "tag": "Comeback Story"}',

    '{"design_art": {"score": 9.3, "tag": "Night City Artistic Triumph"}, "user_experience": {"score": 7.4, "tag": "Post-2.0 Significant Improvement"}, "technology_systems": {"score": 8.0, "tag": "REDengine Recovery"}, "strategy_market": {"score": 7.9, "tag": "Brand Redemption Arc"}}',

    '{"short_term": ["Maintain patch cadence to sustain 2.0 goodwill"], "long_term": ["Sequel must nail launch quality — no second comeback possible"]}',

    '{"high": ["Launch crisis destroyed trust — brand repair is a multi-year project"], "medium": ["REDengine limits on last-gen still erode perception"], "low": ["Open-world RPG market competition"]}',

    '{"rawg_id": "41494", "steam_app_id": "1091500", "metacritic_pc": 86, "preorders": 13000000, "lifetime_sales": 25000000}',

    '{"phases": {"scraping": {"status": "completed"}, "analysis": {"status": "completed"}, "synthesis": {"status": "completed"}, "storage": {"status": "completed"}}}',

    '{"user_rating": 4, "user_notes": "Great comeback story — excellent case study for brand recovery after launch crisis.", "bookmarked": true}',
    NULL, NULL, NULL, NULL, NULL
),

-- ═════════════════════════════════════════════════════════════
-- 4. BALDUR'S GATE 3 — completed · highest confidence · PDF
--    Prueba: pdf_generated=TRUE · filtro año 2023 · co-op tag
-- ═════════════════════════════════════════════════════════════
(
    'd4444444-4444-4444-4444-444444444444',
    '00000000-0000-0000-0000-000000000001',
    'a4444444-4444-4444-4444-444444444444',
    'Baldur''s Gate 3', 'baldurs-gate-3', 'Larian Studios', 2023,
    'RPG',
    ARRAY['RPG', 'Strategy', 'Adventure', 'Co-op'],
    'PC',
    ARRAY['PC', 'PlayStation 5', 'Xbox Series X'],
    'completed', 'comprehensive', 0.97,
    'Baldurs Gate 3 Larian Studios DnD CRPG 2023 GOTY',
    ARRAY['crpg', 'dnd-5e', 'co-op', 'larian', 'goty-2023'],
    'synthesis', 100,
    'https://media.rawg.io/media/games/699/69907ecf13f172e9e144069769c3be73.jpg',
    NOW() - INTERVAL '20 days',
    NOW() - INTERVAL '20 days' + INTERVAL '35 seconds',
    NOW() - INTERVAL '20 days' + INTERVAL '35 seconds',

    $md$# Baldur's Gate 3 — GetSmart Market Intelligence Report

## Executive Summary

Baldur's Gate 3 is the most ambitious RPG ever shipped — 200+ hours of genuinely reactive storytelling with D&D 5e mechanics translated perfectly to the medium. 10M+ copies in year one proved that quality-first development can outperform live-service models even in 2023.

| Metric | Value |
|---|---|
| Year-One Sales | 10M+ |
| Metacritic | 96/100 |
| Peak Steam | 875,343 concurrent |
| GOTY Awards | 50+ |
$md$,

    'Baldur''s Gate 3 — 10M+ copies year one; redefined premium RPG expectations; 50+ GOTY awards.',

    '/api/v1/reports/d4444444-4444-4444-4444-444444444444/content?format=json',
    '/api/v1/reports/d4444444-4444-4444-4444-444444444444/content?format=json_rag',
    '/api/v1/reports/d4444444-4444-4444-4444-444444444444/content?format=markdown',
    '/api/v1/reports/d4444444-4444-4444-4444-444444444444/content?format=pdf',
    TRUE, TRUE, TRUE, TRUE,
    24100,

    '{"pipeline_version": "3.0.0", "synthesis_model": "gemini-2.5-pro", "schema_version": "1.0"}',

    '{"game_identity": "Baldur''s Gate 3 — Larian Studios'' D&D 5e mega-RPG with 200+ hours of reactive content", "market_position": "10M+ copies year one; 50+ GOTY awards; raised bar for premium RPG", "key_insights": ["Early access strategy built community and refined design simultaneously", "Split-screen co-op is technically unprecedented at this scope", "D&D 5e IP drove tabletop crossover audience to mainstream PC gaming"], "overall_score": 9.6, "tag": "Definitive RPG 2023"}',

    '{"design_art": {"score": 9.5, "tag": "Film-Quality Production", "summary": "Jaw-dropping cutscenes; each companion has a fully realized visual arc."}, "user_experience": {"score": 9.7, "tag": "Best-in-Class Player Agency", "summary": "Every choice creates genuine ripples; companion relationships feel deeply alive."}, "technology_systems": {"score": 9.3, "tag": "Technical Masterwork", "summary": "Fully simulated physics; flawless split-screen co-op; massive scope zero compromise."}, "strategy_market": {"score": 9.8, "tag": "Premium RPG Benchmark", "summary": "10M+ copies; redefined commercial expectations for premium RPGs in live-service era."}}',

    '{"short_term": ["Release expansion content given massive player investment"], "long_term": ["Establish Larian as permanent AAA-tier studio through next original IP"]}',

    '{"high": ["No DLC announced despite demand — player expectation risk building"], "medium": ["D&D 5e IP dependency on Wizards of the Coast licensing"], "low": ["Market fatigue on long-form RPGs"]}',

    '{"rawg_id": "452630", "steam_app_id": "1086940", "metacritic": 96, "year_one_sales": 10000000, "peak_steam_players": 875343}',

    '{"phases": {"scraping": {"status": "completed"}, "analysis": {"status": "completed"}, "synthesis": {"status": "completed"}, "storage": {"status": "completed"}}}',

    '{"user_rating": 5, "user_notes": "Best RPG since Planescape Torment. Set a new standard.", "bookmarked": true}',
    NULL, NULL, NULL, NULL, NULL
),

-- ═════════════════════════════════════════════════════════════
-- 5. GOD OF WAR RAGNARÖK — completed · PlayStation primary
--    Prueba: filtro primary_platform PlayStation 5 · Action Adventure
-- ═════════════════════════════════════════════════════════════
(
    'd5555555-5555-5555-5555-555555555555',
    '00000000-0000-0000-0000-000000000001',
    'a5555555-5555-5555-5555-555555555555',
    'God of War Ragnarök', 'god-of-war-ragnarok', 'Santa Monica Studio', 2022,
    'Action Adventure',
    ARRAY['Action Adventure', 'Action', 'Mythology'],
    'PlayStation 5',
    ARRAY['PlayStation 5', 'PlayStation 4', 'PC'],
    'completed', 'comprehensive', 0.92,
    'God of War Ragnarok Sony Santa Monica PS5 exclusive 2022',
    ARRAY['sony', 'playstation', 'norse-mythology', 'cinematic', 'accessibility'],
    'synthesis', 100,
    'https://media.rawg.io/media/games/0cd/0cdf9d61de5e285b79b5d23e9f4f487d.jpg',
    NOW() - INTERVAL '12 days',
    NOW() - INTERVAL '12 days' + INTERVAL '26 seconds',
    NOW() - INTERVAL '12 days' + INTERVAL '26 seconds',

    $md$# God of War Ragnarök — GetSmart Market Intelligence Report

## Executive Summary

God of War Ragnarök is Santa Monica Studio's crowning achievement — a cinematic spectacle delivering across all Nine Realms. 11M copies in week one and 259 GOTY nominations established new benchmarks for PlayStation exclusives.

| Metric | Value |
|---|---|
| Week-1 Sales | 11M |
| GOTY Nominations | 259 |
| Metacritic | 94/100 |
| Accessibility Options | 59 |
$md$,

    'God of War Ragnarök — 11M copies week one; 259 GOTY nominations; cinematic action game benchmark.',

    '/api/v1/reports/d5555555-5555-5555-5555-555555555555/content?format=json',
    '/api/v1/reports/d5555555-5555-5555-5555-555555555555/content?format=json_rag',
    '/api/v1/reports/d5555555-5555-5555-5555-555555555555/content?format=markdown',
    NULL,
    TRUE, TRUE, FALSE, TRUE,
    21300,

    '{"pipeline_version": "3.0.0", "synthesis_model": "gemini-2.5-pro", "schema_version": "1.0"}',

    '{"game_identity": "God of War Ragnarök — Sony Santa Monica Norse trilogy conclusion across Nine Realms", "market_position": "11M copies week one; highest-selling PlayStation exclusive at launch", "key_insights": ["DualSense haptic integration set new industry standard", "59 accessibility settings made it most accessible AAA action game", "PC port extended commercial lifecycle by 18+ months"], "overall_score": 9.2, "tag": "Cinematic Excellence"}',

    '{"design_art": {"score": 9.5, "tag": "Nine Realms Visual Mastery"}, "user_experience": {"score": 9.0, "tag": "59 Accessibility Settings Industry-Leading"}, "technology_systems": {"score": 9.1, "tag": "DualSense Showcase"}, "strategy_market": {"score": 9.2, "tag": "PlayStation Commercial Benchmark"}}',

    '{"short_term": ["Optimize PC port for wider audience discovery"], "long_term": ["New IP or Greek-era continuation — Norse arc fully resolved"]}',

    '{"high": ["Franchise conclusion limits direct sequel potential"], "medium": ["PS4 version compromised visual ambition"], "low": ["Competition from other cinematic action titles"]}',

    '{"rawg_id": "452636", "metacritic": 94, "week_one_sales": 11000000, "goty_nominations": 259, "accessibility_options": 59}',

    '{"phases": {"scraping": {"status": "completed"}, "analysis": {"status": "completed"}, "synthesis": {"status": "completed"}, "storage": {"status": "completed"}}}',

    '{"user_rating": null, "user_notes": null, "bookmarked": false}',
    NULL, NULL, NULL, NULL, NULL
),

-- ═════════════════════════════════════════════════════════════
-- 6. DEAD CELLS — PROCESSING (en pipeline, fase Analysis 42%)
--    Prueba: tarjeta "In Pipeline" · current_phase · progress
-- ═════════════════════════════════════════════════════════════
(
    'd6666666-6666-6666-6666-666666666666',
    '00000000-0000-0000-0000-000000000001',
    'a6666666-6666-6666-6666-666666666666',
    'Dead Cells', 'dead-cells', 'Motion Twin', 2018,
    'Roguelike',
    ARRAY['Roguelike', 'Metroidvania', 'Action', 'Indie'],
    'PC',
    ARRAY['PC', 'PlayStation 4', 'Xbox One', 'Nintendo Switch', 'iOS', 'Android'],
    'processing', 'comprehensive', NULL,
    'Dead Cells Motion Twin roguelike metroidvania 2018',
    ARRAY['roguelike', 'indie', 'motion-twin', 'action'],
    'analysis', 42,
    'https://media.rawg.io/media/games/588/588c6bdff3d4baf66ec36b1c05b793bf.jpg',
    NOW() - INTERVAL '2 hours',
    NOW() - INTERVAL '2 hours',
    NULL,

    NULL, NULL,
    NULL, NULL, NULL, NULL,
    FALSE, FALSE, FALSE, FALSE,
    NULL,

    '{"pipeline_version": "3.0.0", "schema_version": "1.0"}',
    '{}', '{}', '{}', '{}',

    '{"rawg_id": "3272", "steam_app_id": "588650", "metacritic": 89}',

    '{"phases": {"scraping": {"status": "completed", "duration_ms": 7200}, "analysis": {"status": "processing", "progress": 42, "current_skill": "user_experience"}, "synthesis": {"status": "queued"}, "storage": {"status": "queued"}}}',

    '{"user_rating": null, "user_notes": null, "bookmarked": false}',
    NULL, NULL, NULL, NULL, NULL
),

-- ═════════════════════════════════════════════════════════════
-- 7. STARFIELD — FAILED · report_type error
--    Prueba: status=failed en filtro · tarjeta con error state
-- ═════════════════════════════════════════════════════════════
(
    'd7777777-7777-7777-7777-777777777777',
    '00000000-0000-0000-0000-000000000001',
    'a7777777-7777-7777-7777-777777777777',
    'Starfield', 'starfield', 'Bethesda Game Studios', 2023,
    'Open World',
    ARRAY['Open World', 'RPG', 'Sci-Fi', 'Space'],
    'PC',
    ARRAY['PC', 'Xbox Series X', 'Xbox Series S'],
    'failed', 'error', NULL,
    'Starfield Bethesda space RPG 2023 Xbox exclusive',
    ARRAY['bethesda', 'xbox-exclusive', 'space-exploration'],
    NULL, 0,
    'https://media.rawg.io/media/games/b89/b89f7c7e3fba02a8905f79ec2fe5cd42.jpg',
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '3 days' + INTERVAL '13 seconds',
    NULL,

    NULL, NULL,
    NULL, NULL, NULL, NULL,
    FALSE, FALSE, FALSE, FALSE,
    NULL,

    '{"pipeline_version": "3.0.0", "schema_version": "1.0"}',
    '{}', '{}', '{}', '{}',

    '{"rawg_id": "452637", "steam_app_id": "1716740", "metacritic": 83}',

    '{"phases": {"scraping": {"status": "completed", "duration_ms": 5400}, "analysis": {"status": "failed", "error": "Timeout after 120s — RAWG review data returned empty for game_id 452637 in this region"}}, "error": "Analysis phase timeout on user_experience skill"}',

    '{"user_rating": null, "user_notes": null, "bookmarked": false}',
    NULL, NULL, NULL, NULL, NULL
),

-- ═════════════════════════════════════════════════════════════
-- 8. DISCO ELYSIUM — completed · full JSONB · linked analysis
--    Prueba: detalle JSONB completo · PDF download · analysis FKs
--            DELETE endpoint (usar este ID en pruebas de DELETE)
-- ═════════════════════════════════════════════════════════════
(
    'd8888888-8888-8888-8888-888888888888',
    '00000000-0000-0000-0000-000000000001',
    'a8888888-8888-8888-8888-888888888888',
    'Disco Elysium', 'disco-elysium', 'ZA/UM', 2019,
    'RPG',
    ARRAY['RPG', 'Adventure', 'Narrative', 'Indie'],
    'PC',
    ARRAY['PC', 'PlayStation 5', 'PlayStation 4', 'Xbox One', 'iOS'],
    'completed', 'comprehensive', 0.95,
    'Disco Elysium ZA/UM narrative RPG GOTY 2019 political',
    ARRAY['narrative', 'dialogue-rpg', 'zaum', 'goty-2019', 'political-philosophy'],
    'synthesis', 100,
    'https://media.rawg.io/media/games/39e/39e7ec65e2697fcb98cf5c4e83ad1871.jpg',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 days' + INTERVAL '20 seconds',
    NOW() - INTERVAL '5 days' + INTERVAL '20 seconds',

    $md$# Disco Elysium — GetSmart Market Intelligence Report

## Executive Summary

Disco Elysium is the most fully realized dialogue-focused RPG ever made. Every sentence is authored with literary intent. The political philosophy it explores is more sophisticated than most published novels. ZA/UM won GOTY + Best Narrative + Best RPG at the 2019 Game Awards simultaneously — a feat never repeated by any studio.

## Design & Art · 9.6

A painterly visual style evoking 1920s European expressionist art — entirely unique in the medium. Character design expresses personality through clothing and posture with extraordinary precision.

**Strengths:** Unique hand-painted environments · expressive character design through clothing and posture · emotional palette communication.
**Weaknesses:** Most of the game takes place in one district.

## User Experience · 9.9

Dozens of distinct skill voices create a genuine internal chorus. No combat — pure dialogue and skill checks resolve all conflict. Failure states often produce more interesting content than success.

**Strengths:** Failure states produce interesting content · no dead ends — every path is authored · skill voices feel like real characters.
**Weaknesses:** Absence of traditional RPG systems alienates genre fans.

## Technology & Systems · 8.5

ZA/UM built a new RPG engine prioritizing dialogue systems over action. Full voice acting added in the Final Cut update elevated the experience significantly.

**Strengths:** Unpredictable skill checks · full VO in Final Cut · branch-safe saves.
**Weaknesses:** Switch port had significant performance issues.

## Strategy & Market · 9.4

| Metric | Value |
|---|---|
| Copies Sold | 1M+ |
| Price | $39.99 |
| Metacritic | 97/100 |
| Game Awards 2019 | GOTY + Narrative + RPG |

## Strategic Recommendations

1. Final Cut is the definitive version — all distribution should point here.
2. Studio situation: ZA/UM implosion removed all sequel potential.
3. Long-tail Steam sale cycles will sustain discovery indefinitely.

## Risk Assessment

- **High:** Studio collapse removed all sequel and franchise potential.
- **Medium:** IP ownership dispute between ZA/UM and original creators.
- **Low:** Market niche for dialogue-only RPG is inherently limited.
$md$,

    'Disco Elysium — 2019 Game Awards triple crown (GOTY + Narrative + RPG); finest dialogue RPG ever made; 1M+ at $40 from a first-time studio.',

    '/api/v1/reports/d8888888-8888-8888-8888-888888888888/content?format=json',
    '/api/v1/reports/d8888888-8888-8888-8888-888888888888/content?format=json_rag',
    '/api/v1/reports/d8888888-8888-8888-8888-888888888888/content?format=markdown',
    '/api/v1/reports/d8888888-8888-8888-8888-888888888888/content?format=pdf',
    TRUE, TRUE, TRUE, TRUE,
    18500,

    '{"pipeline_version": "3.0.0", "synthesis_model": "gemini-2.5-pro", "schema_version": "1.0", "input_skills": ["design_art", "user_experience", "technology_systems", "strategy_market"], "generated_at": "2026-06-21T10:00:00Z"}',

    '{"game_identity": "Disco Elysium — ZA/UM painterly dialogue RPG set in a politically fractured post-revolutionary city", "market_position": "Critical darling; 1M+ at $39.99; 2019 GOTY at Game Awards", "key_insights": ["Won GOTY + Narrative + RPG simultaneously at Game Awards 2019 — never repeated", "First game to explore political philosophy at this literary depth and sophistication", "ZA/UM studio implosion makes this a permanently closed artistic statement"], "critical_risks": ["No sequel possible due to studio collapse and original creator dismissal", "IP ownership dispute ongoing between ZA/UM entity and original team"], "recommended_actions": ["Focus all distribution on Final Cut (full voice acting)", "Consistent Steam 80% sale cycles for long-tail discovery"], "overall_confidence": 0.95, "overall_score": 9.5, "tag": "Genre-Defining"}',

    '{"design_art": {"score": 9.6, "tag": "Expressionist Masterwork", "summary": "1920s European expressionist painterly style — singular in the medium; character design through costume."}, "user_experience": {"score": 9.9, "tag": "Writing Pinnacle", "summary": "Finest dialogue writing in game history; failure states produce more interesting content than success."}, "technology_systems": {"score": 8.5, "tag": "Narrative Engine", "summary": "Bespoke RPG engine prioritizes dialogue over action; full VO in Final Cut elevated the experience."}, "strategy_market": {"score": 9.4, "tag": "Critical Phenomenon", "summary": "GOTY + Narrative + RPG triple crown at Game Awards 2019 from a first-time studio at $39.99."}}',

    '{"short_term": ["Maintain Final Cut as the only available version on all storefronts", "Regular 80% sale cycles on Steam to sustain discovery"], "long_term": ["License IP for adaptation (film, graphic novel) if creators regain rights", "Monitor legal situation around ZA/UM IP ownership carefully"], "market_opportunities": ["Literary fiction crossover audience — market as a novel you play", "Academic market: political philosophy and narrative design courses"]}',

    '{"high": ["ZA/UM studio implosion — original creators dismissed; no sequel is possible", "IP ownership dispute ongoing"], "medium": ["Switch version poor performance may have damaged console platform reputation"], "low": ["Market niche for dialogue-only RPG is inherently small"], "mitigation": ["Position as a definitive one-time artistic statement, not a franchise", "Long-tail digital distribution only"]}',

    '{"igdb_id": "28272", "rawg_id": "13536", "steam_app_id": "632470", "metacritic": 97, "launch_price": 39.99, "lifetime_sales": 1000000, "awards": {"game_awards_2019": ["GOTY", "Best Narrative", "Best RPG"]}, "studio_fate": "ZA/UM restructured after creator IP dispute in 2022"}',

    '{"phases": {"scraping": {"status": "completed", "duration_ms": 6100}, "analysis": {"status": "completed", "duration_ms": 13400}, "synthesis": {"status": "completed", "duration_ms": 7100}, "storage": {"status": "completed", "duration_ms": 700}}, "total_tokens": 86300}',

    '{"user_rating": 5, "user_notes": "The greatest RPG narrative ever written. Utterly one of a kind.", "bookmarked": true}',

    'c1111111-1111-1111-1111-111111111111',
    'c2222222-2222-2222-2222-222222222222',
    'c3333333-3333-3333-3333-333333333333',
    'c4444444-4444-4444-4444-444444444444',
    'c5555555-5555-5555-5555-555555555555'
)
ON CONFLICT (id) DO NOTHING;

-- =============================================================
-- PASO 3: Actualizar analysis.final_report_id
-- (relación inversa — reports → analysis ya existe por FK;
--  aquí cerramos el círculo analysis → reports)
-- =============================================================

UPDATE analysis
SET final_report_id = 'd1111111-1111-1111-1111-111111111111'
WHERE id IN (
    'b1111111-1111-1111-1111-111111111111',
    'b2222222-2222-2222-2222-222222222222',
    'b3333333-3333-3333-3333-333333333333',
    'b4444444-4444-4444-4444-444444444444',
    'b5555555-5555-5555-5555-555555555555'
);

UPDATE analysis
SET final_report_id = 'd8888888-8888-8888-8888-888888888888'
WHERE id IN (
    'c1111111-1111-1111-1111-111111111111',
    'c2222222-2222-2222-2222-222222222222',
    'c3333333-3333-3333-3333-333333333333',
    'c4444444-4444-4444-4444-444444444444',
    'c5555555-5555-5555-5555-555555555555'
);

-- =============================================================
-- PASO 4: Contadores de vistas y descargas
-- (prueba analytics y ordenamiento por view_count)
-- =============================================================

UPDATE reports SET view_count = 47,  download_count = 12 WHERE id = 'd1111111-1111-1111-1111-111111111111';
UPDATE reports SET view_count = 23,  download_count = 5  WHERE id = 'd2222222-2222-2222-2222-222222222222';
UPDATE reports SET view_count = 31,  download_count = 8  WHERE id = 'd3333333-3333-3333-3333-333333333333';
UPDATE reports SET view_count = 62,  download_count = 19 WHERE id = 'd4444444-4444-4444-4444-444444444444';
UPDATE reports SET view_count = 18,  download_count = 4  WHERE id = 'd5555555-5555-5555-5555-555555555555';
UPDATE reports SET view_count = 71,  download_count = 28 WHERE id = 'd8888888-8888-8888-8888-888888888888';

COMMIT;

-- =============================================================
-- VERIFICACIÓN RÁPIDA (ejecutar después del seed)
-- =============================================================

/*
-- Total por status
SELECT report_status, COUNT(*) FROM reports
WHERE user_id = '00000000-0000-0000-0000-000000000001'
GROUP BY report_status ORDER BY report_status;
-- Esperado: completed=5, failed=1, processing=1

-- Facets de géneros
SELECT unnest(all_genres) AS genre, COUNT(*) AS count
FROM reports
WHERE user_id = '00000000-0000-0000-0000-000000000001'
  AND report_status = 'completed'
GROUP BY genre ORDER BY count DESC;

-- Verificar análisis vinculados
SELECT r.game_name, a.analysis_type, a.status, a.confidence_score
FROM reports r
JOIN analysis a ON a.final_report_id = r.id
WHERE r.user_id = '00000000-0000-0000-0000-000000000001'
ORDER BY r.game_name, a.analysis_type;
-- Esperado: 5 filas Disco Elysium + 5 filas Elden Ring

-- Verificar reporte con contenido completo
SELECT id, game_name, markdown_generated, pdf_generated,
       length(markdown_content) AS md_chars,
       jsonb_pretty(executive_summary_jsonb) AS exec_summary
FROM reports
WHERE id = 'd8888888-8888-8888-8888-888888888888';

-- Verificar reporte en pipeline
SELECT id, game_name, report_status, current_phase, pipeline_progress
FROM reports
WHERE report_status = 'processing';
-- Esperado: Dead Cells, analysis, 42

-- Verificar reporte fallido
SELECT id, game_name, report_status,
       pipeline_data_jsonb->'phases'->'analysis'->>'error' AS error_msg
FROM reports
WHERE report_status = 'failed';
*/
