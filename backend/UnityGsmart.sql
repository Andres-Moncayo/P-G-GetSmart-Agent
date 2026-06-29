-- =====================================================
-- GETSMART LEADER DATABASE DESIGN V1.0
-- 4 TABLAS EXACTAS: usuarios, roles, análisis, reportes
-- Estrategia: JSONB Compacto + Columnas de Filtro Clave
-- Basado en: final_report_schema.json + data_crud_contract.yaml + synthesis_skill.yaml
-- =====================================================

-- Creado: 2026-06-22
-- Requisitos del líder:
-- 1. Exactamente 4 tablas: usuarios, roles, análisis, reportes
-- 2. Máxima compactación en JSONB
-- 3. Reportes con .md para generación de PDF
-- 4. Parámetros de consulta/filtros en columnas aparte
-- 5. IDs de reportes y juegos en columnas separadas

-- =====================================================
-- EXTENSIONES REQUERIDAS
-- =====================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- TABLA 1: usuarios (Información básica + preferencias JSONB)
-- =====================================================
CREATE TABLE users (
    -- Claves Primarias y Autenticación
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- NULL para SSO
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
-- Metadata clave (columnas para filtros y búsqueda)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Todo lo demás en JSONB (perfil y preferencias compactadas)
    profile_jsonb JSONB NOT NULL DEFAULT '{}', -- avatar, bio, location, social links, etc.
    settings_jsonb JSONB NOT NULL DEFAULT '{}' -- notifications, themes, display preferences
);

-- =====================================================
-- TABLA 2: roles (Gestión de roles y permisos JSONB)
-- =====================================================
CREATE TABLE roles (
    -- Claves Primarias
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_name VARCHAR(50) NOT NULL CHECK (role_name IN ('admin','developer', 'user')),
    
    -- Claves para filtros y administración
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraint: Un usuario no puede tener el mismo rol duplicado activo
    UNIQUE(user_id, role_name, is_active)
);

-- =====================================================
-- TABLA 3: analysis (Proceso de pipeline y datos intermedios JSONB)
-- =====================================================
CREATE TABLE analysis (
    -- Claves Primarias y Relaciones
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- Usuario propietario del análisis
    game_id UUID NOT NULL, -- ID del juego (referencia cruzada con reportes)
    
    -- Claves para filtros principales
    analysis_type VARCHAR(50) NOT NULL CHECK (analysis_type IN (
        'design_art', 'user_experience', 'technology_systems', 'strategy_market', 'synthesis'
)),
    status VARCHAR(20) NOT NULL DEFAULT 'queued' CHECK (status IN (
        'queued', 'processing', 'completed', 'failed', 'cancelled'
    )),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    
    -- Parámetros de consulta y configuración (columnas para búsquedas rápidas)
    query_params JSONB NOT NULL DEFAULT '{}', -- Filtros originales de búsqueda
    target_game_filters JSONB NOT NULL DEFAULT '{}', -- {genres: [], platforms: [], release_year_range: []}
    pipeline_config JSONB NOT NULL DEFAULT '{}', -- Configuración específica del pipeline
    
    -- Metadata clave (para ordenamiento y filtrado)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_ms INTEGER,
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    
    -- Datos intermedios y resultados en JSONB (compactado)
    input_data_jsonb JSONB NOT NULL DEFAULT '{}', -- Master JSON + macro-skill inputs
    raw_output_jsonb JSONB NOT NULL DEFAULT '{}', -- Salida cruda del skill
    processed_output_jsonb JSONB NOT NULL DEFAULT '{}', -- Salida procesada y validada
    
    -- Métricas y metadata en JSONB
    metrics_jsonb JSONB NOT NULL DEFAULT '{}', -- performance, data_sources, versiones, etc.
    error_details_jsonb JSONB NOT NULL DEFAULT '{}', -- errores específicos, logs, etc.
    
    -- Referencias cruzadas (para traer el reporte final)
    final_report_id UUID -- Referencia al reporte sintetizado
);

-- =====================================================
-- TABLA 4: reportes (Tabla principal - Almacenamiento de .md y PDFs)
-- =====================================================
CREATE TABLE reports (
    -- Claves Primarias y Relaciones
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- Usuario propietario del reporte
    game_id UUID NOT NULL, -- ID universal del juego
    
    -- Claves para filtros PRINCIPALES
    report_status VARCHAR(20) NOT NULL DEFAULT 'queued' CHECK (report_status IN (
        'queued', 'processing', 'completed', 'failed', 'cancelled'
    )),
    report_type VARCHAR(50) NOT NULL DEFAULT 'comprehensive' CHECK (report_type IN (
        'comprehensive', 'partial', 'low_confidence', 'error', 'template'
    )),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    
    -- Parámetros de búsqueda y filtrado (columnas únicas para performance)
    -- Estos son los campos que se usarán más frecuentemente en WHERE clauses
    search_query TEXT, -- Query original de búsqueda
    game_name VARCHAR(255) NOT NULL, -- Nombre del juego (para búsquedas textuales)
    game_slug VARCHAR(255), -- Slug para URL amigables
    release_year INTEGER CHECK (release_year >= 1970 AND release_year <= EXTRACT(YEAR FROM NOW()) + 5),
    primary_genre VARCHAR(100), -- Género principal para filtro rápido
    primary_platform VARCHAR(100), -- Plataforma principal
    developer_name VARCHAR(255), -- Desarrollador para búsqueda
    cover_url VARCHAR(1000), -- Imagen/cover del juego (proviene del candidato RAWG)
    -- Arrays para filtros múltiples
    all_genres TEXT[], -- Array de todos los géneros
    all_platforms TEXT[], -- Array de todas las plataformas
    tags TEXT[], -- Tags definidos por usuario/sistema

    -- Progreso del pipeline (para la tarjeta "In Pipeline" del dashboard)
    current_phase VARCHAR(50), -- scraping | analysis | synthesis | storage
    pipeline_progress INTEGER DEFAULT 0 CHECK (pipeline_progress >= 0 AND pipeline_progress <= 100),
    
    -- Fechas clave para ordenamiento y filtrado temporal
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    report_date DATE DEFAULT CURRENT_DATE, -- Fecha del reporte (no creación)
    
    -- Métricas y estadísticas (columnas para sorting y analytics)
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    processing_time_ms INTEGER,
    file_size_mb DECIMAL(8,2), -- Tamaño total de archivos generados
    
    -- Contenido principal (.md y formateado para PDF)
    markdown_content TEXT, -- CONTENIDO PRINCIPAL EN .md para generar PDFs
    markdown_summary TEXT, -- Resumen rápido para previews
    pdf_html_content TEXT, -- HTML preparado para WeasyPrint (PDF generation)
    
    -- URLs de acceso a archivos generados
    url_json VARCHAR(1000), -- URL al JSON completo
    url_json_rag VARCHAR(1000), -- URL al JSON optimizado para RAG
    url_markdown VARCHAR(1000), -- URL al archivo .md
    url_pdf VARCHAR(1000), -- URL al PDF generado
    
    -- Estado de generación de archivos
    json_generated BOOLEAN DEFAULT FALSE,
    markdown_generated BOOLEAN DEFAULT FALSE,
    pdf_generated BOOLEAN DEFAULT FALSE,
    json_rag_generated BOOLEAN DEFAULT FALSE,
    
    -- Datos estructurados completos en JSONB (compactado por eficiencia)
    -- Aquí va la estructura completa del final_report_schema.json
    report_metadata_jsonb JSONB NOT NULL DEFAULT '{}', -- metadata del reporte (versión, modelo, etc.)
    executive_summary_jsonb JSONB NOT NULL DEFAULT '{}', -- sección executive_summary
    thematic_analysis_jsonb JSONB NOT NULL DEFAULT '{}', -- 17 categorías temáticas completas
    cross_cutting_insights_jsonb JSONB NOT NULL DEFAULT '{}', -- insights transversales
    strategic_recommendations_jsonb JSONB NOT NULL DEFAULT '{}', -- recomendaciones estratégicas
    risk_assessment_jsonb JSONB NOT NULL DEFAULT '{}', -- evaluación de riesgos
    appendices_jsonb JSONB NOT NULL DEFAULT '{}', -- apéndices, fuentes, metodología
    confidence_analysis_jsonb JSONB NOT NULL DEFAULT '{}', -- análisis detallado de confianza
    
    -- Datos adicionales compactados en JSONB
    game_data_jsonb JSONB NOT NULL DEFAULT '{}', -- Datos completos del juego (IGDB, RAWG, Steam)
    pipeline_data_jsonb JSONB NOT NULL DEFAULT '{}', -- Datos del pipeline: skills, versiones, etc.
    performance_metrics_jsonb JSONB NOT NULL DEFAULT '{}', -- Métricas de rendimiento detalladas
    user_metadata_jsonb JSONB NOT NULL DEFAULT '{}', -- Metadatos usuario: rating, notas, bookmarks
    
-- Referencias a análisis individuales (los 4 macro-skills)
    analysis_design_art UUID REFERENCES analysis(id),
    analysis_user_experience UUID REFERENCES analysis(id),
    analysis_technology_systems UUID REFERENCES analysis(id),
    analysis_strategy_market UUID REFERENCES analysis(id),
    analysis_synthesis UUID REFERENCES analysis(id)
);

-- =====================================================
-- ÍNDICES ESPECIALIZADOS PARA FILTROS RÁPIDOS
-- =====================================================

-- Índices para usuarios
CREATE INDEX idx_usuarios_email ON users(email);
CREATE INDEX idx_usuarios_username ON users(username);
CREATE INDEX idx_usuarios_active ON users(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_usuarios_created ON users(created_at DESC);

-- Índices JSONB para usuarios
CREATE INDEX idx_usuarios_profile ON users USING GIN(profile_jsonb);
CREATE INDEX idx_usuarios_settings ON users USING GIN(settings_jsonb);

-- Índices para roles
CREATE INDEX idx_roles_user_active ON roles(user_id, is_active);
CREATE INDEX idx_roles_name ON roles(role_name);

-- Índices para análisis (parámetros de consulta)
CREATE INDEX idx_analisis_user_status ON analysis(user_id, status);
CREATE INDEX idx_analisis_game_user ON analysis(game_id, user_id);
CREATE INDEX idx_analisis_type ON analysis(analysis_type);
CREATE INDEX idx_analisis_confidence ON analysis(confidence_score DESC);
CREATE INDEX idx_analisis_created ON analysis(created_at DESC);
CREATE INDEX idx_analisis_completed ON analysis(completed_at DESC) WHERE completed_at IS NOT NULL;

-- Índices JSONB para análisis (datos compactados)
CREATE INDEX idx_analisis_input_data ON analysis USING GIN(input_data_jsonb);
CREATE INDEX idx_analisis_output ON analysis USING GIN(processed_output_jsonb);
CREATE INDEX idx_analisis_filters ON analysis USING GIN(target_game_filters);
CREATE INDEX idx_analisis_query_params ON analysis USING GIN(query_params);

-- ÍNDICES CRÍTICOS PARA REPORTES (Tabla principal)
-- Índices para columnas de filtro principal (los más importante para rendimiento)
CREATE INDEX idx_reports_user_status ON reports(user_id, report_status);
CREATE INDEX idx_reports_game_status ON reports(game_id, report_status);
CREATE INDEX idx_reports_status ON reports(report_status);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_confidence ON reports(confidence_score DESC);

-- Índices para búsqueda textual y filtros comunes
CREATE INDEX idx_reports_game_name ON reports USING gin(to_tsvector('english', game_name));
CREATE INDEX idx_reports_search_query ON reports USING gin(to_tsvector('english', search_query));
CREATE INDEX idx_reports_developer ON reports(developer_name);
CREATE INDEX idx_reports_genre ON reports(primary_genre);
CREATE INDEX idx_reports_platform ON reports(primary_platform);
CREATE INDEX idx_reports_year ON reports(release_year DESC);
CREATE INDEX idx_reports_tags ON reports USING GIN(tags);

-- Índices para arrays (filtrado múltiple)
CREATE INDEX idx_reports_genres_array ON reports USING GIN(all_genres);
CREATE INDEX idx_reports_platforms_array ON reports USING GIN(all_platforms);

-- Índices para ordenamiento y analytics
CREATE INDEX idx_reports_created ON reports(created_at DESC);
CREATE INDEX idx_reports_completed ON reports(completed_at DESC) WHERE completed_at IS NOT NULL;
CREATE INDEX idx_reports_views ON reports(view_count DESC);
CREATE INDEX idx_reports_downloads ON reports(download_count DESC);

-- Índices para contenido .md (búsqueda full-text en reportes)
CREATE INDEX idx_reports_markdown_content ON reports USING gin(to_tsvector('english', markdown_content));
CREATE INDEX idx_reports_markdown_summary ON reports USING gin(to_tsvector('english', markdown_summary));

-- Índices URL para acceso rápido
CREATE INDEX idx_reports_url_json ON reports(url_json) WHERE url_json IS NOT NULL;
CREATE INDEX idx_reports_url_markdown ON reports(url_markdown) WHERE url_markdown IS NOT NULL;
CREATE INDEX idx_reports_url_pdf ON reports(url_pdf) WHERE url_pdf IS NOT NULL;

-- Índices JSONB para datos estructurados compactados
CREATE INDEX idx_reports_metadata ON reports USING GIN(report_metadata_jsonb);
CREATE INDEX idx_reports_executive ON reports USING GIN(executive_summary_jsonb);
CREATE INDEX idx_reports_thematic ON reports USING GIN(thematic_analysis_jsonb);
CREATE INDEX idx_reports_game_data ON reports USING GIN(game_data_jsonb);
CREATE INDEX idx_reports_pipeline_data ON reports USING GIN(pipeline_data_jsonb);
CREATE INDEX idx_reports_user_metadata ON reports USING GIN(user_metadata_jsonb);

-- =====================================================
-- TRIGGERS PARA MANTENIMIENTO AUTOMÁTICO
-- =====================================================

-- Función para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_usuarios_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analisis_updated_at 
    BEFORE UPDATE ON analysis 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reportes_updated_at 
    BEFORE UPDATE ON reports 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- User statistics triggers will be added when usage_stats_jsonb column is implemented
-- For now, the triggers are disabled to avoid reference errors

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Políticas para usuarios
CREATE POLICY "Usuarios pueden ver su propio perfil" ON users
    FOR SELECT USING (id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY "Usuarios pueden actualizar su perfil" ON users
    FOR UPDATE USING (id = current_setting('app.current_user_id', true)::UUID);

-- Políticas para roles
CREATE POLICY "Usuarios pueden ver sus roles" ON roles
    FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::UUID);

-- Políticas para análisis
CREATE POLICY "Usuarios pueden ver sus análisis" ON analysis
    FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY "Usuarios pueden crear sus análisis" ON analysis
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY "Usuarios pueden actualizar sus análisis" ON analysis
    FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY "Usuarios pueden eliminar sus análisis" ON analysis
    FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::UUID);

-- Políticas para reportes (tabla más importante)
CREATE POLICY "Usuarios pueden ver sus reportes" ON reports
    FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY "Usuarios pueden crear sus reportes" ON reports
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY "Usuarios pueden actualizar sus reportes" ON reports
    FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::UUID);

CREATE POLICY "Usuarios pueden eliminar sus reportes" ON reports
    FOR DELETE USING (user_id = current_setting('app.current_user_id', true)::UUID);

-- Políticas de admin (acceso completo)
CREATE POLICY "Admins tienen acceso completo a usuarios" ON users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM roles r
            JOIN users u ON r.user_id = u.id
            WHERE r.user_id = current_setting('app.current_user_id', true)::UUID
            AND r.role_name = 'admin' AND r.is_active = TRUE
        )
    );

CREATE POLICY "Admins tienen acceso completo a roles" ON roles
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM roles r 
            WHERE r.user_id = current_setting('app.current_user_id', true)::UUID 
            AND r.role_name = 'admin' AND r.is_active = TRUE
        )
    );

CREATE POLICY "Admins tienen acceso completo a análisis" ON analysis
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM roles r 
            WHERE r.user_id = current_setting('app.current_user_id', true)::UUID 
            AND r.role_name = 'admin' AND r.is_active = TRUE
        )
    );

CREATE POLICY "Admins tienen acceso completo a reportes" ON reports
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM roles r 
            WHERE r.user_id = current_setting('app.current_user_id', true)::UUID 
            AND r.role_name = 'admin' AND r.is_active = TRUE
        )
    );

-- =====================================================
-- VISTAS OPTIMIZADAS PARA CONSULTAS COMUNES
-- =====================================================

-- Vista principal de reportes con datos clave optimizada
CREATE VIEW v_reportes_principal AS
SELECT 
    -- IDs y claves para filtros
    r.id,
    r.user_id,
    u.username,
    r.game_id,
    r.game_name,
    r.game_slug,
    
    -- Filtros principales
    r.report_status,
    r.report_type,
    r.confidence_score,
    r.primary_genre,
    r.primary_platform,
    r.developer_name,
    r.release_year,
    r.all_genres,
    r.all_platforms,
    r.tags,
    
    -- Fechas y métricas
    r.created_at,
    r.completed_at,
    r.view_count,
    r.download_count,
    r.processing_time_ms,
    
    -- Contenido (lo más importante)
    r.markdown_content,
    r.markdown_summary,
    
    -- URLs para acceso rápido
    r.url_json,
    r.url_markdown,
    r.url_pdf,
    
    -- Disponibilidad de archivos
    r.json_generated,
    r.markdown_generated,
    r.pdf_generated,
    
    -- Metadata clave desde JSONB (optimizado)
    r.report_metadata_jsonb->>'pipeline_version' as pipeline_version,
    r.report_metadata_jsonb->>'synthesis_model' as synthesis_model,
    r.user_metadata_jsonb->>'user_rating' as user_rating,
    r.user_metadata_jsonb->>'user_notes' as user_notes,
    r.user_metadata_jsonb->>'bookmarked' as bookmarked
    
FROM reports r
JOIN users u ON r.user_id = u.id
WHERE r.user_id = current_setting('app.current_user_id', true)::UUID
   OR EXISTS (
       SELECT 1 FROM roles ro 
       WHERE ro.user_id = current_setting('app.current_user_id', true)::UUID 
       AND ro.role_name = 'admin' AND ro.is_active = TRUE
   );

-- Vista de análisis con estado
CREATE VIEW v_analisis_usuario AS
SELECT 
    a.id,
    a.analysis_type,
    a.status,
    a.confidence_score,
    a.created_at,
    a.started_at,
    a.completed_at,
    a.processing_time_ms,
    a.game_id,
    -- Referencia al reporte si existe
    r.id as report_id,
    r.game_name,
    -- Datos clave para seguimiento
    a.pipeline_config->>'priority' as priority,
    a.metrics_jsonb->>'data_sources' as data_sources
FROM analysis a
LEFT JOIN reports r ON a.final_report_id = r.id
WHERE a.user_id = current_setting('app.current_user_id', true)::UUID
ORDER BY a.created_at DESC;

-- Vista de búsqueda de juegos (para filtros y facets)
CREATE VIEW v_juegos_populares AS
SELECT DISTINCT
    game_id,
    game_name,
    game_slug,
    primary_genre,
    all_genres,
    primary_platform, 
    all_platforms,
    developer_name,
    release_year,
    COUNT(DISTINCT user_id) as analyst_count,
    AVG(confidence_score) as avg_confidence,
    MAX(completed_at) as last_analyzed,
    SUM(view_count) as total_views
FROM reports 
WHERE report_status = 'completed'
GROUP BY game_id, game_name, game_slug, primary_genre, all_genres, primary_platform, all_platforms, developer_name, release_year
ORDER BY analyst_count DESC, avg_confidence DESC;

-- =====================================================
-- DATOS DE EJEMPLO PARA TESTING INMEDIATO
-- =====================================================

-- Usuario inicial
INSERT INTO users (email, username, profile_jsonb, settings_jsonb) VALUES
('admin@getsmart.local', 'admin',
 '{"display_name": "System Administrator", "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=admin"}',
 '{"theme": "dark", "notifications": true, "language": "en"}'
);

-- Usuario demo: UUID fijo usado por el pipeline como propietario de los reportes generados.
-- Debe existir para satisfacer reports.user_id NOT NULL cuando no hay sesión real.
INSERT INTO users (id, email, username, profile_jsonb, settings_jsonb) VALUES
('00000000-0000-0000-0000-000000000001', 'demo@getsmart.dev', 'demo',
 '{"display_name": "Demo User", "sso_provider": "demo"}',
 '{"theme": "dark", "language": "en"}'
);

-- Asignar rol admin
INSERT INTO roles (user_id, role_name) VALUES
((SELECT id FROM users WHERE username = 'admin'),
 'admin'
);

-- Asignar rol user al demo
INSERT INTO roles (user_id, role_name) VALUES
('00000000-0000-0000-0000-000000000001', 'user');

-- Ejemplo de reporte completo con .md
INSERT INTO reports (
    user_id, game_id, game_name, game_slug, developer_name, release_year,
    primary_genre, all_genres, primary_platform, all_platforms,
    report_status, report_type, confidence_score,
    search_query, tags,
    markdown_content, markdown_summary,
    url_markdown, url_pdf,
    report_metadata_jsonb, executive_summary_jsonb
) VALUES
(
    (SELECT id FROM users WHERE username = 'admin'),
    uuid_generate_v4(), -- ID único para este juego
    'Elden Ring',
    'elden-ring',
    'FromSoftware',
    2022,
    'RPG',
    ARRAY['RPG', 'Action', 'Adventure'],
    'PC',
    ARRAY['PC', 'PlayStation 5', 'Xbox Series X/S'],
    'completed',
    'comprehensive',
    0.92,
    'FromSoftware open world RPG analysis',
    ARRAY['souls-like', 'open-world', 'fantasy', 'fromsoftware'],
    
    '# Market Analysis: Elden Ring

## Executive Summary
Elden Ring represents a watershed moment in the action-RPG genre, combining FromSoftware''s signature difficulty with unprecedented commercial success.

## Market Performance
- **Launch Sales**: 12 million units in first 3 weeks
- **Current Sales**: 20+ million units globally  
- **Critical Reception**: Universal acclaim (96 Metacritic)
- **User Engagement**: High completion rates for the genre

## Key Success Factors
1. **Open World Innovation**: First FromSoftware title with true open-world design
2. **Brand Recognition**: collaboration with George R.R. Martin
3. **Technical Excellence**: Stable performance across platforms
4. **Accessible Difficulty**: More options than previous Souls games

## Strategic Recommendations
- Monitor competitor responses to open-world + difficulty formula
- Track long-term engagement through DLC and community content  
- Consider similar IP collaborations for future titles

## Risk Assessment
- Market saturation in souls-like genre
- Player burnout on high difficulty games
- Competition from established open-world franchises
',
    
    'Elden Ring market analysis showing 20M+ sales, critical acclaim, and establishing new benchmarks for action-RPG open-world games.',
    
    '/reports/elden-ring/report.md',
    '/reports/elden-ring/report.pdf',
    
    '{"pipeline_version": "3.0.0", "synthesis_model": "gemini-2.5-pro", "input_skills": ["design_art", "user_experience", "technology_systems", "strategy_market"]}',
    
    '{"game_identity": "Elden Ring - FromSoftware''s ambitious open-world action RPG", "market_position": "Market leader in action-RPG genre with 20M+ sales", "key_insights": ["Successfully mainstreamed difficult gameplay", "Set new open-world standards", "Strong IP collaboration success"], "critical_risks": ["Market saturation", "Player fatigue on difficulty"], "recommended_actions": ["Monitor competitor responses", "Invest in DLC content"], "overall_confidence": 0.92}'
);

-- =====================================================
-- CONSULTAS DE EJEMPLO PARA DEMOSTRAR PERFORMANCE
-- =====================================================

/*
-- 1. Búsqueda principal por filtros (muy rápida - columnas indexadas)
SELECT * FROM v_reportes_principal 
WHERE user_id = $1 
  AND (report_status = 'completed' OR report_status IS NULL)
  AND (primary_genre = ANY($2) OR $2 IS NULL)
  AND (release_year >= $3 OR $3 IS NULL)
  AND confidence_score >= $4
ORDER BY completed_at DESC 
LIMIT 20 OFFSET $5;

-- 2. Búsqueda full-text en contenido .md ultra rápida
SELECT id, game_name, ts_headline('english', markdown_content, q) as preview, confidence_score
FROM reports, to_tsquery('english', $1) as q
WHERE user_id = $2 
  AND to_tsvector('english', markdown_content) @@ q
  AND report_status = 'completed'
ORDER BY ts_rank(to_tsvector('english', markdown_content), q) DESC, confidence_score DESC
LIMIT 15;

-- 3. Obtener tags populares para filtros (facets)
SELECT jon.nombre as genre, COUNT(*) as count
FROM reports r, jsonb_array_elements_text(r.all_genres) jon(nombre)
WHERE r.report_status = 'completed'
GROUP BY jon.nombre
ORDER BY count DESC;

-- 4. Dashboard de usuario (agregaciones rápidas)
SELECT 
    COUNT(*) as total_reports,
    COUNT(CASE WHEN report_status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as this_month,
    AVG(confidence_score) as avg_confidence,
    SUM(view_count) as total_views,
    SUM(download_count) as total_downloads
FROM reports 
WHERE user_id = $1;

-- 5. Análisis de rendimiento de pipeline
SELECT 
    analysis_type,
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    AVG(processing_time_ms) as avg_time,
    AVG(confidence_score) as avg_confidence
FROM analysis 
WHERE user_id = $1 
  AND created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY analysis_type
ORDER BY total DESC;
*/

-- =====================================================
-- NOTAS DE IMPLEMENTACIÓN
-- =====================================================
/*
ESTRATEGIA DE COMPACTACIÓN APLICADA:

✅ COLUMNAS CLAVE (nunca en JSONB):
- IDs (uuid references)
- status/type enums  
- Parámetros de búsqueda/filtros
- Fechas principales
- Métricas numéricas básicas
- Textos principales (markdown_content)

✅ DATOS COMPACTADOS EN JSONB:
- Perfiles y preferencias de usuarios
- Configuración detallada de roles
- Datos intermedios del pipeline
- Estructuras completas del final_report_schema
- Métricas detalladas y metadata
- Arrays complejos (preferencias, tags)

✅ PERFORMANCE OPTIMIZED:
- Índices específicos para cada filtro常见
- Full-text search en .md content
- GIN indexes para JSONB queries
- Vistas precompiladas para queries comunes
- Trigger automáticos para estadísticas

✅ EXTENSIBLE:
- Nuevos campos se agregan a JSONB fácilmente
- Schema versioning en metadata_jsonb
- Compatible con data_crud_contract.yaml
- Listo para synthesis_skill pipeline

*/

-- =====================================================
-- FIN: GETSMART LEADER DATABASE DESIGN
-- =====================================================