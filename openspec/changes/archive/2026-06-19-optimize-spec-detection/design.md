## Context

This change optimizes OpenSpec specification detection so that `openspec validate --specs` can discover all individual specifications in the repository.

## Goals / Non-Goals

**Goals:**
- Make `openspec validate --specs` detect all individual specs
- Maintain existing structure of specification files
- Ensure full compatibility with OpenSpec tools

**Non-Goals:**
- Do not modify content of existing specification files
- Do not change backend/frontend functionality
- Do not alter existing YAML contracts

## Decisions

- Maintain current structure in openspec/specs/ but add references if necessary
- Investigate exact format that OpenSpec expects for spec detection
- Create index or reference files if OpenSpec requires them

## Risks / Trade-offs

- Risk: Changes might break current change detection
  - Mitigation: Test incrementally and maintain backups
- Risk: OpenSpec might have undocumented specific requirements
  - Mitigation: Research documentation and test different structures