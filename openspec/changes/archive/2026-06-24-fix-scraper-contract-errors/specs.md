## ADDED Requirements

### Requirement: Schema Validation Compliance
<!-- All scraper contract files must pass OpenSpec validation without errors -->

#### Scenario: Scraper Contract Validation
- **WHEN** OpenSpec validation is run on scraper_contract.yaml or scraper_contract.md
- **THEN** Both files must pass validation without any errors

#### Scenario: Schema Field Completeness
- **WHEN** Reviewing YAML and MD files for required fields
- **THEN** All required fields according to spec-driven schema must be present and valid

### Requirement: Cross-File Consistency
<!-- YAML and MD files must be synchronized and consistent -->

#### Scenario: Version Consistency
- **WHEN** Comparing version fields between scraper_contract.yaml and scraper_contract.md
- **THEN** Both files must have identical version numbers

#### Scenario: Status Consistency
- **WHEN** Checking status fields across both files
- **THEN** Status formatting must be consistent (lowercase)

#### Scenario: Date Synchronization
- **WHEN** Reviewing updated_at dates
- **THEN** Both files must reflect the same last update date

### Requirement: Content Integrity Preservation
<!-- Essential technical content must remain unchanged -->

#### Scenario: API Endpoint Preservation
- **WHEN** Validating the corrected files
- **THEN** All API endpoints, data structures, and technical specifications must remain unchanged

#### Scenario: Architectural Decisions Preservation
- **WHEN** Reviewing ADRs and architectural content
- **THEN** All architectural decisions and rationale must be preserved exactly