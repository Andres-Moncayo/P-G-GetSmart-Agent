## Why

The repository already contains OpenSpec contract artifacts under `openspec/specs/`, but the workspace has not registered them for OpenSpec validation.
This change registers the existing spec files in the OpenSpec workflow so `openspec validate` can find and verify them.

## What Changes

- Create an OpenSpec change proposal to register current contract artifacts.
- Add a new OpenSpec capability for spec registration.
- Establish a minimal workspace record so OpenSpec can validate this repository.

## Capabilities

### New Capabilities
- `register-open-specs`: Register existing OpenSpec spec artifacts under `openspec/specs/` to enable OpenSpec validation.

### Modified Capabilities
- None

## Impact

- Affects OpenSpec workspace metadata under `openspec/changes/register-open-specs`
- Enables OpenSpec validation workflows for the current repository
- No functional backend/frontend implementation changes
