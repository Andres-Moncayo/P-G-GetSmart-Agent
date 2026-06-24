# Strategy and Market Analysis Specification

## ADDED Requirements

### Requirement: SMA-1: The system SHALL ingest Strategy and Market data
The system MUST parse StrategyMarketMiniContext and validate all incoming fields.

#### Scenario: Parse Strategy and Market hard data
Given a valid StrategyMarketMiniContext
When StrategyMarketService is invoked
Then it should parse genres, platforms, estimated revenue, and estimated owners.

### Requirement: SMA-2: The system SHALL return Strategy and Market outputs
The system MUST return StrategyMarketOutputModel with all 6 categories and confidence scores.

#### Scenario: Return structured analysis
Given a successful Gemini analysis
When the result is parsed
Then the output must match StrategyMarketOutputModel.

