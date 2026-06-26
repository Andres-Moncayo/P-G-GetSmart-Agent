-- =====================================================
-- GETSMART DATABASE SCHEMA - MYSQL VERSION
-- 4 TABLAS EXACTAS: users, roles, analysis, reports
-- Compatibilidad con PostgreSQL schema adaptado para MySQL 8.0+
-- =====================================================

-- Configuración inicial
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- TABLA 1: users (usuarios)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    -- Claves Primarias y Autenticación
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NULL COMMENT 'NULL para SSO',
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata clave (columnas para filtros y búsqueda)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Datos en formato JSON (MySQL 8.0+)
    profile_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'avatar, bio, location, social links, etc.',
    settings_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'notifications, themes, display preferences',
    
    PRIMARY KEY (id),
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_created_at (created_at),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Usuarios del sistema';

-- =====================================================
-- TABLA 2: roles
-- =====================================================
CREATE TABLE IF NOT EXISTS roles (
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    role_name VARCHAR(50) NOT NULL DEFAULT 'user',
    permissions_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Permisos específicos del rol',
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Metadata adicional del rol',
    
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_role_name (role_name),
    INDEX idx_is_active (is_active),
    UNIQUE KEY uk_user_role (user_id, role_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Roles y permisos de usuarios';

-- =====================================================
-- TABLA 3: analysis
-- =====================================================
CREATE TABLE IF NOT EXISTS analysis (
    -- Claves Primarias y Relaciones
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    game_id CHAR(36) NOT NULL COMMENT 'ID universal del juego',
    
    -- Identificación del análisis
    macro_skill_name VARCHAR(50) NOT NULL COMMENT 'design_art, user_experience, technology_systems, strategy_market',
    skill_version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    status VARCHAR(20) NOT NULL DEFAULT 'queued' 
        CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled', 'waiting', 'paused', 'skipped')),
    
    -- Tiempos y métricas
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    processing_time_ms INT NULL,
    priority INT DEFAULT 5 COMMENT 'Prioridad 1-10',
    
    -- Datos intermedios y resultados en JSON
    input_data_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Master JSON + macro-skill inputs',
    raw_output_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Salida cruda del skill',
    processed_output_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Salida procesada y validada',
    
    -- Métricas y metadata en JSON
    metrics_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'performance, data_sources, versiones, etc.',
    error_details_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'errores específicos, logs, etc.',
    
    -- Referencias cruzadas
    final_report_id CHAR(36) NULL,
    
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_game_id (game_id),
    INDEX idx_macro_skill (macro_skill_name),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_completed_at (completed_at),
    INDEX idx_priority (priority),
    INDEX idx_status_created (status, created_at),
    INDEX fk_analysis_final_report (final_report_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Análisis individuales de macro-skills';

-- =====================================================
-- TABLA 4: reports (Tabla principal)
-- =====================================================
CREATE TABLE IF NOT EXISTS reports (
    -- Claves Primarias y Relaciones
    id CHAR(36) NOT NULL DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    game_id CHAR(36) NOT NULL COMMENT 'ID universal del juego',
    
    -- Claves para filtros PRINCIPALES
    report_status VARCHAR(20) NOT NULL DEFAULT 'queued' 
        CHECK (report_status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')),
    report_type VARCHAR(50) NOT NULL DEFAULT 'comprehensive'
        CHECK (report_type IN ('comprehensive', 'partial', 'low_confidence', 'error', 'template')),
    confidence_score DECIMAL(3,2) NULL 
        CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    
    -- Parámetros de búsqueda y filtrado (columnas únicas para performance)
    search_query TEXT NULL COMMENT 'Query original de búsqueda',
    game_name VARCHAR(255) NOT NULL COMMENT 'Nombre del juego',
    game_slug VARCHAR(255) NULL COMMENT 'Slug para URL amigables',
    release_year INT NULL 
        CHECK (release_year >= 1970 AND release_year <= YEAR(NOW()) + 5),
    primary_genre VARCHAR(100) NULL COMMENT 'Género principal para filtro rápido',
    primary_platform VARCHAR(100) NULL COMMENT 'Plataforma principal',
    developer_name VARCHAR(255) NULL COMMENT 'Desarrollador para búsqueda',
    
    -- Arrays para filtros múltiples (usando JSON en MySQL)
    all_genres JSON NULL COMMENT 'Array de todos los géneros',
    all_platforms JSON NULL COMMENT 'Array de todas las plataformas',
    tags JSON NULL COMMENT 'Tags definidos por usuario/sistema',
    
    -- Fechas clave para ordenamiento y filtrado temporal
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    report_date DATE DEFAULT (CURRENT_DATE) COMMENT 'Fecha del reporte (no creación)',
    
    -- Métricas y estadísticas
    view_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    share_count INT DEFAULT 0,
    processing_time_ms INT NULL,
    file_size_mb DECIMAL(8,2) NULL COMMENT 'Tamaño total de archivos generados',
    
    -- Contenido principal (.md y formateado para PDF)
    markdown_content TEXT NULL COMMENT 'CONTENIDO PRINCIPAL EN .md',
    markdown_summary TEXT NULL COMMENT 'Resumen rápido para previews',
    pdf_html_content TEXT NULL COMMENT 'HTML preparado para WeasyPrint',
    
    -- URLs de acceso a archivos generados
    url_json VARCHAR(1000) NULL,
    url_json_rag VARCHAR(1000) NULL,
    url_markdown VARCHAR(1000) NULL,
    url_pdf VARCHAR(1000) NULL,
    
    -- Estado de generación de archivos
    json_generated BOOLEAN DEFAULT FALSE,
    markdown_generated BOOLEAN DEFAULT FALSE,
    pdf_generated BOOLEAN DEFAULT FALSE,
    json_rag_generated BOOLEAN DEFAULT FALSE,
    
    -- Datos estructurados completos en JSON
    report_metadata_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'metadata del reporte',
    executive_summary_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'sección executive_summary',
    thematic_analysis_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT '17 categorías temáticas',
    cross_cutting_insights_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'insights transversales',
    strategic_recommendations_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'recomendaciones estratégicas',
    risk_assessment_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'evaluación de riesgos',
    appendices_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'apéndices, fuentes, metodología',
    confidence_analysis_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'análisis detallado de confianza',
    
    -- Datos adicionales compactados en JSON
    game_data_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Datos completos del juego',
    pipeline_data_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Datos del pipeline',
    performance_metrics_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Métricas de rendimiento',
    user_metadata_jsonb JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT 'Metadatos usuario: rating, notas',
    
    -- Referencias a análisis individuales (los 4 macro-skills)
    analysis_design_art CHAR(36) NULL,
    analysis_user_experience CHAR(36) NULL,
    analysis_technology_systems CHAR(36) NULL,
    analysis_strategy_market CHAR(36) NULL,
    
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (analysis_design_art) REFERENCES analysis(id) ON DELETE SET NULL,
    FOREIGN KEY (analysis_user_experience) REFERENCES analysis(id) ON DELETE SET NULL,
    FOREIGN KEY (analysis_technology_systems) REFERENCES analysis(id) ON DELETE SET NULL,
    FOREIGN KEY (analysis_strategy_market) REFERENCES analysis(id) ON DELETE SET NULL,
    
    -- Índices para performance
    INDEX idx_user_id (user_id),
    INDEX idx_game_id (game_id),
    INDEX idx_status (report_status),
    INDEX idx_type (report_type),
    INDEX idx_game_name (game_name),
    INDEX idx_developer (developer_name),
    INDEX idx_primary_genre (primary_genre),
    INDEX idx_primary_platform (primary_platform),
    INDEX idx_release_year (release_year),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at),
    INDEX idx_completed_at (completed_at),
    INDEX idx_confidence_score (confidence_score),
    INDEX idx_report_date (report_date),
    INDEX idx_status_created (report_status, created_at),
    INDEX idx_user_status (user_id, report_status),
    INDEX idx_genre_year (primary_genre, release_year),
    INDEX idx_platform_year (primary_platform, release_year),
    
    -- Índices JSON para filtros (MySQL 8.0+)
    INDEX idx_all_genres ((CAST(all_genres AS CHAR(255) ARRAY))),
    INDEX idx_all_platforms ((CAST(all_platforms AS CHAR(255) ARRAY))),
    INDEX idx_tags ((CAST(tags AS CHAR(255) ARRAY))),
    
    -- Índices compuestos para queries comunes
    INDEX idx_user_status_created (user_id, report_status, updated_at DESC),
    INDEX idx_status_completed (report_status, completed_at DESC),
    INDEX idx_genre_status_year (primary_genre, report_status, release_year)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Reportes completos del sistema';

-- =====================================================
-- VISTAS ÚTILES PARA EL FRONTEND
-- =====================================================

-- Vista para el Dashboard (GET /api/reports)
CREATE OR REPLACE VIEW vw_dashboard_reports AS
SELECT 
    r.id as id,
    r.game_name as title,
    r.developer_name as developer,
    COALESCE(r.primary_genre, 'Unknown') as genre,
    COALESCE(r.primary_platform, 'Unknown') as platform,
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
    r.file_size_mb,
    -- Para counts en sidebar
    (SELECT COUNT(*) FROM reports WHERE user_id = r.user_id AND report_status = 'completed') as total_completed,
    -- URL de preview
    CASE 
        WHEN r.markdown_generated = TRUE THEN r.url_markdown
        ELSE NULL
    END as preview_url
FROM reports r
ORDER BY r.updated_at DESC;

-- Vista para detalles de reportes individuales
CREATE OR REPLACE VIEW vw_report_details AS
SELECT 
    r.id,
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
    r.report_type,
    r.json_generated,
    r.markdown_generated,
    r.pdf_generated,
    -- Datos de análisis relacionados
    da.status as design_art_status,
    da.completed_at as design_art_completed,
    ux.status as ux_status,
    ux.completed_at as ux_completed,
    ts.status as tech_status,
    ts.completed_at as tech_completed,
    sm.status as strategy_status,
    sm.completed_at as strategy_completed
FROM reports r
LEFT JOIN analysis da ON r.analysis_design_art = da.id
LEFT JOIN analysis ux ON r.analysis_user_experience = ux.id
LEFT JOIN analysis ts ON r.analysis_technology_systems = ts.id
LEFT JOIN analysis sm ON r.analysis_strategy_market = sm.id;

-- =====================================================
-- STORED PROCEDURES ÚTILES
-- =====================================================

DELIMITER //

-- Procedure para obtener reportes por usuario (Dashboard)
CREATE PROCEDURE sp_get_user_reports(
    IN p_user_id CHAR(36),
    IN p_status VARCHAR(20),
    IN p_limit INT DEFAULT 50,
    IN p_offset INT DEFAULT 0
)
BEGIN
    SELECT 
        id, title, developer, genre, platform, status, confidence_score,
        created_at, updated_at, completed_at, game_slug, year,
        markdown_summary, view_count, download_count, file_size_mb
    FROM vw_dashboard_reports 
    WHERE user_id = p_user_id
    AND (p_status IS NULL OR status = p_status)
    ORDER BY updated_at DESC
    LIMIT p_limit OFFSET p_offset;
END //

-- Procedure para crear/actualizar pipeline progress
CREATE PROCEDURE sp_update_pipeline_progress(
    IN p_report_id CHAR(36),
    IN p_phase VARCHAR(20),
    IN p_status VARCHAR(20),
    IN p_progress FLOAT,
    IN p_message TEXT
)
BEGIN
    DECLARE v_pipeline_json JSON;
    
    -- Obtener pipeline_data actual
    SELECT pipeline_data_jsonb INTO v_pipeline_json
    FROM reports 
    WHERE id = p_report_id;
    
    -- Actualizar progress
    IF v_pipeline_json IS NULL THEN
        SET v_pipeline_json = JSON_OBJECT();
    END IF;
    
    SET v_pipeline_json = JSON_SET(
        v_pipeline_json,
        CONCAT('$.phases.', p_phase),
        JSON_OBJECT(
            'status', p_status,
            'progress', p_progress,
            'message', p_message,
            'updated_at', NOW()
        )
    );
    
    -- Actualizar reporte
    UPDATE reports 
    SET 
        pipeline_data_jsonb = v_pipeline_json,
        updated_at = NOW()
    WHERE id = p_report_id;
    
END //

DELIMITER ;

-- =====================================================
-- TRIGGERS PARA MANTENER CONSISTENCIA
-- =====================================================

DELIMITER //

-- Trigger para actualizar timestamps
CREATE TRIGGER tr_users_updated_at 
BEFORE UPDATE ON users 
FOR EACH ROW 
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END //

-- Trigger para actualizar reportes timestamp
CREATE TRIGGER tr_reports_updated_at 
BEFORE UPDATE ON reports 
FOR EACH ROW 
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END //

-- Trigger para actualizar status de reporte basado en análisis
CREATE TRIGGER tr_analysis_update_report_status 
AFTER UPDATE ON analysis 
FOR EACH ROW 
BEGIN
    DECLARE v_all_completed INT DEFAULT 0;
    DECLARE v_any_failed INT DEFAULT 0;
    
    -- Si el análisis se completa o falla, verificar status del reporte
    IF NEW.status IN ('completed', 'failed') THEN
        -- Contar análisis completados y fallidos para este reporte
        SELECT COUNT(*) INTO v_all_completed
        FROM reports r
        JOIN analysis a ON (
            r.analysis_design_art = a.id OR 
            r.analysis_user_experience = a.id OR 
            r.analysis_technology_systems = a.id OR 
            r.analysis_strategy_market = a.id
        )
        WHERE r.id = NEW.final_report_id AND a.status = 'completed';
        
        SELECT COUNT(*) INTO v_any_failed
        FROM reports r
        JOIN analysis a ON (
            r.analysis_design_art = a.id OR 
            r.analysis_user_experience = a.id OR 
            r.analysis_technology_systems = a.id OR 
            r.analysis_strategy_market = a.id
        )
        WHERE r.id = NEW.final_report_id AND a.status = 'failed';
        
        -- Actualizar status del reporte si todos están completados o alguno falló
        IF v_all_completed = 4 THEN
            UPDATE reports 
            SET report_status = 'completed', completed_at = NOW()
            WHERE id = NEW.final_report_id;
        ELSEIF v_any_failed > 0 THEN
            UPDATE reports 
            SET report_status = 'failed'
            WHERE id = NEW.final_report_id;
        END IF;
    END IF;
END //

DELIMITER ;

-- =====================================================
-- CONFIGURACIÓN FINAL
-- =====================================================
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- EJEMPLOS DE USO
-- =====================================================

/*
-- Para el Dashboard (compatible con frontend)
CALL sp_get_user_reports('user-uuid-here', NULL, 50, 0);

-- Para obtener reportes por status específico
CALL sp_get_user_reports('user-uuid-here', 'processing', 20, 0);

-- Para actualizar pipeline progress (llamado por backend)
CALL sp_update_pipeline_progress('report-uuid-here', 'phase1', 'running', 45.0, 'Scraping game data...');

-- Query directo para buscar por db_report_id (cuando frontend navega)
SELECT id, game_name, developer_name, report_status, confidence_score, 
       markdown_content, url_pdf
FROM reports 
WHERE id = 'uuid-del-reporte';

-- Query para contar reportes por status (para sidebar counts)
SELECT report_status, COUNT(*) as count
FROM reports 
WHERE user_id = 'user-uuid-here'
GROUP BY report_status;

-- Query para filtros de género/año/platform 
SELECT r.*, 
    JSON_EXTRACT(all_genres, '$[*]') as genres_array,
    JSON_EXTRACT(all_platforms, '$[*]') as platforms_array
FROM reports r
WHERE JSON_CONTAINS(all_genres, '"RPG"')
AND release_year BETWEEN 2020 AND 2024
ORDER BY created_at DESC;
*/