## Context

This change registers the existing OpenSpec contract artifacts under `openspec/specs/` so that `openspec validate` can discover and validate them.
The repo already contains OpenSpec metadata and spec files, but the workflow has not yet been fully connected through a registered change.

## Goals / Non-Goals

**Goals:**
- Register the current OpenSpec specs in the change workflow.
- Provide a minimal path for OpenSpec to validate the repository's contract artifacts.
- Keep the change focused on OpenSpec registration, without modifying existing backend/frontend functionality.

**Non-Goals:**
- Do not alter actual YAML contract contents beyond what is necessary for OpenSpec compatibility.
- Do not implement backend or frontend features as part of this change.

## Decisions

- Use a repo-local OpenSpec change (`register-open-specs`) because the repository already has an OpenSpec workspace and contract artifacts.
- Create a minimal capability spec under `openspec/changes/register-open-specs/specs/register-open-specs/` so the change contains at least one parsed delta.
- Keep implementation details in `tasks.md` and use this design doc only to explain the technical purpose and scope.

## Risks / Trade-offs

- Risk: OpenSpec may still reject the change if the spec delta formatting does not match its expected structure.
  - Mitigation: Use explicit `## ADDED Requirements` and `#### Scenario:` headers in the change spec.
- Risk: The change only registers the OpenSpec workflow, not the actual contract file validation semantics.
  - Mitigation: After registration, use `openspec validate --specs` to confirm workspace-level validation and then, separately, use YAML schema validation for the actual contract files.
