-- =====================================================
-- GETSMART - DATOS DE EJEMPLO PARA TESTING
-- Compatible con el schema de PostgreSQL pero adaptado para MySQL
-- =====================================================

-- Datos de ejemplo para la tabla users
INSERT INTO users (id, email, username, password_hash, is_verified, is_active, created_at, updated_at, last_login_at, timezone, language, profile_jsonb, settings_jsonb) VALUES
(UUID_TO_BIN(UUID()), 'admin@getsmart.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/UeCqdVnfa', TRUE, TRUE, NOW(), NOW(), NOW(), 'UTC', 'en', '{}', '{}'),
(UUID_TO_BIN(UUID()), 'test@getsmart.com', 'testuser', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/UeCqdVnfa', TRUE, TRUE, NOW() - INTERVAL 1 DAY, NOW(), 'America/New_York', 'en', '{}', '{}');

-- Datos de ejemplo para la tabla roles
INSERT INTO roles (id, user_id, role_name, permissions_jsonb, granted_at, is_active, metadata_jsonb) VALUES
(UUID_TO_BIN(UUID()), (SELECT id FROM users WHERE username = 'admin'), 'admin', '{"all": true}', NOW(), TRUE, '{}'),
(UUID_TO_BIN(UUID()), (SELECT id FROM users WHERE username = 'testuser'), 'user', '{"read": true, "create": true}', NOW(), TRUE, '{}');

-- Datos de ejemplo para la tabla analysis
INSERT INTO analysis (id, user_id, game_id, macro_skill_name, skill_version, status, created_at, started_at, completed_at, processing_time_ms, priority, input_data_jsonb, raw_output_jsonb, processed_output_jsonb, metrics_jsonb, error_details_jsonb, final_report_id) VALUES
-- Análisis completados para The Witcher 3
(UUID_TO_BIN(UUID()), (SELECT id FROM users WHERE username = 'testuser'), UUID_TO_BIN(UUID()), 'design_art', '1.0.0', 'completed', NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 1 HOUR, 45000, 5, '{}', '{"design_analysis": "...", "art_direction": "..."}', '{"processed": true}', '{"confidence": 0.95}', '{}', NULL),
(UUID_TO_BIN(UUID()), (SELECT id FROM users WHERE username = 'testuser'), UUID_TO_BIN(UUID()), 'user_experience', '1.0.0', 'completed', NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 1 HOUR, 38000, 5, '{}', '{"ux_analysis": "...", "player_journey": "..."}', '{"processed": true}', '{"confidence": 0.92}', '{}', NULL),
(UUID_TO_BIN(UUID()), (SELECT id FROM users WHERE username = 'testuser'), UUID_TO_BIN(UUID()), 'technology_systems', '1.0.0', 'completed', NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 1 HOUR, 52000, 5, '{}', '{"tech_stack": "...", "performance": "..."}', '{"processed": true}', '{"confidence": 0.88}', '{}', NULL),
(UUID_TO_BIN(UUID()), (SELECT id FROM users WHERE username = 'testuser'), UUID_TO_BIN(UUID()), 'strategy_market', '1.0.0', 'completed', NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 1 HOUR, 41000, 5, '{}', '{"business_model": "...", "market_position": "..."}', '{"processed": true}', '{"confidence": 0.90}', '{}', NULL),

-- Análisis en proceso para Cyberpunk 2077
(UUID_TO_BIN(UUID()), (SELECT id FROM users WHERE username = 'testuser'), UUID_TO_BIN(UUID()), 'design_art', '1.0.0', 'running', NOW() - INTERVAL 30 MINUTE, NOW(), NULL, 18000, 5, '{}', '{}', '{}', '{"confidence": null}', '{}', NULL),
(UUID_TO_BIN(UUID()), (SELECT id FROM users WHERE username = 'testuser'), UUID_TO_BIN(UUID()), 'user_experience', '1.0.0', 'waiting', NOW() - INTERVAL 30 MINUTE, NULL, NULL, NULL, 5, '{}', '{}', '{}', '{"confidence": null}', '{}', NULL);

-- Datos de ejemplo para la tabla reports
INSERT INTO reports (
    id, user_id, game_id, report_status, report_type, confidence_score,
    search_query, game_name, game_slug, release_year, primary_genre, primary_platform, 
    developer_name, all_genres, all_platforms, tags,
    created_at, updated_at, completed_at, report_date,
    view_count, download_count, share_count, processing_time_ms, file_size_mb,
    markdown_content, markdown_summary, pdf_html_content,
    url_json, url_json_rag, url_markdown, url_pdf,
    json_generated, markdown_generated, pdf_generated, json_rag_generated,
    report_metadata_jsonb, executive_summary_jsonb, thematic_analysis_jsonb, 
    cross_cutting_insights_jsonb, strategic_recommendations_jsonb, 
    risk_assessment_jsonb, appendices_jsonb, confidence_analysis_jsonb,
    game_data_jsonb, pipeline_data_jsonb, performance_metrics_jsonb, user_metadata_jsonb
) VALUES
-- Reporte completado para The Witcher 3
(
    UUID_TO_BIN(UUID()), 
    (SELECT id FROM users WHERE username = 'testuser'),
    UUID_TO_BIN(UUID()),
    'completed', 'comprehensive', 0.94,
    'The Witcher 3: Wild Hunt', 'The Witcher 3: Wild Hunt', 'the-witcher-3-wild-hunt', 2015, 'RPG', 'PC',
    'CD Projekt Red',
    JSON_ARRAY('RPG', 'Open World', 'Fantasy', 'Adventure'),
    JSON_ARRAY('PC', 'PlayStation 4', 'Xbox One', 'Nintendo Switch'),
    JSON_ARRAY('singleplayer', 'story-rich', 'choices-matter', 'open-world'),
    
    NOW() - INTERVAL 2 HOUR, NOW() - INTERVAL 1 HOUR, NOW() - INTERVAL 1 HOUR, CURRENT_DATE - INTERVAL 1 DAY,
    25, 5, 2, 176000, 2.4,
    
    '# The Witcher 3: Wild Hunt - Comprehensive Analysis Report\n\n## Executive Summary\nThe Witcher 3 represents a benchmark achievement in open-world RPG design...',
    'The Witcher 3: Wild Hunt - A comprehensive analysis covering game design, user experience, technology systems, and market strategy.',
    '<html><body><h1>The Witcher 3 Analysis Report</h1>...</body></html>',
    
    'https://api.getsmart.com/reports/ba8f2c3e-1d4f-4c9e-8b3a-6f7d1e2c9b5a/json',
    'https://api.getsmart.com/reports/ba8f2c3e-1d4f-4c9e-8b3a-6f7d1e2c9b5a/rag',
    'https://api.getsmart.com/reports/ba8f2c3e-1d4f-4c9e-8b3a-6f7d1e2c9b5a/markdown',
    'https://api.getsmart.com/reports/ba8f2c3e-1d4f-4c9e-8b3a-6f7d1e2c9b5a/pdf',
    
    TRUE, TRUE, TRUE, TRUE,
    
    '{"version": "1.0.0", "generated_at": "2024-06-26T04:00:00Z"}',
    '{"overview": "The Witcher 3 excels in narrative design and world-building", "key_findings": ["Strong character development", "Complex moral choices"]}',
    '{"narrative": {"score": 9.5}, "gameplay": {"score": 9.0}, "technical": {"score": 8.5}}',
    '{"patterns": ["Emphasis on player agency", "Branching narratives"], "trends": ["Open world evolution"]}',
    '{"strategies": ["Maintain narrative focus", "Expand modding support"]}',
    '{"technical_risks": ["Engine optimization needed"], "market_risks": ["Competition from similar RPGs"]}',
    '{"sources": ["Game files", "Player reviews", "Developer interviews"], "methodology": "Multi-source analysis"}',
    '{"overall_confidence": 0.94, "data_quality": "high"}',
    
    '{"rawg_id": 25477, "steam_app_id": 292030, "metacritic": 92}',
    '{"pipeline_id": "pipeline_001", "processing_time": "176s", "skills_used": ["design_art", "user_experience", "technology_systems", "strategy_market"]}',
    '{"api_calls": 45, "processing_speed": "high", "memory_usage": "optimal"}',
    '{"user_rating": 4.8, "notes": "Excellent example of modern RPG design", "bookmarked": true}'
),

-- Reporte en proceso para Cyberpunk 2077 (este es el que matchea con el backend)
(
    UUID_TO_BIN(UUID()), -- Este será el db_report_id que el backend usa (1 o algún ID...siguiente)
    (SELECT id FROM users WHERE username = 'testuser'),
    UUID_TO_BIN(UUID()),
    'processing', 'comprehensive', NULL,
    'Cyberpunk 2077', 'Cyberpunk 2077', 'cyberpunk-2077', 2020, 'RPG', 'PC',
    'CD Projekt Red',
    JSON_ARRAY('RPG', 'Sci-Fi', 'Open World', 'Action'),
    JSON_ARRAY('PC', 'PlayStation 4', 'Xbox One', 'PlayStation 5', 'Xbox Series X/S'),
    JSON_ARRAY('singleplayer', 'cyberpunk', 'story-rich', 'open-world'),
    
    NOW() - INTERVAL 30 MINUTE, NOW() - INTERVAL 5 MINUTE, NULL, CURRENT_DATE,
    0, 0, 0, NULL, NULL,
    
    NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,
    FALSE, FALSE, FALSE, FALSE,
    
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    
    '{"rawg_id": 25477, "steam_app_id": 292030, "metacritic": 86}',
    '{"pipeline_id": "pipeline_002", "processing_time": null, "skills_used": ["design_art", "user_experience", "technology_systems", "strategy_market"]}',
    '{"api_calls": 12, "processing_speed": "normal", "memory_usage": "normal"}',
    '{"user_rating": null, "notes": "Currently in analysis phase", "bookmarked": false}'
);

-- =====================================================
-- NOTA IMPORTANTE: MAPES ENTRE BACKEND Y BASE DE DATOS
-- =====================================================
/*
RELACIONES CLAVE:

1. Pipeline ID (_backend_) -> report_id (string UUID tracks del pipeline_tracker)
2. db_report_id (int/detalles) -> id (reports.id UUID convertido a INT para API)

El backend maneja:
- pipeline_tracker.active_pipelines[{report_id}] = {"db_report_id": 123}

El frontend recibe:
- DetailedPipelineResponse con db_report_id: 123
- onComplete(reportId, dbReportId) -> navigate(`/pipeline/${reportId}?db_report_id=${dbReportId}`)

En la llamada a la base de datos necesitas:
SELECT BIN_TO_UUID(id) as uuid_id, * FROM reports WHERE id = UUID_TO_BIN(?)

Para el dashboard, el frontend esperará:
GET /api/reports -> [
  {
    id: "string-uuid",  // reports.id convertido a string UUID
    title: "Game Name",
    status: "completed|processing|failed",
    // ... otros campos
  }
]
*/

-- =====================================================
-- VISTAS ÚTILES PARA TESTING
-- =====================================================

-- Vista para el endpoint GET /api/reports (dashboard)
CREATE OR REPLACE VIEW vw_dashboard_reports AS
SELECT 
    BIN_TO_UUID(r.id) as id,
    r.game_name as title,
    r.developer_name as developer,
    r.primary_genre as genre,
    r.primary_platform as platform,
    r.report_status as status,
    r.confidence_score,
    r.created_at,
    r.updated_at,
    r.completed_at,
    r.game_slug,
    r.release_year as year,
    r.markdown_summary,
    r.view_count,
    r.download_count,
    r.file_size_mb
FROM reports r
ORDER BY r.updated_at DESC;

-- Vista para detalles individuales de reportes
CREATE OR REPLACE VIEW vw_report_details AS
SELECT 
    BIN_TO_UUID(r.id) as id,
    r.game_name,
    r.developer_name,
    r.report_status,
    r.confidence_score,
    r.markdown_content,
    r.markdown_summary,
    r.url_json,
    r.url_markdown,
    r.url_pdf,
    r.created_at,
    r.completed_at,
    r.processing_time_ms,
    r.view_count,
    r.download_count,
    r.json_generated,
    r.markdown_generated,
    r.pdf_generated
FROM reports r
WHERE r.report_status = 'completed';

-- Query para obtener reportes del dashboard (compatible con frontend)
SELECT 
    id,
    title,
    developer,
    genre,
    platform,
    status,
    confidence_score,
    created_at,
    updated_at,
    completed_at,
    game_slug,
    release_year as year,
    markdown_summary,
    view_count,
    download_count,
    file_size_mb
FROM vw_dashboard_reports
ORDER BY updated_at DESC;

-- Query para buscar un reporte por db_report_id (para el frontend)
SELECT 
    BIN_TO_UUID(id) as id,
    game_name,
    developer_name,
    report_status,
    confidence_score,
    markdown_content,
    url_pdf
FROM reports 
WHERE id = (SELECT id FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) as row_num FROM reports) AS t WHERE row_num = ?);