# Reorganize Design Art Skill Structure

## Overview
Reorganize the files of the Design Art Skill module into proper folder structure and separate system prompts for better maintainability and team collaboration.

## Problem Statement
The current Design Art Skill implementation has all files scattered across different directories without proper organization. The system prompts are embedded within service code, making them difficult to maintain and update. The team lead has requested proper folder structure and prompt separation.

## Current State Issues
- Service files are in macro_skills root directory
- API endpoints are mixed with service logic
- System prompts are hardcoded inside methods
- No clear separation of concerns
- Difficult to maintain and update prompts
- Poor code organization for team collaboration

## Proposed Solution
1. Create dedicated folder structure for Design Art Skill
2. Separate system prompts into dedicated files
3. Organize service, API, and model files properly
4. Follow established architectural patterns

## Target State
```
backend/app/services/macro_skills/design_art_skill/
├── __init__.py
├── design_art_service.py      # Main service logic
├── system_prompt.py           # All LLM prompts
└── endpoints.py              # FastAPI endpoints (moved from api/)

backend/app/api/macro_skills/design_art_skill/
├── __init__.py
└── endpoints.py              # API layer
```

## Benefits
- **Better Organization**: Clear separation of concerns
- **Maintainability**: Easier to update and modify prompts
- **Team Collaboration**: Better code navigation and understanding
- **Scalability**: Structure supports additional skills
- **Best Practices**: Follows Python package conventions

## Dependencies
- None (architectural change only)
- Existing API routes must be updated
- Import statements need modification

## Success Criteria
- ✅ All service files organized in proper folders
- ✅ System prompts extracted to dedicated files  
- ✅ API endpoints properly structured
- ✅ All imports updated and working
- ✅ Existing functionality preserved
- ✅ API tests pass without changes