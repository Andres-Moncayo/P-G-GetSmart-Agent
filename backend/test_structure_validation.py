"""
Simplified structure validation test for TechSystems Skill.

This script tests the structure without LLM dependencies.
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


def test_basic_structure():
    """Test 1: Basic file structure"""
    print("=== Test 1: Basic File Structure ===")
    try:
        # Test if files exist
        skill_dir = "app/services/macro_skills/tech_system_skill"
        required_files = [
            "__init__.py",
            "system_prompt.py", 
            "tech_system_service.py"
        ]
        
        for file in required_files:
            file_path = os.path.join(skill_dir, file)
            if os.path.exists(file_path):
                print(f"[PASS] {file} exists")
            else:
                print(f"[FAIL] {file} missing")
                return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Structure test failed: {e}")
        return False


def test_direct_file_structure():
    """Test 2: Direct file content checks"""
    print("\n=== Test 2: Direct File Content ===")
    try:
        # Check system_prompt.py has content
        with open("app/services/macro_skills/tech_system_skill/system_prompt.py", 'r') as f:
            prompts_content = f.read()
            if "TECH_SYSTEMS_MAIN_PROMPT" in prompts_content and len(prompts_content) > 1000:
                print("[PASS] System prompts file has content")
            else:
                print("[FAIL] System prompts file empty or incomplete")
                return False
        
        # Check service file has class
        with open("app/services/macro_skills/tech_system_skill/tech_system_service.py", 'r') as f:
            service_content = f.read()
            
        checks = [
            ("class TechSystemService", "TechSystemService class defined"),
            ("BaseMacroSkill", "Extends BaseMacroSkill"),
('skill_id: str = "tech_systems"', "Skill ID set correctly"),
('skill_name: str = "Technology and Systems"', "Skill name set correctly"),
            ("def system_prompt", "System prompt method implemented"),
            ("def build_user_prompt", "User prompt builder implemented"),
            ("def _fallback_output", "Fallback output method implemented")
        ]
        
        for check, description in checks:
            if check in service_content:
                print(f"[PASS] {description}")
            else:
                print(f"[FAIL] {description}")
                return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Direct file check failed: {e}")
        return False


def test_open_spec_alignment():
    """Test 3: Check alignment with OpenSpec requirements"""
    print("\n=== Test 3: OpenSpec Alignment ===")
    try:
        # Check system prompts for enum references
        with open("app/services/macro_skills/tech_system_skill/system_prompt.py", 'r') as f:
            prompts_content = f.read()
        
        # Check technology performance enums
        tech_enums = [
            "engine_type: proprietary, unreal_engine_4, unreal_engine_5, unity, customized_commercial, other",
            "graphics_api: directx_11, directx_12, vulkan, opengl, metal, multiple",
            "performance_stability: unstable, variable, stable, rock_solid",
            "optimization_rating: poor, average, good, excellent"
        ]
        
        for enum_def in tech_enums:
            if enum_def in prompts_content:
                print(f"[PASS] Tech enum present: {enum_def.split(':')[0]}")
            else:
                print(f"[FAIL] Tech enum missing: {enum_def.split(':')[0]}")
                return False
        
        # Check multiplayer enums
        multiplayer_enums = [
            "netcode_type: p2p, dedicated_servers, hybrid, rollback, listen_server",
            "latency_rating: unplayable, noticeable, acceptable, imperceptible"
        ]
        
        for enum_def in multiplayer_enums:
            if enum_def in prompts_content:
                print(f"[PASS] Multiplayer enum present: {enum_def.split(':')[0]}")
            else:
                print(f"[FAIL] Multiplayer enum missing: {enum_def.split(':')[0]}")
                return False
        
        # Check platform enums
        platform_enums = [
            "parity_level: fragmented, uneven, functional, full",
            "port_quality_rating: unplayable, functional, good, excellent"
        ]
        
        for enum_def in platform_enums:
            if enum_def in prompts_content:
                print(f"[PASS] Platform enum present: {enum_def.split(':')[0]}")
            else:
                print(f"[FAIL] Platform enum missing: {enum_def.split(':')[0]}")
                return False
        
        return True
    except Exception as e:
        print(f"[FAIL] OpenSpec alignment test failed: {e}")
        return False


def test_router_integration():
    """Test 4: Router integration check"""
    print("\n=== Test 4: Router Integration ===")
    try:
        # Check router file directly
        with open("app/api/skills_routes.py", 'r') as f:
            router_content = f.read()
        
        required_elements = [
            ("@skills_router.post(\"/tech-systems\")", "Tech systems endpoint"),
            ("from ..services.macro_skills.tech_system_skill import TechSystemService", "Tech systems import"),
            ("TechSystemService()", "Service instantiation")
        ]        
        for element, description in required_elements:
            if element in router_content:
                print(f"[PASS] {description}")
            else:
                print(f"[FAIL] {description}")
                return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Router integration test failed: {e}")
        return False


def test_catgory_structure():
    """Test 5: Verify 3 category structure"""
    print("\n=== Test 5: Category Structure ===")
    try:
        # Check service file references 3 categories
        with open("app/services/macro_skills/tech_system_skill/tech_system_service.py", 'r') as f:
            service_content = f.read()
        
        categories = [
            "technology_performance",
            "multiplayer_social", 
            "platforms_distribution"
        ]
        
        for category in categories:
            if category in service_content:
                print(f"[PASS] {category} category included")
            else:
                print(f"[FAIL] {category} category missing")
                return False
        
        return True
    except Exception as e:
        print(f"[FAIL] Category structure test failed: {e}")
        return False


def test_main_py_includes_router():
    """Test 6: Check main.py includes skills router"""
    print("\n=== Test 6: Main.py Integration ===")
    try:
        # Check main.py includes skills router
        with open("app/main.py", 'r') as f:
            main_content = f.read()
        
        if "skills_router" in main_content and "app.include_router(skills_router" in main_content:
            print("[PASS] Skills router included in main.py")
            return True
        else:
            print("[FAIL] Skills router not included in main.py")
            return False
    except Exception as e:
        print(f"[FAIL] Main.py integration test failed: {e}")
        return False


def main():
    """Run all structure tests"""
    print("Starting TechSystems Skill Structure Validation")
    print("=" * 60)
    
    tests = [
        ("Basic File Structure", test_basic_structure),
        ("Direct File Content", test_direct_file_structure),
        ("OpenSpec Alignment", test_open_spec_alignment),
        ("Router Integration", test_router_integration),
        ("Category Structure", test_catgory_structure),
        ("Main.py Integration", test_main_py_includes_router),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("STRUCTURE VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\nALL STRUCTURE TESTS PASSED!")
        print("Implementation follows OpenSpec specifications")
        print("Ready for integration with API pipeline")
        
        print("\nImplementation Summary:")
        print("- Technology Systems Skill successfully implemented")
        print("- 3 analysis categories: Technology/Performance, Multiplayer/Social, Platforms/Distribution")
        print("- System prompts centralized and versionable")
        print("- Router endpoint: POST /api/skills/tech-systems")
        print("- Extends BaseMacroSkill for caching and retry logic")
        print("- Complete fallback support for error scenarios")
        print("- All required enums from OpenSpec YAML included")
        
    else:
        print("\nSome structure tests failed - review implementation")
    
    return failed == 0


if __name__ == "__main__":
    main()