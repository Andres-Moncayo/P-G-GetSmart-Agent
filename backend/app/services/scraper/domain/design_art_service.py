"""
Design & Art Scraper Domain Service.

Phase 1 scraper that extracts design and art-related information about a game.
Focuses on game mechanics, art style, story elements, and creative aspects.

Output: Mini-Context with hard_data (structured) and semantic_data (search results).
"""

from __future__ import annotations

import logging
from typing import Any

from ..infrastructure.rawg_client import RAWGClient
from ..infrastructure.steam_client import SteamClient
from ..infrastructure.tavily_client import TavilyClient

logger = logging.getLogger(__name__)


class DesignArtService:
    """Design & Art scraper for extracting game creative and mechanical information."""

    def __init__(
        self,
        rawg_client: RAWGClient | None = None,
        steam_client: SteamClient | None = None,
        tavily_client: TavilyClient | None = None,
    ) -> None:
        self.rawg_client = rawg_client or RAWGClient()
        self.steam_client = steam_client or SteamClient()
        self.tavily_client = tavily_client or TavilyClient()

    async def extract_design_art_context(
        self,
        *,
        game_id: str,
        game_name: str,
        rawg_id: int | None = None,
        steam_app_id: int | None = None,
        aliases: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Extract Design & Art Mini-Context for analysis.

        Returns Mini-Context structure:
        {
            "metadata": {
                "game_id": str,
                "game_name": str,
                "confidence_score": float,
                "data_sources": list[str],
                "evidence_count": int,
            },
            "hard_data": {
                "genres": list[str],
                "themes": list[str],
                "game_modes": list[str],
                "player_perspectives": list[str],
                "art_styles": list[str],
                "gameplay_mechanics": list[str],
                "story_elements": list[str],
                "visual_engine": str,
                "graphics_types": list[str],
                "platforms": list[str],
                "release_dates": dict[str, str],
            },
            "semantic_data": {
                "gameplay_analysis": {"sources": []},
                "art_design": {"sources": []},
                "story_narrative": {"sources": []},
                "visual_aesthetics": {"sources": []},
                "design_philosophy": {"sources": []},
            }
        }
        """
        aliases = aliases or []
        logger.info("Starting Design & Art extraction for: %s", game_name)

        # Collect hard data from APIs
        hard_data = await self._extract_hard_data(
            game_name=game_name,
            rawg_id=rawg_id,
            steam_app_id=steam_app_id,
            aliases=aliases,
        )

        # Collect semantic data from web search
        semantic_data = await self._extract_semantic_data(
            game_name=game_name,
            aliases=aliases,
            hard_data=hard_data,
        )

        # Calculate evidence counts and confidence
        evidence_count = self._count_evidence(hard_data, semantic_data)
        confidence_score = self._calculate_confidence(hard_data, semantic_data)
        data_sources = self._identify_data_sources(hard_data, semantic_data)

        return {
            "metadata": {
                "game_id": game_id,
                "game_name": game_name,
                "confidence_score": confidence_score,
                "data_sources": data_sources,
                "evidence_count": evidence_count,
            },
            "hard_data": hard_data,
            "semantic_data": semantic_data,
        }

    async def _extract_hard_data(
        self,
        game_name: str,
        rawg_id: int | None,
        steam_app_id: int | None,
        aliases: list[str],
    ) -> dict[str, Any]:
        """Extract structured data from game APIs."""
        hard_data = {
            "genres": [],
            "themes": [],
            "game_modes": [],
            "player_perspectives": [],
            "art_styles": [],
            "gameplay_mechanics": [],
            "story_elements": [],
            "visual_engine": "",
            "graphics_types": [],
            "platforms": [],
            "release_dates": {},
        }

        # RAWG extraction
        if rawg_id:
            try:
                rawg_data = await self._fetch_rawg_design_data(rawg_id)
                self._merge_hard_data(hard_data, rawg_data)
                logger.info("RAWG data extracted for %s", game_name)
            except Exception as e:
                logger.warning("RAWG extraction failed for %s: %s", game_name, e)

        # Steam extraction
        if steam_app_id:
            try:
                steam_data = await self._fetch_steam_design_data(steam_app_id)
                self._merge_hard_data(hard_data, steam_data)
                logger.info("Steam data extracted for %s", game_name)
            except Exception as e:
                logger.warning("Steam extraction failed for %s: %s", game_name, e)

        return hard_data

    async def _extract_semantic_data(
        self, game_name: str, aliases: list[str], hard_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract semantic data from web searches."""
        semantic_data = {
            "gameplay_analysis": {"sources": []},
            "art_design": {"sources": []},
            "story_narrative": {"sources": []},
            "visual_aesthetics": {"sources": []},
            "design_philosophy": {"sources": []},
        }

        # Build search queries based on hard data
        genres = hard_data.get("genres", [])
        gameplay_mechanics = hard_data.get("gameplay_mechanics", [])

        # Gameplay Analysis Search
        gameplay_query = self._build_gameplay_query(game_name, genres, gameplay_mechanics)
        try:
            gameplay_results = await self.tavily_client.search(
                gameplay_query, max_results=3, search_depth="basic"
            )
            semantic_data["gameplay_analysis"]["sources"] = self._format_tavily_results(
                gameplay_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Gameplay search failed for %s: %s", game_name, e)

        # Art & Design Search
        art_query = self._build_art_query(game_name, genres)
        try:
            art_results = await self.tavily_client.search(
                art_query, max_results=3, search_depth="basic"
            )
            semantic_data["art_design"]["sources"] = self._format_tavily_results(
                art_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Art design search failed for %s: %s", game_name, e)

        # Story & Narrative Search
        story_query = self._build_story_query(game_name)
        try:
            story_results = await self.tavily_client.search(
                story_query, max_results=2, search_depth="basic"
            )
            semantic_data["story_narrative"]["sources"] = self._format_tavily_results(
                story_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Story search failed for %s: %s", game_name, e)

        # Visual Aesthetics Search
        visual_query = self._build_visual_query(game_name, hard_data.get("art_styles", []))
        try:
            visual_results = await self.tavily_client.search(
                visual_query, max_results=2, search_depth="basic"
            )
            semantic_data["visual_aesthetics"]["sources"] = self._format_tavily_results(
                visual_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Visual search failed for %s: %s", game_name, e)

        # Design Philosophy Search
        design_query = self._build_design_philosophy_query(game_name)
        try:
            design_results = await self.tavily_client.search(
                design_query, max_results=2, search_depth="basic"
            )
            semantic_data["design_philosophy"]["sources"] = self._format_tavily_results(
                design_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Design philosophy search failed for %s: %s", game_name, e)

        return semantic_data

    async def _fetch_rawg_design_data(self, rawg_id: int) -> dict[str, Any]:
        """Fetch design-relevant data from RAWG."""
        try:
            data = await self.rawg_client.get_game_details(rawg_id)
            return {
                "genres": [g["name"] for g in data.get("genres", [])],
                "gameplay_mechanics": [t["name"] for t in data.get("tags", [])[:15]],
                "platforms": [p["platform"]["name"] for p in data.get("platforms", [])],
            }
        except Exception:
            return {}

    async def _fetch_steam_design_data(self, steam_app_id: int) -> dict[str, Any]:
        """Fetch design-relevant data from Steam."""
        try:
            data = await self.steam_client.get_app_details(steam_app_id)
            categories = [c["description"] for c in data.get("categories", [])]
            genres = [g["description"] for g in data.get("genres", [])]
            
            gameplay_mechs = []
            for cat in categories:
                if any(keyword in cat.lower() for keyword in ["multi", "single", "co-op", "pvp"]):
                    gameplay_mechs.append(cat)
            
            return {
                "game_modes": gameplay_mechs,
                "genres": genres,
                "platforms": ["Windows"] if data.get("type") == "game" else [],
            }
        except Exception:
            return {}

    def _merge_hard_data(self, base: dict[str, Any], new: dict[str, Any]) -> None:
        """Merge new hard data into base data, deduplicating lists."""
        for key, value in new.items():
            if key in base and isinstance(base[key], list) and isinstance(value, list):
                # Deduplicate and merge
                base[key] = list(set(base[key] + value))
            elif key not in base:
                base[key] = value

    def _build_gameplay_query(
        self, game_name: str, genres: list[str], mechanics: list[str]
    ) -> str:
        """Build gameplay-focused search query."""
        base_query = f'"{game_name}" gameplay mechanics design analysis'
        if genres:
            base_query += f" {genres[0]}" if len(genres) == 1 else f" {' '.join(genres[:2])}"
        if mechanics:
            base_query += f" {mechanics[0]}" if len(mechanics) == 1 else f" {' '.join(mechanics[:2])}"
        return base_query

    def _build_art_query(self, game_name: str, genres: list[str]) -> str:
        """Build art & design search query."""
        return f'"{game_name}" art style visual design aesthetics {(" ".join(genres[:2]) if genres else "")}'

    def _build_story_query(self, game_name: str) -> str:
        """Build story & narrative search query."""
        return f'"{game_name}" story narrative plot analysis themes'

    def _build_visual_query(self, game_name: str, art_styles: list[str]) -> str:
        """Build visual aesthetics search query."""
        additional = f" {' '.join(art_styles[:2])}" if art_styles else ""
        return f'"{game_name}" visual aesthetics graphics design {additional}'

    def _build_design_philosophy_query(self, game_name: str) -> str:
        """Build design philosophy search query."""
        return f'"{game_name}" design philosophy developer interview game design decisions'

    def _format_tavily_results(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Format Tavily search results for consumption."""
        formatted = []
        for result in results[:10]:  # Limit to 10 results max
            formatted.append(
                {
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "snippet": result.get("content", ""),
                    "platform": self._detect_platform(result.get("url", "")),
                }
            )
        return formatted

    def _detect_platform(self, url: str) -> str:
        """Detect content platform from URL."""
        url_lower = url.lower()
        if "reddit.com" in url_lower:
            return "reddit"
        elif "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "youtube"
        elif "steam" in url_lower:
            return "steam"
        elif "ign.com" in url_lower:
            return "press"
        else:
            return "general"

    def _count_evidence(self, hard_data: dict[str, Any], semantic_data: dict[str, Any]) -> int:
        """Count total evidence pieces from both hard and semantic data."""
        count = sum(len(v) if isinstance(v, list) else 1 for v in hard_data.values() if v)
        
        for category in semantic_data.values():
            sources = category.get("sources", [])
            count += len(sources)
            
        return count

    def _calculate_confidence(self, hard_data: dict[str, Any], semantic_data: dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness."""
        # Base confidence from hard data
        hard_fields_filled = sum(1 for v in hard_data.values() if v)
        total_hard_fields = len(hard_data)
        hard_confidence = hard_fields_filled / total_hard_fields if total_hard_fields > 0 else 0

        # Boost from semantic data
        semantic_sources = sum(len(cat.get("sources", [])) for cat in semantic_data.values())
        semantic_confidence = min(semantic_sources / 10, 0.3)  # Max 0.3 boost from semantic

        total_confidence = hard_confidence + semantic_confidence
        return min(total_confidence, 1.0)

    def _identify_data_sources(self, hard_data: dict[str, Any], semantic_data: dict[str, Any]) -> list[str]:
        """Identify which data sources contributed information."""
        sources = set()
        
        if hard_data.get("genres") or hard_data.get("themes"):
            sources.add("rawg")
        if hard_data.get("platforms"):
            sources.update(["rawg", "steam"])
            
        # Check semantic sources
        for category in semantic_data.values():
            for source in category.get("sources", []):
                platform = source.get("platform", "")
                if platform and platform != "general":
                    sources.add(platform)
                    
        return sorted(list(sources)) or ["unknown"]