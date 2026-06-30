import pytest
import asyncio
from app.services.macro_skills.tech_system_skill import TechSystemService
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

@pytest.fixture(autouse=True)
def setup_cache():
    FastAPICache.init(InMemoryBackend())

@pytest.fixture
def service():
    return TechSystemService()

def test_service_initialization(service):
    """Test 1: Service initialization"""
    assert service.skill_id == "tech_systems"
    assert service.skill_name == "Technology and Systems"
    assert service.model_name == "gemini-2.5-flash"
    assert hasattr(service, '_model')

def test_system_prompt(service):
    """Test 2: System prompt loading"""
    prompt = service.system_prompt
    assert "Technology and Systems Analyst" in prompt
    assert "ANALYZE, don't copy" in prompt
    assert len(prompt) > 500

def test_user_prompt_building(service):
    """Test 3: User prompt building from mini context"""
    mini_context = {
        "metadata": {
            "game_id": "test123",
            "game_name": "Test Game"
        },
        "hard_data": {
            "game_engines": ["Unreal Engine 5"],
            "platforms": ["PC", "PS5"],
            "multiplayer_modes": ["Online Co-op"],
            "pc_requirements": {
                "minimum": "OS: Windows 10",
                "recommended": "OS: Windows 11"
            },
            "current_player_count": 5000
        },
        "semantic_data": {
            "technology_performance": {"sources": []},
            "multiplayer_social": {"sources": []},
            "platforms_distribution": {"sources": []}
        },
        "evidence_count": 5,
        "confidence_score": 0.5
    }
    
    prompt = service.build_user_prompt(mini_context)
    assert "Test Game" in prompt
    assert "Unreal Engine 5" in prompt

def test_fallback_output(service):
    """Test 4: Fallback output generation"""
    fallback = service._fallback_output("test123_tech", "Test Tech Game")
    
    required_fields = ["metadata", "analysis", "summary", "confidence"]
    for field in required_fields:
        assert field in fallback
        
    assert fallback["metadata"]["skill_id"] == "tech_systems"
    assert fallback["metadata"]["game_id"] == "test123_tech"
    assert fallback["metadata"]["game_name"] == "Test Tech Game"
    
    analysis_categories = ["technology_performance", "multiplayer_social", "platforms_distribution"]
    for category in analysis_categories:
        assert category in fallback["analysis"]
        assert "error" in fallback["analysis"][category]
        
    assert fallback["confidence"]["overall_score"] == 0.0

@pytest.mark.asyncio
async def test_complete_flow(service):
    """Test 5: Complete flow with fallback (no API key simulation)"""
    mini_context = {
        "metadata": {
            "game_id": "tech-test-001",
            "game_name": "Technology Test Game"
        },
        "hard_data": {
            "game_engines": ["Unity"],
            "platforms": ["PC"],
            "multiplayer_modes": [],
            "pc_requirements": {"minimum": "Basic specs"},
            "current_player_count": 0
        },
        "semantic_data": {
            "technology_performance": {"sources": []},
            "multiplayer_social": {"sources": []},
            "platforms_distribution": {"sources": []}
        },
        "evidence_count": 0,
        "confidence_score": 0.1
    }
    
    result = await service.analyze(mini_context)
    
    assert "metadata" in result
    assert "analysis" in result
    assert "summary" in result
    assert "confidence" in result

def test_router_integration():
    """Test 6: Router integration check"""
    from app.api.skills_routes import skills_router
    routes = [route.path for route in skills_router.routes]
    
    # We check if tech-systems is registered
    # (The previous test showed "/tech-systems" in routes. Wait, the old assert had "/user-experience", "/tech-systems".)
    # The actual paths registered might have the full prefix depending on how it's included, 
    # but the router itself will have "/tech-systems".
    expected_routes = ["/user-experience", "/tech-systems"]
    for expected in expected_routes:
        # Check if any route ends with expected to be safe
        assert any(r.endswith(expected) for r in routes)

def test_schema_compliance(service):
    """Test 7: Schema compliance validation"""
    fallback = service._fallback_output("schema123", "Schema Test Game")
    
    metadata = fallback["metadata"]
    assert metadata["skill_id"] == "tech_systems"
    assert metadata["skill_name"] == "Technology and Systems"
    assert "game_id" in metadata
    assert "game_name" in metadata
    assert "generated_at" in metadata
    assert metadata["model_used"] == "gemini-2.5-flash"
    
    analysis = fallback["analysis"]
    assert len(analysis) == 3
    assert "technology_performance" in analysis
    assert "multiplayer_social" in analysis
    assert "platforms_distribution" in analysis
    
    tech_perf = analysis["technology_performance"]
    tech_required = ["category_id", "category_name", "overview"]
    for field in tech_required:
        assert field in tech_perf
    assert tech_perf["category_id"] == "technology_performance"
    assert tech_perf["category_name"] == "Technology/Performance"
    
    summary = fallback["summary"]
    summary_required = ["technical_philosophy", "standout_strengths", "critical_weaknesses", "engineering_risks"]
    for field in summary_required:
        assert field in summary
        
    confidence = fallback["confidence"]
    conf_required = ["overall_score", "category_scores", "data_quality_notes"]
    for field in conf_required:
        assert field in confidence
