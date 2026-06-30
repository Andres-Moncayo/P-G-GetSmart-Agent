"""
Strategy & Market Scraper Domain Service.

Phase 1 scraper that extracts business and market-related information about a game.
Focuses on demographics, monetization, market performance, and business metrics.

Output: Mini-Context with hard_data (structured) and semantic_data (search results).
"""

from __future__ import annotations

import logging
from typing import Any

from ..infrastructure.rawg_client import RAWGClient
from ..infrastructure.steam_client import SteamClient
from ..infrastructure.tavily_client import TavilyClient

logger = logging.getLogger(__name__)


class StrategyMarketService:
    """Strategy & Market scraper for extracting business and market information."""

    def __init__(
        self,
        rawg_client: RAWGClient | None = None,
        steam_client: SteamClient | None = None,
        tavily_client: TavilyClient | None = None,
    ) -> None:
        self.rawg_client = rawg_client or RAWGClient()
        self.steam_client = steam_client or SteamClient()
        self.tavily_client = tavily_client or TavilyClient()

    async def extract_strategy_market_context(
        self,
        *,
        game_id: str,
        game_name: str,
        rawg_id: int | None = None,
        steam_app_id: int | None = None,
        aliases: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Extract Strategy & Market Mini-Context for analysis.

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
                "target_audience": list[str],
                "monetization_models": list[str],
                "business_model": str,
                "platforms": list[str],
                "release_info": dict,
                "market_metrics": dict,
                "publisher_info": dict,
                "price_info": dict,
            },
            "semantic_data": {
                "market_analysis": {"sources": []},
                "business_strategy": {"sources": []},
                "audience_demographics": {"sources": []},
                "revenue_performance": {"sources": []},
                "competitive_landscape": {"sources": []},
            }
        }
        """
        aliases = aliases or []
        logger.info("Starting Strategy & Market extraction for: %s", game_name)

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
        """Extract structured market data from game APIs."""
        hard_data = {
            "genres": [],
            "target_audience": [],
            "monetization_models": [],
            "business_model": "",
            "platforms": [],
            "release_info": {
                "release_date": "",
                "early_access": False,
                "platforms": [],
            },
            "market_metrics": {
                "steam_owners": 0,
                "player_count": 0,
                "review_score": "",
            },
            "publisher_info": {
                "developers": [],
                "publishers": [],
                "franchises": [],
            },
            "price_info": {
                "base_price_usd": 0,
                "price_history": [],
                "discount_patterns": [],
            },
        }

        # RAWG extraction
        if rawg_id:
            try:
                rawg_data = await self._fetch_rawg_market_data(rawg_id)
                self._merge_hard_data(hard_data, rawg_data)
                logger.info("RAWG market data extracted for %s", game_name)
            except Exception as e:
                logger.warning("RAWG market extraction failed for %s: %s", game_name, e)
                failed_sources.append("rawg")

        # Steam extraction (critical for market metrics)
        if steam_app_id:
            try:
                steam_data = await self._fetch_steam_market_data(steam_app_id)
                self._merge_hard_data(hard_data, steam_data)
                logger.info("Steam market data extracted for %s", game_name)
            except Exception as e:
                logger.warning("Steam market extraction failed for %s: %s", game_name, e)
                failed_sources.append("steam")

        return hard_data

    async def _extract_semantic_data(
        self, game_name: str, aliases: list[str], hard_data: dict[str, Any], failed_sources: list[str]
    ) -> dict[str, Any]:
        """Extract semantic market data from web searches."""
        semantic_data = {
            "market_analysis": {"sources": []},
            "business_strategy": {"sources": []},
            "audience_demographics": {"sources": []},
            "revenue_performance": {"sources": []},
            "competitive_landscape": {"sources": []},
        }

        genres = hard_data.get("genres", [])
        publishers = hard_data.get("publisher_info", {}).get("publishers", [])

        # Market Analysis Search
        market_query = self._build_market_query(game_name, genres)
        try:
            market_results = await self.tavily_client.search(
                market_query, max_results=3, search_depth="basic"
            )
            semantic_data["market_analysis"]["sources"] = self._format_tavily_results(
                market_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Business Strategy Search
        strategy_query = self._build_strategy_query(game_name, publishers)
        try:
            strategy_results = await self.tavily_client.search(
                strategy_query, max_results=3, search_depth="basic"
            )
            semantic_data["business_strategy"]["sources"] = self._format_tavily_results(
                strategy_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Audience Demographics Search
        demographics_query = self._build_demographics_query(game_name, genres)
        try:
            demographics_results = await self.tavily_client.search(
                demographics_query, max_results=2, search_depth="basic"
            )
            semantic_data["audience_demographics"]["sources"] = self._format_tavily_results(
                demographics_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Revenue Performance Search
        revenue_query = self._build_revenue_query(game_name)
        try:
            revenue_results = await self.tavily_client.search(
                revenue_query, max_results=2, search_depth="basic"
            )
            semantic_data["revenue_performance"]["sources"] = self._format_tavily_results(
                revenue_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Competitive Landscape Search
        competitive_query = self._build_competitive_query(game_name, genres)
        try:
            competitive_results = await self.tavily_client.search(
                competitive_query, max_results=2, search_depth="basic"
            )
            semantic_data["competitive_landscape"]["sources"] = self._format_tavily_results(
                competitive_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        return semantic_data

    async def _fetch_rawg_market_data(self, rawg_id: int) -> dict[str, Any]:
        """Fetch market-relevant data from RAWG."""
        try:
            data = await self.rawg_client.get_game_details(rawg_id)

            return {
                "genres": [g["name"] for g in data.get("genres", [])],
                "target_audience": self._infer_target_from_rawg(data),
                "platforms": [p["platform"]["name"] for p in data.get("platforms", [])],
                "price_info": {
                    "base_price_usd": data.get("stores", [{}])[0].get("price", {}).get("final_usd", 0),
                },
            }
        except Exception:
            return {}

    async def _fetch_steam_market_data(self, steam_app_id: int) -> dict[str, Any]:
        """Fetch comprehensive market data from Steam."""
        try:
            data = await self.steam_client.get_app_details(steam_app_id)

            # Basic market information
            is_free = data.get("is_free", False)
            price_overview = data.get("price_overview", {})
            base_price = price_overview.get("final", 0) / 100 if price_overview else 0  # Convert from cents
            currency = price_overview.get("currency", "USD")

            # Market metrics (limited without Steam API key)
            market_metrics = {
                "steam_owners": 0,  # Would need SteamSpy API for this
                "player_count": 0,  # Would need real-time API for this
                "review_score": "",  # Can get from reviews endpoint
            }

            # Try to get reviews for score
            try:
                reviews = await self.steam_client.get_game_reviews(steam_app_id, limit=100)
                if reviews:
                    positive_count = sum(1 for r in reviews if r.get("voted_up", False))
                    total_count = len(reviews)
                    if total_count > 0:
                        score = positive_count / total_count
                        market_metrics["review_score"] = self._categorize_review_score(score)
            except Exception:
                pass  # Reviews not critical

            return {
                "business_model": "free-to-play" if is_free else "premium",
                "monetization_models": ["free-to-play"] if is_free else ["premium"],
                "platforms": ["Windows", "Mac", "Linux"][:len(data.get("platforms", []))],
                "market_metrics": market_metrics,
                "price_info": {
                    "base_price_usd": base_price,
                    "currency": currency,
                    "price_history": [],  # Would need additional API calls
                    "discount_patterns": [],  # Would need historical data
                },
            }
        except Exception:
            return {}

    def _merge_hard_data(self, base: dict[str, Any], new: dict[str, Any]) -> None:
        """Merge new hard data into base data, handling special cases."""
        for key, value in new.items():
            if key in base and isinstance(base[key], list) and isinstance(value, list):
                # Deduplicate and merge
                base[key] = list(set(base[key] + value))
            elif key in base and isinstance(base[key], dict) and isinstance(value, dict):
                # Merge dictionaries
                base[key].update(value)
            elif key not in base:
                base[key] = value

    def _determine_target_audience(self, genres: list[str], perspectives: list[str]) -> list[str]:
        """Determine target audience from genres and player perspectives."""
        audience = []
        
        # Genre-based audience mapping
        genre_audience_map = {
            "Adventure": "casual_adventure",
            "RPG": "hardcore_rpg",
            "Shooter": "multiplayer_shooter",
            "Strategy": "strategy_enthusiast",
            "Puzzle": "casual_puzzle",
            "Racing": "simulation_racing",
            "Sports": "sports_fan",
            "Simulation": "simulation_enthusiast",
            "Fighting": "competitive_fighting",
            "Platform": "platform_enthusiast",
        }
        
        for genre in genres:
            audience_genres = [value for key, value in genre_audience_map.items() if key.lower() in genre.lower()]
            audience.extend(audience_genres)
        
        # Perspective-based audience
        if "first person" in [p.lower() for p in perspectives]:
            audience.append("fps_player")
        if "third person" in [p.lower() for p in perspectives]:
            audience.append("tps_player")
        if "bird's eye" in [p.lower() for p in perspectives]:
            audience.append("top_down_player")
            
        return list(set(audience)) or ["general_gamer"]

    def _extract_monetization_from_keywords(self, keywords: list[dict[str, Any]]) -> list[str]:
        """Extract monetization models from metadata keywords."""
        monetization_keywords = []
        monetization_map = {
            "free": "free-to-play",
            "premium": "premium",
            "freemium": "freemium",
            "subscription": "subscription",
            "microtransactions": "microtransactions",
            "loot boxes": "loot_boxes",
            "dlc": "downloadable_content",
            "season pass": "season_pass",
            "battle pass": "battle_pass",
        }
        
        for keyword in keywords:
            keyword_name = keyword.get("name", "").lower()
            for key, value in monetization_map.items():
                if key in keyword_name:
                    monetization_keywords.append(value)
                    
        return list(set(monetization_keywords))

    def _infer_business_model(self, genres: list[str], game_modes: list[dict[str, Any]]) -> str:
        """Infer business model from genres and game modes."""
        genres_str = " ".join([g.lower() for g in genres])
        
        if any(indicator in genres_str for indicator in ["free-to-play", "mmorpg", "mobile"]):
            return "free-to-play"
        elif any(indicator in genres_str for indicator in ["indie", "puzzle", "visual novel"]):
            return "premium_indie"
        else:
            return "premium"

    def _infer_target_from_rawg(self, data: dict[str, Any]) -> list[str]:
        """Infer target audience from RAWG data."""
        # RAWG-specific audience inference logic
        audience = []
        if data.get("esrb_rating"):
            rating = data.get("esrb_rating", {}).get("name", "")
            if "teen" in rating.lower():
                audience.append("teen")
            elif "mature" in rating.lower():
                audience.append("mature")
            else:
                audience.append("everyone")
                
        return audience or ["general_gamer"]

    def _categorize_review_score(self, score: float) -> str:
        """Categorize review score from 0-1 confidence."""
        if score >= 0.85:
            return "overwhelmingly_positive"
        elif score >= 0.8:
            return "very_positive"
        elif score >= 0.7:
            return "mostly_positive"
        elif score >= 0.4:
            return "mixed"
        elif score >= 0.2:
            return "mostly_negative"
        else:
            return "very_negative"

    def _build_market_query(self, game_name: str, genres: list[str]) -> str:
        """Build market analysis search query."""
        genre_part = f" {' '.join(genres[:2])}" if genres else ""
        return f'"{game_name}"{genre_part} market analysis sales performance business model'

    def _build_strategy_query(self, game_name: str, publishers: list[str]) -> str:
        """Build business strategy search query."""
        publisher_part = f" {' '.join(publishers[:2])}" if publishers else ""
        return f'"{game_name}"{publisher_part} business strategy developer interview monetization pricing'

    def _build_demographics_query(self, game_name: str, genres: list[str]) -> str:
        """Build audience demographics search query."""
        genre_part = f" {' '.join(genres[:2])}" if genres else ""
        return f'"{game_name}"{genre_part} target audience demographics age range player base'

    def _build_revenue_query(self, game_name: str) -> str:
        """Build revenue performance search query."""
        return f'"{game_name}" revenue sales numbers financial performance market success'

    def _build_competitive_query(self, game_name: str, genres: list[str]) -> str:
        """Build competitive landscape search query."""
        genre_part = f" {' '.join(genres[:2])}" if genres else ""
        return f'"{game_name}"{genre_part} similar games competitive landscape market competitors'

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
        elif "gamesindustry.biz" in url_lower or "venturebeat.com" in url_lower:
            return "industry"
        elif "metacritic.com" in url_lower or "opencritic.com" in url_lower:
            return "review_aggregator"
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
        # Critical fields for market analysis
        critical_fields = ["genres", "platforms", "publisher_info", "price_info"]
        critical_filled = sum(1 for field in critical_fields if hard_data.get(field))
        critical_confidence = critical_filled / len(critical_fields)

        # Overall hard data coverage
        hard_fields_filled = sum(1 for v in hard_data.values() if v)
        total_hard_fields = len(hard_data)
        hard_confidence = hard_fields_filled / total_hard_fields if total_hard_fields > 0 else 0

        # Boost from semantic data
        semantic_sources = sum(len(cat.get("sources", [])) for cat in semantic_data.values())
        semantic_confidence = min(semantic_sources / 12, 0.3)  # Max 0.3 boost

        # Weight critical fields more heavily
        weighted_confidence = (critical_confidence * 0.5) + (hard_confidence * 0.2) + semantic_confidence
        
        return min(weighted_confidence, 1.0)

    def _identify_data_sources(self, hard_data: dict[str, Any], semantic_data: dict[str, Any]) -> list[str]:
        """Identify which data sources contributed information."""
        sources = set()
        
        if hard_data.get("genres"):
            sources.add("rawg")
        if hard_data.get("price_info", {}).get("base_price_usd"):
            sources.add("steam")
        if hard_data.get("platforms"):
            sources.update(["rawg", "steam"])
            
        # Check semantic sources
        for category in semantic_data.values():
            for source in category.get("sources", []):
                platform = source.get("platform", "")
                if platform and platform != "general":
                    sources.add(platform)
                    
        return sorted(list(sources)) or ["unknown"]