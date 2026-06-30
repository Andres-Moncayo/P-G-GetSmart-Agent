import pytest
import os

@pytest.fixture
def base_dir():
    # The tests run in `backend/` or `backend/tests/`, so we can resolve the root backend directory
    # Assuming this runs from the backend directory
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_basic_structure(base_dir):
    """Test 1: Check basic file and directory structure for Tech Systems Skill"""
    skill_dir = os.path.join(base_dir, "app", "services", "macro_skills", "tech_system_skill")
    
    assert os.path.isdir(skill_dir), "Skill directory missing"
    
    expected_files = [
        "__init__.py",
        "tech_system_service.py",
        "system_prompt.py"
    ]
    
    for file in expected_files:
        assert os.path.isfile(os.path.join(skill_dir, file)), f"Missing file: {file}"

def test_direct_file_structure(base_dir):
    """Test 2: Check direct file content structure"""
    skill_dir = os.path.join(base_dir, "app", "services", "macro_skills", "tech_system_skill")
    system_prompt_file = os.path.join(skill_dir, "system_prompt.py")
    
    with open(system_prompt_file, 'r') as f:
        prompts_content = f.read()
    assert "TECH_SYSTEMS_MAIN_PROMPT = \"\"\"" in prompts_content, "System prompt missing"
    service_file = os.path.join(skill_dir, "tech_system_service.py")
    with open(service_file, 'r') as f:
        service_content = f.read()
        
    checks = [
        "class TechSystemService",
        "BaseMacroSkill",
        'skill_id: str = "tech_systems"',
        'skill_name: str = "Technology and Systems"',
        "def system_prompt",
        "def build_user_prompt",
        "def _fallback_output"
    ]
    
    for check in checks:
        assert check in service_content, f"Missing implementation detail: {check}"

def test_open_spec_alignment(base_dir):
    """Test 3: Check alignment with OpenSpec requirements"""
    skill_dir = os.path.join(base_dir, "app", "services", "macro_skills", "tech_system_skill")
    system_prompt_file = os.path.join(skill_dir, "system_prompt.py")
    
    with open(system_prompt_file, 'r') as f:
        prompts_content = f.read()
        
    tech_enums = [
        "engine_type: proprietary, unreal_engine_4, unreal_engine_5, unity, customized_commercial, other",
        "graphics_api: directx_11, directx_12, vulkan, opengl, metal, multiple",
        "performance_stability: unstable, variable, stable, rock_solid",
        "optimization_rating: poor, average, good, excellent"
    ]
    for enum_def in tech_enums:
        assert enum_def in prompts_content, f"Missing enum: {enum_def}"
        
    multiplayer_enums = [
        "netcode_type: p2p, dedicated_servers, hybrid, rollback, listen_server",
        "latency_rating: unplayable, noticeable, acceptable, imperceptible"
    ]
    for enum_def in multiplayer_enums:
        assert enum_def in prompts_content, f"Missing enum: {enum_def}"
        
    platform_enums = [
        "parity_level: fragmented, uneven, functional, full",
        "port_quality_rating: unplayable, functional, good, excellent"
    ]
    for enum_def in platform_enums:
        assert enum_def in prompts_content, f"Missing enum: {enum_def}"

def test_router_integration(base_dir):
    """Test 4: Router integration check"""
    router_file = os.path.join(base_dir, "app", "api", "skills_routes.py")
    
    with open(router_file, 'r') as f:
        router_content = f.read()
        
    required_elements = [
        'skills_router.post("/tech-systems"',
        "from ..services.macro_skills.tech_system_skill import TechSystemService",
        "TechSystemService()"
    ]        
    for element in required_elements:
        assert element in router_content, f"Missing element in router: {element}"

def test_catgory_structure(base_dir):
    """Test 5: Verify 3 category structure"""
    service_file = os.path.join(base_dir, "app", "services", "macro_skills", "tech_system_skill", "tech_system_service.py")
    
    with open(service_file, 'r') as f:
        service_content = f.read()
        
    categories = [
        "technology_performance",
        "multiplayer_social", 
        "platforms_distribution"
    ]
    for category in categories:
        assert category in service_content, f"Missing category: {category}"

def test_main_py_includes_router(base_dir):
    """Test 6: Check main.py includes skills router"""
    main_file = os.path.join(base_dir, "app", "main.py")
    
    with open(main_file, 'r') as f:
        main_content = f.read()
        
    assert "skills_router" in main_content
    assert "app.include_router(skills_router" in main_content
