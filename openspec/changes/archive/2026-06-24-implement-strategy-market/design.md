## Context

Phase 3 of the GetSmart pipeline requires 4 Macro-Skills to execute in parallel. The Strategy and Market Macro-Skill evaluates Audience, Business Model, Retention/Live Ops, Production/Business, Marketing, and Cultural Impact. It uses Google Gemini 2.5 Flash with Pydantic schemas for data integrity.

## Goals / Non-Goals

**Goals:**
- Implement `StrategyMarketService` following `strategy_market_skill.yaml` exactly.
- Register route `POST /skills/strategy-market` in the FastAPI routes.
- Validate incoming context schemas and final response structures.

**Non-Goals:**
- Do not implement frontend rendering.
- Do not implement Celery tasks or RAG pipelines.
