"""
Test script for StrategyMarket Skill implementation validation.

This script tests:
1. Service initialization
2. System prompt generation
3. Input parsing / User prompt building
4. Fallback output generation
5. Integration with FastAPI router
6. Schema compliance validation
7. Complete flow
"""

import asyncio
import json
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.macro_skills.strategy_market_skill import StrategyMarketService
from app.tasks.cache_manager import CacheManager


def test_service_initialization():
    """Test 1: Service initialization"""
    print("=== Test 1: Service Initialization ===")
    try:
        service = StrategyMarketService()
        assert service.skill_id == "strategy_market"
        assert service.skill_name == "Strategy and Market"
        assert service.model_name == "gemini-2.5-flash"
        assert hasattr(service, '_model')
        print("[PASS] Service initialized successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Service initialization failed: {e}")
        return False


def test_system_prompt():
    """Test 2: System prompt loading"""
    print("\n=== Test 2: System Prompt ===")
    try:
        service = StrategyMarketService()
        prompt = service.system_prompt
        assert "Strategy and Market Analyst" in prompt
        assert "ANALYZE, don't copy" in prompt
        assert len(prompt) > 500  # Basic length check
        print("[PASS] System prompt loaded successfully")
        return True
    except Exception as e:
        print(f"[FAIL] System prompt test failed: {e}")
        return False


def test_user_prompt_building():
    """Test 3: User prompt building from mini context"""
    print("\n=== Test 3: User Prompt Building ===")
    try:
        service = StrategyMarketService()
        
        # Mock mini context
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
                },
                "business_model": {"sources": []},
                "retention_live_ops": {"sources": []},
                "production_business": {"sources": []},
                "marketing": {"sources": []},
                "cultural_impact": {"sources": []}
            },
            "evidence_count": 8,
            "confidence_score": 0.85
        }
        
        prompt = service.build_user_prompt(mini_context)
        
        # Verify key components are present
        assert "Test Strategy Game" in prompt
        assert "Turn-Based Strategy" in prompt
        assert "Estimated Owners: 500K-1M" in prompt
        assert "Audience Profile" in prompt
        assert "CONTEXT METRICS" in prompt
        
        print("[PASS] User prompt building successful")
        print(f"   Prompt length: {len(prompt)} characters")
        return True
    except Exception as e:
        print(f"[FAIL] User prompt building failed: {e}")
        return False


def test_fallback_output():
    """Test 4: Fallback output generation"""
    print("\n=== Test 4: Fallback Output ===")
    try:
        service = StrategyMarketService()
        fallback = service._fallback_output("test123_sm", "Test Strategy Game")
        
        # Check required top-level fields
        required_fields = ["metadata", "analysis", "summary", "confidence"]
        for field in required_fields:
            assert field in fallback, f"Missing field: {field}"
        
        # Check metadata
        assert fallback["metadata"]["skill_id"] == "strategy_market"
        assert fallback["metadata"]["game_id"] == "test123_sm"
        assert fallback["metadata"]["game_name"] == "Test Strategy Game"
        
        # Check analysis structure (6 categories)
        analysis_categories = [
            "audience", "business_model", "retention_live_ops",
            "production_business", "marketing", "cultural_impact"
        ]
        for category in analysis_categories:
            assert category in fallback["analysis"], f"Missing analysis category: {category}"
            assert "error" in fallback["analysis"][category], f"Missing error flag in {category}"
        
        # Check confidence scores
        assert fallback["confidence"]["overall_score"] == 0.0
        assert all(score == 0.0 for score in fallback["confidence"]["category_scores"].values())
        
        print("[PASS] Fallback output generation successful")
        return True
    except Exception as e:
        print(f"[FAIL] Fallback output test failed: {e}")
        return False


def test_router_integration():
    """Test 5: Router integration check"""
    print("\n=== Test 5: Router Integration ===")
    try:
        # Import router to check it loads correctly
        from app.api.skills_routes import skills_router
        
        # Check routes
        routes = [route.path for route in skills_router.routes]
        expected_routes = ["/skills/user-experience", "/skills/tech-systems", "/skills/strategy-market"]
        
        for expected in expected_routes:
            assert expected in routes, f"Missing route: {expected}"
        
        print("[PASS] Router integration successful")
        print(f"   Available routes: {routes}")
        return True
    except Exception as e:
        print(f"[FAIL] Router integration test failed: {e}")
        return False


def validate_schema_compliance():
    """Test 6: Schema compliance validation"""
    print("\n=== Test 6: Schema Compliance ===")
    try:
        service = StrategyMarketService()
        fallback = service._fallback_output("schema_sm", "Schema Strategy Game")
        
        # 1. Metadata structure
        metadata = fallback["metadata"]
        assert "skill_id" in metadata and metadata["skill_id"] == "strategy_market"
        assert "skill_name" in metadata and metadata["skill_name"] == "Strategy and Market"
        assert "game_id" in metadata
        assert "game_name" in metadata
        assert "generated_at" in metadata
        assert "model_used" in metadata and metadata["model_used"] == "gemini-2.5-flash"
        
        # 2. Analysis structure with 6 categories
        analysis = fallback["analysis"]
        assert len(analysis) == 6  # Exactly 6 categories
        categories = [
            "audience", "business_model", "retention_live_ops",
            "production_business", "marketing", "cultural_impact"
        ]
        for category in categories:
            assert category in analysis
            assert analysis[category]["category_id"] == category
            assert "category_name" in analysis[category]
        
        # 3. Summary structure
        summary = fallback["summary"]
        summary_required = [
            "strategic_positioning", "standout_strengths", "critical_weaknesses",
            "market_opportunities", "threats_and_risks", "competitive_positioning",
            "future_outlook"
        ]
        for field in summary_required:
            assert field in summary, f"Missing {field} in summary"
        
        # 4. Confidence structure
        confidence = fallback["confidence"]
        conf_required = ["overall_score", "category_scores", "data_quality_notes"]
        for field in conf_required:
            assert field in confidence, f"Missing {field} in confidence"
        
        # 5. Confidence score ranges
        assert 0.0 <= confidence["overall_score"] <= 1.0
        for category_score in confidence["category_scores"].values():
            assert 0.0 <= category_score <= 1.0
        
        print("[PASS] Schema compliance validation successful")
        return True
    except Exception as e:
        print(f"[FAIL] Schema compliance test failed: {e}")
        return False


async def test_complete_flow():
    """Test 7: Complete flow with fallback (no API key simulation)"""
    print("\n=== Test 7: Complete Flow ===")
    try:
        service = StrategyMarketService()
        
        # Initialize cache first
        try:
            await CacheManager.init_cache()
        except Exception:
            pass # Avoid crash if already initialized
        
        # Mock mini context with minimal data for testing
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
        
        # This will run analyze and might fallback if API key is not configured or fails
        result = await service.analyze(mini_context)
        
        # Verify result structure
        assert "metadata" in result
        assert "analysis" in result
        assert "summary" in result
        assert "confidence" in result
        
        print("[PASS] Complete flow successful (likely fallback due to API key or success if configured)")
        print(f"   Skill ID: {result['metadata']['skill_id']}")
        print(f"   Game Name: {result['metadata']['game_name']}")
        return True
    except Exception as e:
        print(f"[FAIL] Complete flow test failed: {e}")
        return False


async def main():
    """Run all validation tests"""
    print("Starting StrategyMarket Skill Validation Tests")
    print("=" * 50)
    
    tests = [
        ("Service Initialization", test_service_initialization),
        ("System Prompt Loading", test_system_prompt),
        ("User Prompt Building", test_user_prompt_building),
        ("Fallback Output Generation", test_fallback_output),
        ("Router Integration", test_router_integration),
        ("Schema Compliance", validate_schema_compliance),
        ("Complete Flow", test_complete_flow),
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
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("ALL TESTS PASSED - StrategyMarket Skill implementation is ready!")
    else:
        print("Some tests failed - review implementation")
    
    return failed == 0


if __name__ == "__main__":
    asyncio.run(main())
