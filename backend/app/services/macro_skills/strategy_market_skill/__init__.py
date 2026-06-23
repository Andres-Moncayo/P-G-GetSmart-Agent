"""
Strategy and Market Macro-Skill for GetSmart.

Analyzes audience segmentation, business monetization models, player retention,
production contexts, marketing campaigns, and cultural footprint.

This skill processes the Strategy & Market Mini-Context and produces
structured intelligence for the Synthesizer (Phase 4).
"""

from .strategy_market_service import StrategyMarketService

__all__ = ["StrategyMarketService"]
