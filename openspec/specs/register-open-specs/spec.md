# register-open-specs Specification

## Purpose
TBD - created by archiving change register-open-specs. Update Purpose after archive.
## Requirements
### Requirement: Register current spec artifacts
The system SHALL register existing OpenSpec contract artifacts so `openspec validate` can discover them.

#### Scenario: Register existing OpenSpec contract files
- **WHEN** the repository contains `openspec/specs/` with contract YAML and Markdown files
- **THEN** `openspec validate --type change register-open-specs --no-interactive` succeeds

