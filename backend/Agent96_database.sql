-- ============================================================
-- GetSmart Agent Database Schema - REDISEÑADO V2.0
-- Based on master_json_schema.yaml, final_report_schema.json, ui_login_contract.yaml
-- ============================================================

-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. USERS TABLE (Enhanced from ui_login_contract.yaml)
-- ============================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT true,
    
    -- SSO Provider fields
    google_id VARCHAR(255) UNIQUE,
    provider VARCHAR(50) DEFAULT 'local', -- 'local', 'google', etc.
    
    -- Profile preferences (from ui_contract)
    preferences JSONB DEFAULT '{}',
    
    -- Audit fields
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 2. GAMES TABLE (Rediseñado desde master_json_schema.yaml)
-- ============================================================
CREATE TABLE games (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Basic game info
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    release_year INTEGER,
    
    -- External API IDs
    igdb_id INTEGER UNIQUE,
    rawg_id INTEGER UNIQUE,
    steam_app_id INTEGER UNIQUE,
    
    -- Basic metadata
    summary TEXT,
    storyline TEXT,
    aliases TEXT[], -- Array of alternative names
    
    -- Visual assets
    cover_url TEXT,
    screenshots JSONB,
    videos JSONB,
    artworks JSONB,
    
    -- Rating metrics
    igdb_total_rating DECIMAL(3,1),
    igdb_rating_count INTEGER,
    rawg_metacritic INTEGER,
    rawg_ratings_count INTEGER,
    
    -- Steam-specific data
    steam_is_free BOOLEAN DEFAULT false,
    steam_price_overview JSONB,
    steam_dlc_count INTEGER DEFAULT 0,
    
    -- SteamSpy analytics
    steamspy_owners_range VARCHAR(20),
    steamspy_average_playtime INTEGER,
    steamspy_median_playtime INTEGER,
    steamspy_price INTEGER,
    
    -- Support and requirements
    supported_languages TEXT[],
    system_requirements JSONB,
    controller_support BOOLEAN DEFAULT false,
    public BOOLEAN DEFAULT true,
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 3. IGDB DETAILED DATA TABLE
-- ============================================================
CREATE TABLE igdb_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    
    -- Categorical data
    genres TEXT[],
    themes TEXT[],
    game_modes TEXT[],
    player_perspectives TEXT[],
    multiplayer_modes TEXT[],
    
    -- Engine and technical
    game_engines JSONB,
    
    -- Companies (involved_companies)
    involved_companies JSONB, -- Array of {name, role, type}
    
    -- Platform availability
    platforms TEXT[],
    language_supports JSONB,
    
    -- Social features
    online_coop BOOLEAN DEFAULT false,
    offline_coop BOOLEAN DEFAULT false,
    lan_coop BOOLEAN DEFAULT false,
    split_screen BOOLEAN DEFAULT false,
    cross_play BOOLEAN DEFAULT false,
    
    -- Community metrics
    hypes INTEGER DEFAULT 0,
    follows INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 4. RAWG DETAILED DATA TABLE
-- ============================================================
CREATE TABLE rawg_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    
    -- Ratings data
    esrb_rating VARCHAR(20),
    ratings JSONB, -- Array of {title, count, percent}
    reviews_text_count INTEGER DEFAULT 0,
    
    -- User engagement
    added INTEGER DEFAULT 0,
    added_by_status JSONB,
    suggestions_count INTEGER DEFAULT 0,
    
    -- Categories and tags
    categories TEXT[],
    tags TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 5. PLATFORMS TABLE (Simplified)
-- ============================================================
CREATE TABLE platforms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 6. GAME-PLATFORM RELATIONSHIP
-- ============================================================
CREATE TABLE game_platforms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    platform_id INTEGER REFERENCES platforms(id) ON DELETE CASCADE,
    UNIQUE(game_id, platform_id)
);

-- ============================================================
-- 7. REPORTS TABLE (Rediseñado desde final_report_schema.json)
-- ============================================================
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Report metadata (from final_report_schema)
    report_classification VARCHAR(50) NOT NULL CHECK (report_classification IN ('comprehensive', 'partial', 'low_confidence', 'error')),
    pipeline_version VARCHAR(20) DEFAULT '3.0.0',
    synthesis_model VARCHAR(50) DEFAULT 'gemini-2.5-pro',
    
    -- Master-JSON metadata (from master_json_schema)
    workers_executed TEXT[],
    workers_failed TEXT[],
    total_evidence_count INTEGER DEFAULT 0,
    overall_confidence_score DECIMAL(4,3) CHECK (overall_confidence_score >= 0.0 AND overall_confidence_score <= 1.0),
    input_confidence_range JSONB, -- {min: 0.0, max: 1.0}
    
    -- Pipeline phases and status
    status VARCHAR(50) DEFAULT 'pending',
    current_phase VARCHAR(50) DEFAULT 'initial',
    progress_percent INTEGER DEFAULT 0 CHECK (progress_percent >= 0 AND progress_percent <= 100),
    
    -- User-editable metadata (the ONLY fields users can edit)
    tags TEXT[] DEFAULT '{}',
    notes TEXT,
    
    -- Report content (stored as structured data)
    executive_summary JSONB, -- {game_identity, market_position, key_insights, critical_risks, recommended_actions, overall_confidence}
    thematic_analysis JSONB, -- 17 partition categories with detailed analysis
    cross_cutting_insights JSONB,
    strategic_recommendations JSONB,
    risk_assessment JSONB,
    appendices JSONB,
    confidence_metrics JSONB,
    
    -- Pipeline metadata (system-managed)
    pipeline_metadata JSONB, -- worker results, timestamps, etc.
    master_json_storage JSONB, -- The full master JSON from pipeline
    
    -- Output files and formats
    outputs JSONB, -- {markdown_url, pdf_url, json_url} etc.
    output_formats TEXT[], -- ['json', 'markdown', 'pdf_html']
    
    -- File storage references
    generated_report_path TEXT,
    cloud_storage_urls JSONB, -- {markdown: "url", pdf: "url", json: "url"}
    
    -- Tracking and analytics
    views_count INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMPTZ,
    
    -- Audit fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT reports_owner_owned UNIQUE (game_id, owner_id) -- One report per game per user
);

-- ============================================================
-- 8. PARTITION ANALYSIS CACHE TABLE
-- For storing the 17 thematic categories analysis
-- ============================================================
CREATE TABLE report_partitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
    
    -- 17 partition categories
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'gameplay', 'level_design', 'narrative', 'art_direction', 'sound_design',
        'ui_ux', 'accessibility', 'localization', 'technology_performance',
        'multiplayer_social', 'platforms_distribution', 'audience',
        'business_model', 'retention_live_ops', 'monetization', 'technical_infrastructure',
        'market_competitive'
    )),
    
    -- Analysis data
    analysis_content JSONB,
    evidence_count INTEGER DEFAULT 0,
    confidence_score DECIMAL(4,3) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    source_macro_skill VARCHAR(50), -- Which worker produced this
    source_path TEXT, -- Path to data in mini-contexts
    
    -- Metrics
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(report_id, category)
);

-- ============================================================
-- 9. ANALYTICS AND METADATA TABLES
-- ============================================================

-- MASTER-JSON STORAGE (full pipeline results)
CREATE TABLE master_json_store (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    game_id UUID REFERENCES games(id) ON DELETE CASCADE,
    master_json JSONB NOT NULL, -- The complete master JSON
    worker_contexts JSONB, -- Individual mini-contexts
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AUDIT LOG
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ANALYTICS METRICS
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    game_id UUID REFERENCES games(id) ON DELETE SET NULL,
    report_id UUID REFERENCES reports(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 10. ROW LEVEL SECURITY (RLS) SETUP
-- ============================================================

-- Enable RLS on tables with user data
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_partitions ENABLE ROW LEVEL SECURITY;

-- Users own reports policy
CREATE POLICY users_own_reports ON reports
    FOR ALL TO authenticated_users
    USING (owner_id = current_setting('app.current_user_id')::uuid)
    WITH CHECK (owner_id = current_setting('app.current_user_id')::uuid);

-- Users their own partitions policy
CREATE POLICY users_own_partitions ON report_partitions
    FOR ALL TO authenticated_users
    USING (
        EXISTS (
            SELECT 1 FROM reports 
            WHERE reports.id = report_partitions.report_id 
            AND reports.owner_id = current_setting('app.current_user_id')::uuid
        )
    );

-- UPDATE RESTRICTION: Only allow user-editable fields
CREATE POLICY users_update_own_metadata_reports ON reports
    FOR UPDATE TO authenticated_users
    USING (
        owner_id = current_setting('app.current_user_id')::uuid
    )
    WITH CHECK (
        (game_id IS NOT DISTINCT FROM OLD.game_id) AND
        (status IS NOT DISTINCT FROM OLD.status) AND
        (current_phase IS NOT DISTINCT FROM OLD.current_phase) AND
        (progress_percent IS NOT DISTINCT FROM OLD.progress_percent) AND
        (report_classification IS NOT DISTINCT FROM OLD.report_classification) AND
        (pipeline_version IS NOT DISTINCT FROM OLD.pipeline_version) AND
        (synthesis_model IS NOT DISTINCT FROM OLD.synthesis_model) AND
        (overall_confidence_score IS NOT DISTINCT FROM OLD.overall_confidence_score) AND
        (executive_summary IS NOT DISTINCT FROM OLD.executive_summary) AND
        (thematic_analysis IS NOT DISTINCT FROM OLD.thematic_analysis) AND
        (strategic_recommendations IS NOT DISTINCT FROM OLD.strategic_recommendations) AND
        (risk_assessment IS NOT DISTINCT FROM OLD.risk_assessment) AND
        (appendices IS NOT DISTINCT FROM OLD.appendices) AND
        (pipeline_metadata IS NOT DISTINCT FROM OLD.pipeline_metadata) AND
        (master_json_storage IS NOT DISTINCT FROM OLD.master_json_storage) AND
        (outputs IS NOT DISTINCT FROM OLD.outputs) AND
        (output_formats IS NOT DISTINCT FROM OLD.output_formats)
        -- ALLOWED TO CHANGE: only tags and notes
    );

-- DELETE RESTRICTION: Only owners can delete their reports
CREATE POLICY users_delete_own_reports ON reports
    FOR DELETE TO authenticated_users
    USING (owner_id = current_setting('app.current_user_id')::uuid);

-- BLOCK DIRECT INSERT - Reports only created by pipeline
CREATE POLICY block_direct_reports_insert ON reports
    FOR INSERT TO authenticated_users
    WITH CHECK (false);

-- ============================================================
-- 11. INDEXES FOR PERFORMANCE
-- ============================================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_google_id ON users(google_id);

-- Games  
CREATE INDEX idx_games_name ON games(name);
CREATE INDEX idx_games_slug ON games(slug);
CREATE INDEX idx_games_release_year ON games(release_year);
CREATE INDEX idx_games_igdb_id ON games(igdb_id);
CREATE INDEX idx_games_rawg_id ON games(rawg_id);
CREATE INDEX idx_games_steam_app_id ON games(steam_app_id);

-- IGDB metadata
CREATE INDEX idx_igdb_game_id ON igdb_metadata(game_id);
CREATE INDEX idx_igdb_genres ON igdb_metadata USING GIN(genres);
CREATE INDEX idx_igdb_platforms ON igdb_metadata USING GIN(platforms);

-- RAWG metadata
CREATE INDEX idx_rawg_game_id ON rawg_metadata(game_id);
CREATE INDEX idx_rawg_categories ON rawg_metadata USING GIN(categories));
CREATE INDEX idx_rawg_tags ON rawg_metadata USING GIN(tags);

-- Reports
CREATE INDEX idx_reports_game_id ON reports(game_id);
CREATE INDEX idx_reports_owner_id ON reports(owner_id);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_classification ON reports(report_classification);
CREATE INDEX idx_reports_created_at ON reports(created_at);
CREATE INDEX idx_reports_tags ON reports USING GIN(tags);
CREATE INDEX idx_reports_progress ON reports(progress_percent);
CREATE INDEX idx_reports_confidence ON reports(overall_confidence_score);

-- Report partitions
CREATE INDEX idx_report_partitions_report_id ON report_partitions(report_id);
CREATE INDEX idx_report_partitions_category ON report_partitions(category);
CREATE INDEX idx_report_partitions_confidence ON report_partitions(confidence_score);

-- Analytics
CREATE INDEX idx_analytics_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_created_at ON analytics_events(created_at);

-- Full-text search
CREATE INDEX idx_games_name_fts ON games USING GIN(to_tsvector('english', name));
CREATE INDEX idx_reports_notes_fts ON reports USING GIN(to_tsvector('english', COALESCE(notes, '')));
CREATE INDEX idx_reports_tags_fts ON reports USING GIN(tags);

-- ============================================================
-- 12. TRIGGERS AND FUNCTIONS
-- ============================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_games_updated_at BEFORE UPDATE ON games
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_igdb_metadata_updated_at BEFORE UPDATE ON igdb_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rawg_metadata_updated_at BEFORE UPDATE ON rawg_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_report_partitions_updated_at BEFORE UPDATE ON report_partitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (user_id, action, resource_type, resource_id, old_values, new_values)
    VALUES (
        current_setting('app.current_user_id', true)::uuid,
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id::uuid, OLD.id::uuid),
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers
CREATE TRIGGER audit_reports_trigger
    AFTER INSERT OR UPDATE OR DELETE ON reports
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- ============================================================
-- 13. VIEWS FOR COMPLEX QUERIES
-- ============================================================

-- Enhanced games view with metadata
CREATE VIEW game_details_view AS
SELECT 
    g.*,
    ig.genres,
    ig.platforms,
    ig.themes,
    ig.game_modes,
    r.metadata_specific,
    esrb.rawg_metacritic
FROM games g
LEFT JOIN igdb_metadata ig ON g.id = ig.game_id
LEFT JOIN rawg_metadata r ON g.id = r.game_id;

-- Reports with game and user details
CREATE VIEW reports_detailed_view AS
SELECT 
    r.*,
    g.name as game_name,
    g.release_year as game_release_year,
    u.username as owner_username,
    u.full_name as owner_full_name
FROM reports r
JOIN games g ON r.game_id = g.id  
JOIN users u ON r.owner_id = u.id;

-- Reports summary view for facets
CREATE MATERIALIZED VIEW report_facets AS
SELECT 
    COUNT(*) as total_reports,
    COUNT(DISTINCT r.game_id) as unique_games,
    COUNT(DISTINCT r.owner_id) as unique_users,
    MIN(r.created_at) as earliest_report,
    MAX(r.created_at) as latest_report,
    AVG(r.overall_confidence_score) as avg_confidence,
    jsonb_agg(
        DISTINCT jsonb_build_object(
            'genre', ig.genres[1],
            'platform', ig.platforms[1]
        )
    ) filter (where ig.genres[1] IS NOT NULL) as sample_facets
FROM reports r
LEFT JOIN igdb_metadata ig ON r.game_id = ig.game_id
WHERE r.status = 'completed';

-- Refresh materialized view periodically
CREATE OR REPLACE FUNCTION refresh_report_facets()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY report_facets;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 14. ROLES AND PERMISSIONS
-- ============================================================

-- Create roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated_users') THEN
        CREATE ROLE authenticated_users;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_service') THEN
        CREATE ROLE app_service;
    END IF;
END
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA public TO authenticated_users;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO authenticated_users;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated_users;

-- Service account permissions (for pipeline, etc.)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_service;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_service;

-- ============================================================
-- 15. SAMPLE DATA (Optional)
-- ============================================================

-- Insert sample platforms
INSERT INTO platforms (name, slug) VALUES
('PC', 'pc'),
('PlayStation 5', 'playstation-5'),
('Xbox Series X/S', 'xbox-series-xs'),
('Nintendo Switch', 'nintendo-switch');

-- ============================================================
-- 16. CONSTRAINTS AND VALIDATIONS
-- ============================================================

-- Add reasonable constraints
ALTER TABLE games ADD CONSTRAINT games_release_year_check 
    CHECK (release_year >= 1970 AND release_year <= 2100);

ALTER TABLE reports ADD CONSTRAINT reports_progress_positive 
    CHECK (progress_percent >= 0 AND progress_percent <= 100);

ALTER TABLE reports ADD CONSTRAINT reports_confidence_range 
    CHECK (overall_confidence_score >= 0.0 AND overall_confidence_score <= 1.0);

-- ============================================================
-- 17. PERFORMANCE TUNING
-- ============================================================

-- Set table statistics target for better query planning
ALTER TABLE reports ALTER COLUMN created_at SET STATISTICS 1000;
ALTER TABLE games ALTER COLUMN created_at SET STATISTICS 1000;

-- Enable parallel query execution for large scans
SET max_parallel_workers_per_gather = 4;

-- ============================================================
-- DATABASE SETUP COMPLETE
-- ============================================================

-- Log setup completion
DO $$
BEGIN
    RAISE NOTICE 'GetSmart Agent Database V2.0 setup completed successfully';
    RAISE NOTICE '- % tables created', (
        SELECT count(*) FROM information_schema.tables 
        WHERE table_schema = 'public'
    );
    RAISE NOTICE '- Row Level Security enabled on user data tables';
    RAISE NOTICE '- Comprehensive indexes for performance added';
    RAISE NOTICE '- Triggers for audit and timestamps added';
    RAISE NOTICE '- Views for complex queries created';
    RAISE NOTICE '- Based on master_json_schema.yaml + final_report_schema.json + ui_contract';
END $$;