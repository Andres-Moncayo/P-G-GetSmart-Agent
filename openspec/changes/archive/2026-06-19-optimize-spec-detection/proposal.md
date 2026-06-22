## Why

Current OpenSpec specifications are not detected by `openspec validate --specs`, preventing complete repository validation. Although the base structure is correct, it needs adjustments to meet the expected format.

## What Changes

- Will adjust the openspec/specs/ directory structure
- Will create reference files for OpenSpec to detect individual specs
- Will implement renaming if necessary to comply with conventions

## Capabilities

### New Capabilities
- optimize-spec-detection: Optimizes specification detection for complete validation

### Modified Capabilities
- None - only structural adjustments, no functional changes

## Impact

- Affects only OpenSpec metadata
- Does not change backend/frontend functionality
- Improves development experience with complete validation