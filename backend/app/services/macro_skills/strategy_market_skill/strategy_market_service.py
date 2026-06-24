"""
Strategy and Market Macro-Skill — Phase 3 Parallel Analyzer.

Contract ref: openspec/specs/macro_skills/strategy_market_skill.yaml
Input:  mini_contexts.strategy_market (from Master-JSON)
Output: Structured Strategy & Market intelligence for Phase 4 Synthesizer.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging

from ..base_skill import BaseMacroSkill
from .system_prompt import STRATEGY_MARKET_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class StrategyMarketService(BaseMacroSkill):
    """
    Strategy and Market Macro-Skill service.
    Analyzes Audience, Business Model, Retention/Live Ops, Production/Business,
    Marketing, and Cultural Impact from the Strategy & Market Mini-Context.
    """

    skill_id = "strategy_market"
    skill_name = "Strategy and Market"
    max_output_tokens = 8000

    def __init__(self) -> None:
        super().__init__()
        logger.info("StrategyMarketService initialized")

    @property
    def system_prompt(self) -> str:
        return STRATEGY_MARKET_SYSTEM_PROMPT

    def build_user_prompt(self, mini_context: dict) -> str:
        meta = mini_context.get("metadata", {})
        hd = mini_context.get("hard_data", {})
        sd = mini_context.get("semantic_data", {})

        return f"""## GAME: {meta.get('game_name', 'Unknown')} (ID: {meta.get('game_id', '')})

## HARD DATA
- Genres: {', '.join(hd.get('genres', [])) or 'N/A'}
- Themes: {', '.join(hd.get('themes', [])) or 'N/A'}
- Game Modes: {', '.join(hd.get('game_modes', [])) or 'N/A'}
- Platforms: {', '.join(hd.get('platforms', [])) or 'N/A'}
- Release Date: {hd.get('release_date') or 'N/A'}
- Developers: {', '.join(hd.get('developers', [])) or 'N/A'}
- Publishers: {', '.join(hd.get('publishers', [])) or 'N/A'}
- Metacritic: {hd.get('metacritic') or 'N/A'}
- Price (USD): {hd.get('price_usd') or 'N/A'}
- Peak Player Count: {hd.get('player_count_peak') or 'N/A'}
- Current Player Count: {hd.get('player_count_current') or 'N/A'}
- Estimated Owners: {hd.get('estimated_owners') or 'N/A'}
- Estimated Revenue: {hd.get('estimated_revenue') or 'N/A'}
- Review Score: {hd.get('review_score') or 'N/A'}
- Review Count: {hd.get('review_count') or 'N/A'}
- DLC Count: {hd.get('dlc_count') or 'N/A'}
- DLC Price Total: {hd.get('dlc_price_total') or 'N/A'}
- Tags: {', '.join(hd.get('tags', [])) or 'N/A'}

## SEMANTIC DATA
### Audience ({len(sd.get('audience', {}).get('sources', []))} sources)
{self._fmt_sources(sd.get('audience', {}))}

### Business Model ({len(sd.get('business_model', {}).get('sources', []))} sources)
{self._fmt_sources(sd.get('business_model', {}))}

### Retention/Live Ops ({len(sd.get('retention_live_ops', {}).get('sources', []))} sources)
{self._fmt_sources(sd.get('retention_live_ops', {}))}

### Production/Business ({len(sd.get('production_business', {}).get('sources', []))} sources)
{self._fmt_sources(sd.get('production_business', {}))}

### Marketing ({len(sd.get('marketing', {}).get('sources', []))} sources)
{self._fmt_sources(sd.get('marketing', {}))}

### Cultural Impact ({len(sd.get('cultural_impact', {}).get('sources', []))} sources)
{self._fmt_sources(sd.get('cultural_impact', {}))}

## CONTEXT METRICS
- Total Evidence Count: {mini_context.get('evidence_count', 0)}
- Input Confidence Score: {mini_context.get('confidence_score', 0.0)}
- Data Sources: {', '.join(meta.get('data_sources', []))}

Analyze the data above and return the structured JSON intelligence report.
"""

    @staticmethod
    def _fmt_sources(category: dict) -> str:
        sources = category.get("sources", [])
        if not sources:
            return "  (no sources available)"
        lines = []
        for i, s in enumerate(sources, 1):
            lines.append(f"  [{i}] {s.get('title', 'No title')}")
            lines.append(f"      URL: {s.get('url', '')}")
            lines.append(f"      Platform: {s.get('platform', '')}")
            lines.append(f"      Snippet: {s.get('snippet', '')[:350]}")
        return "\n".join(lines)

    def _fallback_output(self, game_id: str, game_name: str) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "metadata": {
                "skill_id": "strategy_market",
                "skill_name": "Strategy and Market",
                "game_id": game_id,
                "game_name": game_name,
                "generated_at": now,
                "model_used": self.model_name,
                "input_evidence_count": 0,
                "input_confidence_score": 0.0,
            },
            "analysis": {
                "audience": {
                    "category_id": "audience",
                    "category_name": "Audience",
                    "overview": "Analysis failed due to system error.",
                    "error": True,
                },
                "business_model": {
                    "category_id": "business_model",
                    "category_name": "Business Model",
                    "overview": "Analysis failed due to system error.",
                    "error": True,
                },
                "retention_live_ops": {
                    "category_id": "retention_live_ops",
                    "category_name": "Retention/Live Ops",
                    "overview": "Analysis failed due to system error.",
                    "error": True,
                },
                "production_business": {
                    "category_id": "production_business",
                    "category_name": "Production/Business",
                    "overview": "Analysis failed due to system error.",
                    "error": True,
                },
                "marketing": {
                    "category_id": "marketing",
                    "category_name": "Marketing",
                    "overview": "Analysis failed due to system error.",
                    "error": True,
                },
                "cultural_impact": {
                    "category_id": "cultural_impact",
                    "category_name": "Cultural Impact",
                    "overview": "Analysis failed due to system error.",
                    "error": True,
                },
            },
            "summary": {
                "strategic_positioning": "Analysis could not be completed due to system error.",
                "standout_strengths": [],
                "critical_weaknesses": [],
                "market_opportunities": [],
                "threats_and_risks": [],
                "competitive_positioning": {
                    "genre_benchmark": "unknown",
                    "unique_selling_points": [],
                    "comparable_titles": [],
                },
                "future_outlook": {
                    "twelve_month_projection": "unknown",
                    "twenty_four_month_projection": "unknown",
                    "key_assumptions": [],
                    "upside_scenarios": [],
                    "downside_scenarios": [],
                },
            },
            "confidence": {
                "overall_score": 0.0,
                "category_scores": {
                    "audience": 0.0,
                    "business_model": 0.0,
                    "retention_live_ops": 0.0,
                    "production_business": 0.0,
                    "marketing": 0.0,
                    "cultural_impact": 0.0,
                },
                "data_quality_notes": ["System error prevented analysis."],
            },
        }
