## Why

The GetSmart v3.0 pipeline requires 4 Macro-Skills to run in parallel during Phase 3 (Parallel Analysis).
The User Experience Macro-Skill is the first to be implemented, following the contract defined in
`openspec/specs/macro_skills/ux_skill.yaml`.

Without this skill, the pipeline cannot produce UX intelligence for the Phase 4 Synthesizer.

## What Changes

- Implement `UserExperienceSkill` covering UI/UX, Accessibility, and Localization analysis.
- Create `BaseMacroSkill` abstract base class to share cache, retry, and model-call logic across all 4 skills.
- Register the skill as a Celery task (`run_ux_skill`) for parallel async execution.
- Expose 3 FastAPI endpoints: async dispatch, sync (dev), and job polling.
- Reorganize skill code from `app/skills/` into `app/services/macro_skills/` to align with the existing `services/` layer.

## Capabilities

### New Capabilities
- `user_experience_analysis`: Analyze a game's UI/UX, Accessibility, and Localization from a UXMiniContext.

### Modified Capabilities
- `cache_manager`: Fixed `InMemoryBackend` import path and `expire` type (int, not timedelta).
- `requirements`: Added `google-genai>=2.0.0`, `jinja2>=3.1.0`, `tenacity>=8.2.0`, `redis>=5.0.0`, `celery[redis]`.

## Impact

- Implements `openspec/specs/macro_skills/ux_skill.yaml` (Phase 3 contract).
- No changes to the scraper, synthesis, or frontend contracts.
- The `BaseMacroSkill` pattern will be reused for `design_art`, `tech_systems`, and `strategy_market` skills.
