# Design: Reorganize Design Art Skill Structure

## Architecture Overview

This change reorganizes the Design Art Skill module from a flat file structure to a proper package-based structure with clear separation of concerns.

## Current Structure
```
backend/app/services/macro_skills/
├── design_art_service.py           # Mixed service + prompts
└── __init__.py

backend/app/api/macro_skills/
└── design_art_skill.py             # Single API file
```

## Target Structure
```
backend/app/services/macro_skills/design_art_skill/
├── __init__.py                     # Package initialization
├── design_art_service.py           # Clean service logic
├── system_prompt.py                # All LLM system prompts
└── endpoints.py                    # Service layer endpoints (if needed)

backend/app/api/macro_skills/design_art_skill/
├── __init__.py                     # API package initialization  
└── endpoints.py                    # FastAPI API layer
```

## Component Design

### 1. System Prompt Module (`system_prompt.py`)
**Purpose**: Centralized location for all LLM prompts

**Contains**:
- `GAMEPLAY_ANALYSIS_PROMPT` - Expert game design analyst prompt
- `LEVEL_DESIGN_ANALYSIS_PROMPT` - Level design specialist prompt  
- `NARRATIVE_ANALYSIS_PROMPT` - Narrative design specialist prompt
- `ART_DIRECTION_ANALYSIS_PROMPT` - Art direction expert prompt
- `SOUND_DESIGN_ANALYSIS_PROMPT` - Audio design specialist prompt
- `SUMMARY_ANALYSIS_PROMPT` - Executive summary synthesis prompt

**Benefits**:
- Easy to update and version control prompts
- Clear separation of business logic from prompts
- Better readability and maintenance
- Team collaboration friendly

### 2. Service Module (`design_art_service.py`)
**Purpose**: Core business logic for Design and Art analysis

**Changes**:
- Import prompts from `system_prompt.py`
- Remove hardcoded prompt strings
- Clean method structure
- Maintain all existing functionality

**Key Methods**:
- `analyze()` - Main orchestration method
- `_analyze_gameplay_with_llm()` - Gameplay analysis
- `_create_fallback_*_analysis()` - Fallback implementations
- `_calculate_confidence()` - Confidence scoring

### 3. API Package (`api/macro_skills/design_art_skill/`)
**Purpose**: Clean API layer for FastAPI integration

**Structure**:
- `endpoints.py` - FastAPI route definitions
- `__init__.py` - Router exports

**Changes**:
- Update service import paths
- Enhanced documentation
- Maintain existing API contract

### 4. Package Initialization
**Purpose**: Proper Python package structure

**Both `__init__.py` files include**:
- Package docstring explaining purpose
- Clean exports
- Type hints for better IDE support

## Implementation Strategy

### Phase 1: File Creation
1. Create new directory structure
2. Create `system_prompt.py` with extracted prompts
3. Create package `__init__.py` files

### Phase 2: Code Migration  
1. Update service imports
2. Remove hardcoded prompts from service
3. Update API import paths
4. Maintain all existing functionality

### Phase 3: Validation
1. Test API endpoints
2. Verify all prompts load correctly
3. Ensure no breaking changes
4. Update documentation

## Import Mapping

### Before:
```python
from ...services.macro_skills.design_art_service import DesignArtService
```

### After:
```python
from ...services.macro_skills.design_art_skill.design_art_service import DesignArtService
from ...services.macro_skills.design_art_skill.system_prompt import (
    GAMEPLAY_ANALYSIS_PROMPT,
    LEVEL_DESIGN_ANALYSIS_PROMPT,
    # ... other prompts
)
```

## Risk Assessment

### Low Risk
- Pure structural change
- No functional modification
- All existing contracts preserved

### Mitigation Steps
- Step-by-step migration
- Test after each major change
- Preserve original files until verification

## Backward Compatibility
- API endpoints unchanged
- Input/output formats preserved  
- No breaking changes to consumers

## Future Extensibility
This structure enables:
- Easy addition of new analysis categories
- Prompt A/B testing capabilities
- Multiple LLM provider support
- Enhanced service modularity