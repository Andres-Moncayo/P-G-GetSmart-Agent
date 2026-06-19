# OpenSpec Spec-Driven Development Workflow

## Overview

This document defines the complete workflow for Spec-Driven Development (SDD) using OpenSpec in the GetSmart project, including GitHub PR integration and file management rules.

## Core Principles

### Spec-First Development
- All changes must start from OpenSpec contracts
- Code implementation follows specification contracts
- No code changes should occur without corresponding specification support

### Modular Architecture
- Each contract/skill operates independently
- File ownership is clearly defined per contract
- No cross-contract dependencies without explicit specification

### Workflow Separation
- **OpenSpec Changes**: Workflow tracking and approval management
- **Git Commits**: Code version control and integration
- **GitHub PRs**: Code review and merge approval

## Workflow Types

### 1. Specification Changes (Spec Modification)
**Use when**: Modifying system behavior, contracts, or requirements

**Prerequisites:** 
- Contract owner or Tech Lead role required
- Full understanding of impact on dependent components

**Process:**
```bash
# Create specification change
openspec new change "spec-modification-name"

# Modify specification files
openspec/specs/contract_name.yaml
openspec/specs/contract_name.md

# Validation
openspec validate --all

# Git integration
git checkout -b feature/spec-modification-name
git add openspec/specs/contract_name.yaml
git add openspec/specs/contract_name.md  
git add openspec/changes/spec-modification-name/
git commit -m "feat: Modify contract_name specification per OpenSpec change"
git push origin feature/spec-modification-name

# GitHub PR
# Title: [Spec Change] Modify Contract Name
# Body: Referencing OpenSpec change: spec-modification-name
# Request review from Tech Lead
```

**Approval Process:**
1. Tech Lead reviews GitHub PR
2. Validates specification changes align with project architecture  
3. Merges PR if approved
4. Completes OpenSpec change process

### 2. Implementation Changes (Code Only)
**Use when**: Implementing functionality defined in existing specifications

**Prerequisites:**
- Specification contracts are already approved and stable
- Clear understanding of contract requirements

**Process:**
```bash
# Create implementation change
openspec new --type implementation "implement-contract-name"

# Implement code only (NO spec modifications)
backend/app/api/contract_name.py
frontend/src/modules/contract_name/
# Other implementation files as per contract

# Validation
openspec validate --all
# Additional code-specific tests
npm test
pytest

# Git integration  
git checkout -b feature/implement-contract-name
git add backend/app/api/contract_name.py
git add frontend/src/modules/contract_name/
git add openspec/changes/implement-contract-name/
git commit -m "feat: Implement contract_name per OpenSpec specifications"
git push origin feature/implement-contract-name

# GitHub PR
# Title: [Implementation] Contract Name Module  
# Body: Implements openspec/specs/contract_name.yaml contract
# Request review from appropriate team member
```

**Approval Process:**
1. Team member reviews implementation code
2. Verifies compliance with specification contracts
3. Merges PR if implementation is correct
4. Completes OpenSpec change implementation

## File Management Rules

### Contract-Specific File Ownership

Each skill/contract owns these exclusive files:

#### UX Skill Contract Files
```
openspec/specs/macro_skills/ux_skill.yaml
openspec/specs/macro_skills/ux_skill.md
backend/app/api/macro_skills/ux_skill.py
backend/app/services/macro_skills/ux_service.py  
backend/app/models/macro_skills/ux_models.py
frontend/src/modules/macro_skills/ux_skill/
frontend/src/services/api/uxApi.ts
frontend/src/types/api/uxTypes.ts
```

#### Design Art Skill Contract Files
```
openspec/specs/macro_skills/design_art_skill.yaml
openspec/specs/macro_skills/design_art_skill.md
backend/app/api/macro_skills/design_art_skill.py
backend/app/services/macro_skills/design_art_service.py
backend/app/models/macro_skills/design_art_models.py
frontend/src/modules/macro_skills/design_art_skill/
frontend/src/services/api/designApi.ts
frontend/src/types/api/designTypes.ts
```

#### Tech Systems Skill Contract Files
```
openspec/specs/macro_skills/tech_systems_skill.yaml
openspec/specs/macro_skills/tech_systems_skill.md
backend/app/api/macro_skills/tech_systems_skill.py
backend/app/services/macro_skills/tech_service.py
backend/app/models/macro_skills/tech_models.py
frontend/src/modules/macro_skills/tech_systems_skill/
frontend/src/services/api/techApi.ts
frontend/src/types/api/techTypes.ts
```

#### Strategy Market Skill Contract Files
```
openspec/specs/macro_skills/strategy_market_skill.yaml
openspec/specs/macro_skills/strategy_market_skill.md
backend/app/api/macro_skills/strategy_market_skill.py
backend/app/services/macro_skills/strategy_service.py
backend/app/models/macro_skills/strategy_models.py
frontend/src/modules/macro_skills/strategy_market_skill/
frontend/src/services/api/strategyApi.ts
frontend/src/types/api/strategyTypes.ts
```

#### Synthesis Skill Contract Files
```
openspec/specs/synthesis/synthesis_skill.yaml
openspec/specs/synthesis/synthesis_skill.md
backend/app/api/synthesis/synthesis_skill.py
backend/app/services/synthesis/synthesis_service.py
backend/app/models/synthesis/synthesis_models.py
frontend/src/modules/synthesis/synthesis_skill/
frontend/src/services/api/synthesisApi.ts
frontend/src/types/api/synthesisTypes.ts
```

#### UI and Login Contract Files
```
openspec/specs/ui_and_login/ui_login_contract.yaml
openspec/specs/ui_and_login/ui_login_contract.md
frontend/src/modules/auth/login/
frontend/src/modules/dashboard/
frontend/src/modules/reports/
frontend/src/modules/pipeline/
```

#### Scraper Contract Files
```
openspec/specs/scraper/master_json_schema.yaml
openspec/specs/scraper/data_crud_contract.yaml
openspec/specs/scraper/pre_scrap_contract.yaml
openspec/specs/scraper/scraper_contract.yaml
backend/app/services/scrapers/
backend/app/models/scrapers/
```

### File Upload Restrictions

**RULE: Only upload files that your contract creates**

**Permitted Files per Change:**
- Specification files for your specific contract only
- Implementation files for contract functionality
- OpenSpec change metadata folder
- Dependencies explicitly required by your contract

**Prohibited Files:**
- Files belonging to other contracts/skills
- General infrastructure files not in your scope
- Configuration files not related to your contract
- Files that create cross-contract dependencies

## Approval Authority

### Tech Lead Capabilities
As Tech Lead, you have direct approval authority:
- ✅ Complete OpenSpec specification changes without external approval
- ✅ Merge GitHub PRs after technical review
- ✅ Archive OpenSpec changes after completion
- ✅ Approve cross-contract dependencies
- ✅ Override team member approval for critical changes

### Team Member Responsibilities
- ✅ Create OpenSpec changes for their assigned contracts
- ✅ Implement code following specification contracts
- ✅ Request appropriate reviews for changes
- ✅ Follow file upload restrictions strictly
- ✅ Validate changes before submission

## Complete Change Integration Process

### For Specification Changes (Tech Lead Authority)
```bash
# 1. Create and modify specs
openspec new change "update-contract-behavior"
# Modify openspec/specs/contract_name.yaml

# 2. Validate locally
openspec validate --all

# 3. Create PR for documentation
git checkout -b feature/update-contract-behavior
git add openspec/specs/contract_name.yaml
git add openspec/changes/update-contract-behavior/
git commit -m "feat: Update contract behavior per OpenSpec change"
git push origin feature/update-contract-behavior

# 4. Create GitHub PR (self-merge if needed)

# 5. After PR merge
git checkout main && git pull
openspec complete change/update-contract-behavior
openspec archive change/update-contract-behavior
```

### For Team Member Implementation Changes
```bash
# 1. Team member creates implementation
openspec new --type implementation "implement-contract-x"
# Implement code files per contract

# 2. Team member requests review
git push origin feature/implement-contract-x
# Creates PR requesting Tech Lead review

# 3. Tech Lead reviews and merges
# Approve GitHub PR if implementation matches specs

# 4. Tech Lead completes the OpenSpec change
git checkout main && git pull
openspec complete change/implement-contract-x
openspec archive change/implement-contract-x
```

## Quality Assurance

### Pre-Submission Validation
```bash
# Required validations before PR:
openspec validate --all          # OpenSpec contract validation
git status                       # Check staged files
# Additional technical validations:
npm run lint                      # Frontend linting
python -m ruff check            # Backend linting
npm test                        # Frontend tests
pytest                          # Backend tests
```

### Review Checklist

**For GitHub PRs:**
- [ ] Files uploaded match contract ownership rules
- [ ] OpenSpec change referenced in PR description
- [ ] All validations pass locally
- [ ] Code follows project conventions
- [ ] No cross-contract file pollution

**For OpenSpec Changes:**
- [ ] Change type is correct (spec vs implementation)
- [ ] Description is clear and complete
- [ ] All required metadata is included
- [ ] Change aligns with project architecture

## Error Prevention Strategies

### Common Mistakes to Avoid
1. **Uploading wrong files** → Always verify contract file ownership
2. **Missing OpenSpec reference** → Always include change folder in commit
3. **Skipping validation** → Always run `openspec validate --all`
4. **Cross-contract pollution** → Stay within your contract boundaries
5. **Missing PR description** → Always describe change and OpenSpec reference

### Recovery Procedures
```bash
# If wrong files were committed:
git reset HEAD~1                    # Remove last commit
git checkout HEAD -- path/to/wrong/files  # Restore original files
# Make correct commit with proper files only

# If OpenSpec validation fails:
openspec validate --all               # Identify specific errors
# Fix specification files
git add openspec/specs/affected_contracts.yaml
git commit -m "fix: Resolve validation errors"
```

## Team Communication Standards

### PR Description Template
```markdown
## Change Summary
[Brief description of what this change accomplishes]

## Change Type
- [ ] Spec Change (modifying YAML/MD contracts)  
- [ ] Implementation (creating code per existing specs)

## OpenSpec Reference
- **Change**: `change-name-in-openspec`
- **Contract**: `openspec/specs/related_contract.yaml`
- **Schema**: Referenced contract specification

## Files Modified (Contract-Specific Only)
- [ ] `openspec/specs/contract_name.yaml`
- [ ] `backend/app/api/contract_file.py`
- [ ] `frontend/src/modules/contract_name/`

## Validation Status
- [ ] `openspec validate --all` passed
- [ ] Only contract-specific files included
- [ ] All linting checks passed
- [ ] All tests passing

## Impact Assessment
- [ ] No cross-contract dependencies created
- [ ] Backward compatibility maintained
- [ ] Rolling deployment safe

## Review Requirements
- [ ] Code review from Tech Lead required
- [ ] Architecture impact assessment needed
```

### Commit Message Standards
```
type(scope): action per OpenSpec change/change-name

feat(ux_skill): Implement analysis component per OpenSpec change/implement-ux-v1
fix(design_art): Resolve validation errors in schema per OpenSpec change/fix-design-schema
docs(synthesis): Update documentation per OpenSpec change/update-synthesis-docs
```

This workflow ensures clean modular development while maintaining full traceability between OpenSpec contracts and code implementation.