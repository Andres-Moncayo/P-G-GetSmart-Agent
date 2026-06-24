## Why

The GetSmart v3.0 pipeline requires 4 Macro-Skills to run in parallel during Phase 3 (Parallel Analysis).
The Strategy and Market Macro-Skill evaluates market positioning, monetization sustainability, and cultural reach, following the contract defined in `openspec/specs/macro_skills/strategy_market_skill.yaml`.

Without this skill, the pipeline cannot evaluate the commercial viability of titles.

## What Changes

- Implement `StrategyMarketService` covering Audience, Business Model, Retention/Live Ops, Production/Business, Marketing, and Cultural Impact analysis.
- Inherit from `BaseMacroSkill` to leverage shared caching, retry logic, and API generation capabilities.
- Register the skill in the FastAPI routing under `/skills/strategy-market` endpoint.

## Capabilities

### New Capabilities
- `strategy_market_analysis`: Analyze a game's market dynamics, financial strategies, and cultural reach from a StrategyMarketMiniContext.

## Impact

- Implements `openspec/specs/macro_skills/strategy_market_skill.yaml` (Phase 3 contract).
- No changes to the scraper, synthesis, or frontend contracts.
