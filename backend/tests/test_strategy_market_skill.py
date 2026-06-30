import pytest
import asyncio
from app.services.macro_skills.strategy_market_skill import StrategyMarketService
from app.tasks.cache_manager import CacheManager

@pytest.fixture
def service():
    return StrategyMarketService()

def test_service_initialization(service):
    """Test 1: Service initialization"""
    assert service.skill_id == "strategy_market"
    assert service.skill_name == "Strategy and Market"
    assert service.model_name == "gemini-2.5-flash"
    assert hasattr(service, '_model')

def test_system_prompt(service):
    """Test 2: System prompt loading"""
    prompt = service.system_prompt
    assert "Strategy and Market Analyst" in prompt
    assert "ANALYZE, don't copy" in prompt
    assert len(prompt) > 500

def test_user_prompt_building(service):
    """Test 3: User prompt building from mini context"""
    mini_context = {
        "metadata": {
            "game_id": "test123_sm",
            "game_name": "Test Strategy Game"
        },
        "hard_data": {
            "genres": ["Strategy", "RPG"],
            "themes": ["Fantasy"],
            "game_modes": ["Single-player"],
            "platforms": ["PC"],
            "release_date": "2026-06-23",
            "developers": ["Test Studio"],
            "publishers": ["Test Publisher"],
            "metacritic": 90,
            "price_usd": 49.99,
            "player_count_peak": 12000,
            "player_count_current": 800,
            "estimated_owners": "500K-1M",
            "estimated_revenue": "$25M",
            "review_score": 0.92,
            "review_count": 5000,
            "dlc_count": 2,
            "dlc_price_total": 19.99,
            "tags": ["Turn-Based Strategy", "RPG"]
        },
        "semantic_data": {
            "audience": {
                "sources": [
                    {
                        "url": "https://example.com/audience",
                        "title": "Audience Profile",
                        "snippet": "Strong appeal to strategy enthusiasts",
                        "platform": "forums"
                    }
                ]
            }
        },
        "evidence_count": 10,
        "confidence_score": 0.7
    }
    
    prompt = service.build_user_prompt(mini_context)
    
    assert "Test Strategy Game" in prompt
    assert "Strategy" in prompt
    assert "Fantasy" in prompt
    assert "Strong appeal to strategy enthusiasts" in prompt

def test_fallback_output(service):
    """Test 4: Fallback output generation"""
    fallback = service._fallback_output("test123_sm", "Test Strategy Game")
    
    required_fields = ["metadata", "analysis", "summary", "confidence"]
    for field in required_fields:
        assert field in fallback
        
    assert fallback["metadata"]["skill_id"] == "strategy_market"
    assert fallback["metadata"]["game_id"] == "test123_sm"
    assert fallback["metadata"]["game_name"] == "Test Strategy Game"
    
    analysis_categories = [
        "audience", "business_model", "retention_live_ops",
        "production_business", "marketing", "cultural_impact"
    ]
    for category in analysis_categories:
        assert category in fallback["analysis"]
        assert "error" in fallback["analysis"][category]
        
    assert fallback["confidence"]["overall_score"] == 0.0

def test_router_integration():
    """Test 5: Router integration check"""
    from app.api.skills_routes import skills_router
    routes = [route.path for route in skills_router.routes]
    expected_routes = ["/skills/user-experience", "/skills/tech-systems", "/skills/strategy-market"]
    
    for expected in expected_routes:
        assert expected in routes

def test_schema_compliance(service):
    """Test 6: Schema compliance validation"""
    fallback = service._fallback_output("schema_sm", "Schema Strategy Game")
    
    metadata = fallback["metadata"]
    assert metadata["skill_id"] == "strategy_market"
    assert metadata["skill_name"] == "Strategy and Market"
    assert "game_id" in metadata
    assert "game_name" in metadata
    assert "generated_at" in metadata
    assert metadata["model_used"] == "gemini-2.5-flash"
    
    analysis = fallback["analysis"]
    assert len(analysis) == 6
    categories = [
        "audience", "business_model", "retention_live_ops",
        "production_business", "marketing", "cultural_impact"
    ]
    for category in categories:
        assert category in analysis
        assert analysis[category]["category_id"] == category
        assert "category_name" in analysis[category]
    
    summary = fallback["summary"]
    summary_required = [
        "strategic_positioning", "standout_strengths", "critical_weaknesses",
        "market_opportunities", "threats_and_risks", "competitive_positioning",
        "future_outlook"
    ]
    for field in summary_required:
        assert field in summary
        
    confidence = fallback["confidence"]
    conf_required = ["overall_score", "category_scores", "data_quality_notes"]
    for field in conf_required:
        assert field in confidence

@pytest.mark.asyncio
async def test_complete_flow(service):
    """Test 7: Complete flow with fallback (no API key simulation)"""
    try:
        await CacheManager.init_cache()
    except Exception:
        pass
        
    mini_context = {
        "metadata": {
            "game_id": "sm-test-001",
            "game_name": "Strategy Test Game"
        },
        "hard_data": {
            "genres": ["RPG"],
            "platforms": ["PC"],
            "developers": ["Dev"],
            "publishers": ["Pub"],
            "tags": []
        },
        "semantic_data": {
            "audience": {"sources": []},
            "business_model": {"sources": []},
            "retention_live_ops": {"sources": []},
            "production_business": {"sources": []},
            "marketing": {"sources": []},
            "cultural_impact": {"sources": []}
        },
        "evidence_count": 0,
        "confidence_score": 0.1
    }
    
    result = await service.analyze(mini_context)
    
    assert "metadata" in result
    assert "analysis" in result
    assert "summary" in result
    assert "confidence" in result
