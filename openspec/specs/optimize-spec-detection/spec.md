# optimize-spec-detection Specification

## Purpose
TBD - created by archiving change optimize-spec-detection. Update Purpose after archive.
## Requirements
### Requirement: Optimize spec detection for OpenSpec validation
The system SHALL optimize the OpenSpec configuration so that `openspec validate --specs` discovers all individual specification files in the repository.

#### Scenario: Ensure OpenSpec detects all specs
- **WHEN** the repository contains specification files in `openspec/specs/` directories
- **THEN** `openspec validate --specs` detects and validates all individual spec files
- **AND** the total reported includes all macro_skills, scraper, synthesis, and ui_and_login specs

