# Update Workflow Schema Documentation

## Purpose

Update OpenSpec schema documentation with file upload restrictions and GitHub PR approval workflow to ensure proper spec-driven development practices.

## Key Updates

### 1. File Upload Restrictions
- **Rule**: Only upload files that your contract creates
- **Purpose**: Avoid conflicts and maintain clean workflow
- **Implementation**: Developers should identify which files belong to their specific contract/skill

### 2. GitHub PR Approval Workflow
- **Team Member Workflow**:
  1. Create feature branch from main
  2. Implement changes (specs and/or code)
  3. Push branch and create Pull Request
  4. Add OpenSpec change reference in PR description
  5. Request review from Tech Lead

- **Tech Lead Approval Process**:
  1. Review Pull Request in GitHub UI
  2. Verify changes match OpenSpec contracts
  3. Merge PR if approved
  4. Update local: `git checkout main && git pull`
  5. Complete OpenSpec change: `openspec complete change/name`
  6. Archive OpenSpec change: `openspec archive change/name`

### 3. Change Management Integration
- **No need for additional PR** after merge
- OpenSpec changes serve as workflow tracking
- Git PR serves as code integration mechanism
- Both work together but serve different purposes

## Technical Implementation Details

### For Spec Changes (YAML/MD modifications)
```bash
# 1. Create OpenSpec change
openspec new change "spec-update-name"

# 2. Modify spec files directly
# openspec/specs/skill_name.yaml
# openspec/specs/skill_name.md

# 3. Git workflow
git checkout -b feature/spec-update-name
git add openspec/specs/skill_name.yaml
git add openspec/specs/skill_name.md
git add openspec/changes/spec-update-name/
git commit -m "feat: Update skill_name specification"
git push origin feature/spec-update-name

# 4. Create PR in GitHub with reference to OpenSpec change
# Title: [Spec Change] Update Skill Name Contract
# Body: "Referencing OpenSpec change: spec-update-name"
```

### For Implementation Changes (Code only)
```bash
# 1. Create OpenSpec implementation change
openspec new --type implementation "implement-skill-name"

# 2. Implement code without touching specs
# backend/app/api/skill_name.py
# frontend/src/modules/skill_name/

# 3. Git workflow
git checkout -b feature/implement-skill-name
git add backend/app/api/skill_name.py
git add frontend/src/modules/skill_name/
git add openspec/changes/implement-skill-name/
git commit -m "feat: Implement skill_name per OpenSpec contract"
git push origin feature/implement-skill-name

# 4. Create PR referencing specs
# Title: [Implementation] Skill Name Module
# Body: "Implements openspec/specs/skill_name.yaml contract"
```

## Approval Authority

### Tech Lead Permissions
As Tech Lead, you have direct approval authority:
- Can complete OpenSpec changes without external approval
- Can merge GitHub PRs after review
- Responsible for ensuring changes align with project architecture

### Approval Process Flow
```bash
# After PR merge:
git checkout main
git pull origin main
openspec complete change/change-name
openspec archive change/change-name
```

## File Management Rules

### What to Upload (For Each Contract/Skill)
- **Spec Changes**: Only the specific YAML/MD files for your skill
- **Implementation Changes**: Only the code files your skill requires
- **OpenSpec Metadata**: The change folder itself for tracking

### What NOT to Upload
- No unrelated files outside your contract scope
- No duplicate files or backup versions
- No development artifacts related to other skills

## Error Prevention

### Common Issues to Avoid
1. **File Conflicts**: Only upload files you modified according to contract
2. **Scope Creep**: Stay within your defined contract boundaries
3. **Missing Metadata**: Always include the OpenSpec change folder in commits
4. **Validation**: Always run `openspec validate --all` before PR

### Validation Checklist
```bash
# Before creating PR:
openspec validate --all
git status  # Verify staged files
# Review what you're uploading matches your contract
```

## Team Communication

### PR Description Template
```markdown
## Change Type
- [ ] Spec Change (modifying YAML/MD contracts)
- [ ] Implementation (creating code per existing specs)

## OpenSpec Reference
- Change: `change-name-in-openspec`
- Spec: `openspec/specs/related_contract.yaml`

## Files Modified
- [ ] `path/to/file1.ext`
- [ ] `path/to/file2.ext`

## Validation
- [ ] `openspec validate --all` passed
- [ ] Only contract-specific files included
```