"""
User Experience Scraper Domain Service.

Phase 1 scraper that extracts UX-related information about a game.
Focuses on UI, accessibility, localization, controller support, and player experience.

Output: Mini-Context with hard_data (structured) and semantic_data (search results).
"""

from __future__ import annotations

import logging
from typing import Any

from ..infrastructure.rawg_client import RAWGClient
from ..infrastructure.steam_client import SteamClient
from ..infrastructure.tavily_client import TavilyClient

logger = logging.getLogger(__name__)


class UserExperienceService:
    """User Experience scraper for extracting UX and accessibility information."""

    def __init__(
        self,
        rawg_client: RAWGClient | None = None,
        steam_client: SteamClient | None = None,
        tavily_client: TavilyClient | None = None,
    ) -> None:
        self.rawg_client = rawg_client or RAWGClient()
        self.steam_client = steam_client or SteamClient()
        self.tavily_client = tavily_client or TavilyClient()

    async def extract_user_experience_context(
        self,
        *,
        game_id: str,
        game_name: str,
        rawg_id: int | None = None,
        steam_app_id: int | None = None,
        aliases: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Extract User Experience Mini-Context for analysis.

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
                "platforms": list[str],
                "controller_support": bool,
                "full_controller_support": bool,
                "languages_supported": list[str],
                "accessibility_features": list[str],
                "ui_features": list[str],
                "steam_cloud": bool,
                "steam_achievements": bool,
                "system_requirements": dict,
                "multiplayer_features": list[str],
            },
            "semantic_data": {
                "ui_ux": {"sources": []},
                "accessibility": {"sources": []},
                "localization": {"sources": []},
                "steam_reviews_sample": {
                    "positive_count": int,
                    "negative_count": int,
                    "review_score": str,
                    "sample_reviews": list[dict],
                }
            }
        }
        """
        aliases = aliases or []
        logger.info("Starting User Experience extraction for: %s", game_name)

        failed_sources: list[str] = []

        # Collect hard data from APIs
        hard_data = await self._extract_hard_data(
            game_name=game_name,
            rawg_id=rawg_id,
            steam_app_id=steam_app_id,
            aliases=aliases,
            failed_sources=failed_sources,
        )

        # Collect semantic data from web search
        semantic_data = await self._extract_semantic_data(
            game_name=game_name,
            aliases=aliases,
            steam_app_id=steam_app_id,
            hard_data=hard_data,
            failed_sources=failed_sources,
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
                "failed_sources": list(set(failed_sources)),
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
        failed_sources: list[str],
    ) -> dict[str, Any]:
        """Extract structured UX data from game APIs."""
        hard_data = {
            "platforms": [],
            "controller_support": False,
            "full_controller_support": False,
            "languages_supported": [],
            "accessibility_features": [],
            "ui_features": [],
            "steam_cloud": False,
            "steam_achievements": False,
            "system_requirements": {},
            "multiplayer_features": [],
        }

        # RAWG extraction
        if rawg_id:
            try:
                rawg_data = await self._fetch_rawg_ux_data(rawg_id)
                self._merge_hard_data(hard_data, rawg_data)
                logger.info("RAWG UX data extracted for %s", game_name)
            except Exception as e:
                logger.warning("RAWG UX extraction failed for %s: %s", game_name, e)
                failed_sources.append("rawg")

        # Steam extraction (critical for UX data)
        if steam_app_id:
            try:
                steam_data = await self._fetch_steam_ux_data(steam_app_id)
                self._merge_hard_data(hard_data, steam_data)
                logger.info("Steam UX data extracted for %s", game_name)
            except Exception as e:
                logger.warning("Steam UX extraction failed for %s: %s", game_name, e)
                failed_sources.append("steam")

        return hard_data

    async def _extract_semantic_data(
        self,
        game_name: str,
        aliases: list[str],
        steam_app_id: int | None,
        hard_data: dict[str, Any],
        failed_sources: list[str],
    ) -> dict[str, Any]:
        """Extract semantic UX data from web searches and reviews."""
        semantic_data = {
            "ui_ux": {"sources": []},
            "accessibility": {"sources": []},
            "localization": {"sources": []},
            "steam_reviews_sample": {
                "positive_count": 0,
                "negative_count": 0,
                "review_score": None,
                "sample_reviews": [],
            },
        }

        # UI/UX Analysis Search
        ux_query = self._build_ux_query(game_name)
        try:
            ux_results = await self.tavily_client.search(
                ux_query, max_results=3, search_depth="basic"
            )
            semantic_data["ui_ux"]["sources"] = self._format_tavily_results(
                ux_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Accessibility Search
        accessibility_query = self._build_accessibility_query(game_name)
        try:
            accessibility_results = await self.tavily_client.search(
                accessibility_query, max_results=3, search_depth="basic"
            )
            semantic_data["accessibility"]["sources"] = self._format_tavily_results(
                accessibility_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Localization Search
        localization_query = self._build_localization_query(game_name)
        try:
            localization_results = await self.tavily_client.search(
                localization_query, max_results=2, search_depth="basic"
            )
            semantic_data["localization"]["sources"] = self._format_tavily_results(
                localization_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Steam Reviews Sample (very important for UX analysis)
        if steam_app_id:
            try:
                reviews_data = await self._fetch_steam_reviews_sample(steam_app_id)
                semantic_data["steam_reviews_sample"] = reviews_data
                logger.info("Steam reviews sample extracted for %s", game_name)
            except Exception as e:
                logger.warning("Steam reviews extraction failed for %s: %s", game_name, e)

        return semantic_data

    async def _fetch_rawg_ux_data(self, rawg_id: int) -> dict[str, Any]:
        """Fetch UX-relevant data from RAWG."""
        try:
            data = await self.rawg_client.get_game_details(rawg_id)
            platforms = [p["platform"]["name"] for p in data.get("platforms", [])]
            features = []
            
            # Check for common UX features
            if data.get("esrb_rating"):
                features.append(f"ESRB: {data['esrb_rating']['name']}")
                
            return {
                "platforms": platforms,
                "ui_features": features,
            }
        except Exception:
            return {}

    async def _fetch_steam_ux_data(self, steam_app_id: int) -> dict[str, Any]:
        """Fetch comprehensive UX data from Steam."""
        try:
            data = await self.steam_client.get_app_details(steam_app_id)
            
            # Controller support
            categories = data.get("categories", [])
            controller_support = any(
                "controller" in cat["description"].lower() for cat in categories
            )
            full_controller_support = any(
                "full controller" in cat["description"].lower() for cat in categories
            )

            # Steam features
            steam_features = [f["description"] for f in data.get("features", [])]
            
            # Languages from Steam API (if available)
            languages = data.get("supported_languages", "")
            language_list = [lang.strip() for lang in languages.split("*") if lang.strip()] if languages else []

            return {
                "platforms": ["Windows", "Mac", "Linux"][:len(data.get("platforms", []))],
                "controller_support": controller_support,
                "full_controller_support": full_controller_support,
                "languages_supported": language_list,
                "steam_cloud": any("cloud" in f.lower() for f in steam_features),
                "steam_achievements": any("achievements" in f.lower() for f in steam_features),
                "multiplayer_features": [
                    cat["description"] for cat in categories
                    if any(keyword in cat["description"].lower() for keyword in ["multi", "online", "co-op"])
                ],
                "system_requirements": {
                    "minimum": data.get("pc_requirements", {}).get("minimum", "")[:500],
                    "recommended": data.get("pc_requirements", {}).get("recommended", "")[:500],
                },
            }
        except Exception:
            return {}

    async def _fetch_steam_reviews_sample(self, steam_app_id: int) -> dict[str, Any]:
        """Fetch sample Steam reviews for UX analysis."""
        try:
            reviews = await self.steam_client.get_game_reviews(steam_app_id, limit=20)
            
            # Extract positive/negative counts and sample reviews
            positive_count = sum(1 for r in reviews if r.get("voted_up", False))
            negative_count = len(reviews) - positive_count
            
            # Calculate simple review score
            if reviews:
                score = positive_count / len(reviews)
                if score >= 0.8:
                    rating = "Very Positive"
                elif score >= 0.6:
                    rating = "Mostly Positive" 
                elif score >= 0.4:
                    rating = "Mixed"
                elif score >= 0.2:
                    rating = "Mostly Negative"
                else:
                    rating = "Very Negative"
            else:
                rating = "No Reviews"

            # Sample representative reviews (up to 5)
            sample_reviews = []
            if reviews:
                # Mix of positive and negative reviews
                positive_reviews = [r for r in reviews if r.get("voted_up", False)][:3]
                negative_reviews = [r for r in reviews if not r.get("voted_up", False)][:2]
                sample_reviews = positive_reviews + negative_reviews

            return {
                "positive_count": positive_count,
                "negative_count": negative_count,
                "review_score": rating,
                "sample_reviews": [
                    {
                        "review": r.get("review", ""),
                        "playtime_hours": r.get("author", {}).get("playtime_forever", 0) / 60,
                        "voted_up": r.get("voted_up", False),
                        "language": r.get("author", {}).get("steamid", "")[:2],  # Simplified
                    }
                    for r in sample_reviews[:5]
                ],
            }
        except Exception:
            return {
                "positive_count": 0,
                "negative_count": 0,
                "review_score": "No Reviews",
                "sample_reviews": [],
            }

    def _merge_hard_data(self, base: dict[str, Any], new: dict[str, Any]) -> None:
        """Merge new hard data into base data, deduplicating lists."""
        for key, value in new.items():
            if key in base and isinstance(base[key], list) and isinstance(value, list):
                # Deduplicate and merge
                base[key] = list(set(base[key] + value))
            elif key not in base:
                base[key] = value

    def _build_ux_query(self, game_name: str) -> str:
        """Build UI/UX-focused search query."""
        return f'"{game_name}" user interface design menu navigation controls UX problems'

    def _build_accessibility_query(self, game_name: str) -> str:
        """Build accessibility-focused search query."""
        return f'"{game_name}" accessibility features colorblind subtitles controller options'

    def _build_localization_query(self, game_name: str) -> str:
        """Build localization-focused search query."""
        return f'"{game_name}" localization languages translation international regional pricing'

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
        elif "ign.com" in url_lower or "gamespot.com" in url_lower:
            return "press"
        elif "accessibility.com" in url_lower or "game-accessibility.com" in url_lower:
            return "specialized"
        else:
            return "forums"

    def _is_ui_feature(self, keyword: str) -> bool:
        """Check if keyword relates to UI features."""
        ui_keywords = [
            "menu", "interface", "controls", "ui", "ux", "accessibility",
            "colorblind", "subtitle", "controller", "keyboard", "mouse"
        ]
        return any(ui_keyword in keyword.lower() for ui_keyword in ui_keywords)

    def _count_evidence(self, hard_data: dict[str, Any], semantic_data: dict[str, Any]) -> int:
        """Count total evidence pieces from both hard and semantic data."""
        count = sum(len(v) if isinstance(v, list) else 1 for v in hard_data.values() if v)
        
        for category in semantic_data.values():
            if category == "steam_reviews_sample":
                # Count review samples as evidence
                reviews = category.get("sample_reviews", [])
                count += len(reviews)
                if category.get("review_score"):
                    count += 1
            else:
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
        semantic_sources = sum(len(cat.get("sources", [])) for cat in semantic_data.values() 
                             if cat != "steam_reviews_sample")
        
        # Reviews provide strong evidence
        review_samples = len(semantic_data.get("steam_reviews_sample", {}).get("sample_reviews", []))
        review_confidence = min(review_samples / 5, 0.2)  # Max 0.2 boost from reviews
        
        semantic_confidence = min(semantic_sources / 8, 0.3) + review_confidence  # Max 0.5 boost total

        total_confidence = hard_confidence + semantic_confidence
        return min(total_confidence, 1.0)

    def _identify_data_sources(self, hard_data: dict[str, Any], semantic_data: dict[str, Any]) -> list[str]:
        """Identify which data sources contributed information."""
        sources = set()
        
        if hard_data.get("platforms"):
            sources.add("steam")
            
        if hard_data.get("languages_supported"):
            sources.add("steam")
            
        # Check semantic sources
        for category in semantic_data.values():
            if category == "steam_reviews_sample":
                sources.add("steam_reviews")
            else:
                for source in category.get("sources", []):
                    platform = source.get("platform", "")
                    if platform and platform != "general":
                        sources.add(platform)
                    
        return sorted(list(sources)) or ["unknown"]