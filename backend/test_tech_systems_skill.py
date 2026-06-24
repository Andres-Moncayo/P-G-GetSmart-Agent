"""
Test script for TechSystems Skill implementation validation.

This script tests:
1. Service initialization
2. System prompt generation
3. Input parsing
4. Fallback output generation
5. Integration with FastAPI router
"""

import asyncio
import json
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.macro_skills.tech_system_skill import TechSystemService


def test_service_initialization():
    """Test 1: Service initialization"""
    print("=== Test 1: Service Initialization ===")
    try:
        service = TechSystemService()
        assert service.skill_id == "tech_systems"
        assert service.skill_name == "Technology and Systems"
        assert service.model_name == "gemini-2.5-flash"
        assert hasattr(service, '_client')
        print("✅ Service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False


def test_system_prompt():
    """Test 2: System prompt loading"""
    print("\n=== Test 2: System Prompt ===")
    try:
        service = TechSystemService()
        prompt = service.system_prompt
        assert "Technology and Systems Analyst" in prompt
        assert "ANALYZE, don't copy" in prompt
        assert len(prompt) > 500  # Basic length check
        print("✅ System prompt loaded successfully")
        return True
    except Exception as e:
        print(f"❌ System prompt test failed: {e}")
        return False


def test_user_prompt_building():
    """Test 3: User prompt building from mini context"""
    print("\n=== Test 3: User Prompt Building ===")
    try:
        service = TechSystemService()
        
        # Mock mini context
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
                "technology_performance": {
                    "sources": [
                        {
                            "url": "https://example.com/tech",
                            "title": "Technical Analysis",
                            "snippet": "Game uses advanced rendering",
                            "platform": "github"
                        }
                    ]
                },
                "multiplayer_social": {
                    "sources": []
                },
                "platforms_distribution": {
                    "sources": []
                }
            },
            "evidence_count": 5,
            "confidence_score": 0.75
        }
        
        prompt = service.build_user_prompt(mini_context)
        
        # Verify key components are present
        assert "Test Game" in prompt
        assert "Unreal Engine 5" in prompt
        assert "Online Co-op" in prompt
        assert "ANALYSIS TASKS" in prompt
        assert "SYNTHESIS REQUIREMENTS" in prompt
        assert "OUTPUT REQUIREMENTS" in prompt
        
        print("✅ User prompt building successful")
        print(f"   Prompt length: {len(prompt)} characters")
        return True
    except Exception as e:
        print(f"❌ User prompt building failed: {e}")
        return False


def test_fallback_output():
    """Test 4: Fallback output generation"""
    print("\n=== Test 4: Fallback Output ===")
    try:
        service = TechSystemService()
        fallback = service._fallback_output("test123", "Test Game")
        
        # Check required top-level fields
        required_fields = ["metadata", "analysis", "summary", "confidence"]
        for field in required_fields:
            assert field in fallback, f"Missing field: {field}"
        
        # Check metadata
        assert fallback["metadata"]["skill_id"] == "tech_systems"
        assert fallback["metadata"]["game_id"] == "test123"
        assert fallback["metadata"]["game_name"] == "Test Game"
        
        # Check analysis structure
        analysis_categories = ["technology_performance", "multiplayer_social", "platforms_distribution"]
        for category in analysis_categories:
            assert category in fallback["analysis"], f"Missing analysis category: {category}"
            assert "error" in fallback["analysis"][category], f"Missing error flag in {category}"
        
        # Check confidence scores
        assert fallback["confidence"]["overall_score"] == 0.0
        assert all(score == 0.0 for score in fallback["confidence"]["category_scores"].values())
        
        print("✅ Fallback output generation successful")
        return True
    except Exception as e:
        print(f"❌ Fallback output test failed: {e}")
        return False


async def test_complete_flow():
    """Test 5: Complete flow with fallback (no API key simulation)"""
    print("\n=== Test 5: Complete Flow ===")
    try:
        service = TechSystemService()
        
        # Mock mini context with minimal data for testing
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
        
        # This will likely fail due to missing API key, but should produce fallback
        result = await service.analyze(mini_context)
        
        # Verify fallback structure
        assert "metadata" in result
        assert "analysis" in result
        assert "summary" in result
        assert "confidence" in result
        
        print("✅ Complete flow successful (likely used fallback due to API key)")
        print(f"   Skill ID: {result['metadata']['skill_id']}")
        print(f"   Game Name: {result['metadata']['game_name']}")
        return True
    except Exception as e:
        print(f"❌ Complete flow test failed: {e}")
        return False


def test_router_integration():
    """Test 6: Router integration check"""
    print("\n=== Test 6: Router Integration ===")
    try:
        # Import router to check it loads correctly
        from app.api.skills_routes import skills_router
        
        # Check routes
        routes = [route.path for route in skills_router.routes]
        expected_routes = ["/user-experience", "/tech-systems"]
        
        for expected in expected_routes:
            assert expected in routes, f"Missing route: {expected}"
        
        print("✅ Router integration successful")
        print(f"   Available routes: {routes}")
        return True
    except Exception as e:
        print(f"❌ Router integration test failed: {e}")
        return False


def validate_schema_compliance():
    """Test 7: Schema compliance validation"""
    print("\n=== Test 7: Schema Compliance ===")
    try:
        service = TechSystemService()
        fallback = service._fallback_output("schema123", "Schema Test Game")
        
        # Validate against key schema requirements from tech_systems_skill.yaml
        
        # 1. Metadata structure
        metadata = fallback["metadata"]
        assert "skill_id" in metadata and metadata["skill_id"] == "tech_systems"
        assert "skill_name" in metadata and metadata["skill_name"] == "Technology and Systems"
        assert "game_id" in metadata
        assert "game_name" in metadata
        assert "generated_at" in metadata
        assert "model_used" in metadata and metadata["model_used"] == "gemini-2.5-flash"
        
        # 2. Analysis structure with 3 categories
        analysis = fallback["analysis"]
        assert len(analysis) == 3  # Exactly 3 categories
        assert "technology_performance" in analysis
        assert "multiplayer_social" in analysis
        assert "platforms_distribution" in analysis
        
        # 3. Technology/Performance category structure
        tech_perf = analysis["technology_performance"]
        tech_required = ["category_id", "category_name", "overview"]
        for field in tech_required:
            assert field in tech_perf, f"Missing {field} in technology_performance"
        assert tech_perf["category_id"] == "technology_performance"
        assert tech_perf["category_name"] == "Technology/Performance"
        
        # 4. Multiplayer/Social category structure
        multiplayer = analysis["multiplayer_social"]
        multi_required = ["category_id", "category_name", "overview"]
        for field in multi_required:
            assert field in multiplayer, f"Missing {field} in multiplayer_social"
        assert multiplayer["category_id"] == "multiplayer_social"
        assert multiplayer["category_name"] == "Multiplayer/Social"
        
        # 5. Platforms/Distribution category structure
        platforms = analysis["platforms_distribution"]
        platforms_required = ["category_id", "category_name", "overview"]
        for field in platforms_required:
            assert field in platforms, f"Missing {field} in platforms_distribution"
        assert platforms["category_id"] == "platforms_distribution"
        assert platforms["category_name"] == "Platforms/Distribution"
        
        # 6. Summary structure
        summary = fallback["summary"]
        summary_required = ["technical_philosophy", "standout_strengths", "critical_weaknesses", "engineering_risks"]
        for field in summary_required:
            assert field in summary, f"Missing {field} in summary"
        
        # 7. Confidence structure
        confidence = fallback["confidence"]
        conf_required = ["overall_score", "category_scores", "data_quality_notes"]
        for field in conf_required:
            assert field in confidence, f"Missing {field} in confidence"
        
        # 8. Confidence score ranges
        assert 0.0 <= confidence["overall_score"] <= 1.0
        for category_score in confidence["category_scores"].values():
            assert 0.0 <= category_score <= 1.0
        
        print("✅ Schema compliance validation successful")
        return True
    except Exception as e:
        print(f"❌ Schema compliance test failed: {e}")
        return False


async def main():
    """Run all validation tests"""
    print("🚀 Starting TechSystems Skill Validation Tests")
    print("=" * 50)
    
    tests = [
        ("Service Initialization", test_service_initialization),
        ("System Prompt Loading", test_system_prompt),
        ("User Prompt Building", test_user_prompt_building),
        ("Fallback Output Generation", test_fallback_output),
        ("Complete Flow", test_complete_flow),
        ("Router Integration", test_router_integration),
        ("Schema Compliance", validate_schema_compliance),
    ]
    
    results = []
    for test_name, test_func in tests:
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - TechSystems Skill implementation is ready!")
    else:
        print("⚠️  Some tests failed - review implementation")
    
    return failed == 0


if __name__ == "__main__":
    asyncio.run(main())