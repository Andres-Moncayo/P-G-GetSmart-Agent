"""
Technology Systems Scraper Domain Service.

Phase 1 scraper that extracts technical and performance-related information about a game.
Focuses on engine technology, system requirements, networking, and technical specs.

Output: Mini-Context with hard_data (structured) and semantic_data (search results).
"""

from __future__ import annotations

import logging
from typing import Any

from ..infrastructure.rawg_client import RAWGClient
from ..infrastructure.steam_client import SteamClient
from ..infrastructure.tavily_client import TavilyClient

logger = logging.getLogger(__name__)


class TechnologySystemsService:
    """Technology Systems scraper for extracting technical and performance information."""

    def __init__(
        self,
        rawg_client: RAWGClient | None = None,
        steam_client: SteamClient | None = None,
        tavily_client: TavilyClient | None = None,
    ) -> None:
        self.rawg_client = rawg_client or RAWGClient()
        self.steam_client = steam_client or SteamClient()
        self.tavily_client = tavily_client or TavilyClient()

    async def extract_technology_systems_context(
        self,
        *,
        game_id: str,
        game_name: str,
        rawg_id: int | None = None,
        steam_app_id: int | None = None,
        aliases: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Extract Technology Systems Mini-Context for analysis.

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
                "game_engine": str,
                "engine_details": dict,
                "system_requirements": {
                    "minimum": str,
                    "recommended": str,
                    "platforms": list[str],
                },
                "platforms": list[str],
                "multiplayer_technology": list[str],
                "network_features": list[str],
                "performance_specs": dict,
                "technology_stack": list[str],
                "file_size_info": str,
            },
            "semantic_data": {
                "engine_performance": {"sources": []},
                "technical_analysis": {"sources": []},
                "performance_issues": {"sources": []},
                "network_performance": {"sources": []},
                "developer_tech": {"sources": []},
            }
        }
        """
        aliases = aliases or []
        logger.info("Starting Technology Systems extraction for: %s", game_name)

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
        """Extract structured technical data from game APIs."""
        hard_data = {
            "game_engine": "",
            "engine_details": {},
            "system_requirements": {
                "minimum": "",
                "recommended": "",
                "platforms": [],
            },
            "platforms": [],
            "multiplayer_technology": [],
            "network_features": [],
            "performance_specs": {
                "file_size_mb": 0,
                "memory_gb": 0,
                "storage_gb": 0,
            },
            "technology_stack": [],
            "file_size_info": "",
        }

        # RAWG extraction
        if rawg_id:
            try:
                rawg_data = await self._fetch_rawg_tech_data(rawg_id)
                self._merge_hard_data(hard_data, rawg_data)
                logger.info("RAWG technical data extracted for %s", game_name)
            except Exception as e:
                logger.warning("RAWG technical extraction failed for %s: %s", game_name, e)
                failed_sources.append("rawg")

        # Steam extraction (critical for system requirements)
        if steam_app_id:
            try:
                steam_data = await self._fetch_steam_tech_data(steam_app_id)
                self._merge_hard_data(hard_data, steam_data)
                logger.info("Steam technical data extracted for %s", game_name)
            except Exception as e:
                logger.warning("Steam technical extraction failed for %s: %s", game_name, e)
                failed_sources.append("steam")

        return hard_data

    async def _extract_semantic_data(
        self, game_name: str, aliases: list[str], hard_data: dict[str, Any], failed_sources: list[str]
    ) -> dict[str, Any]:
        """Extract semantic technical data from web searches."""
        semantic_data = {
            "engine_performance": {"sources": []},
            "technical_analysis": {"sources": []},
            "performance_issues": {"sources": []},
            "network_performance": {"sources": []},
            "developer_tech": {"sources": []},
        }

        game_engine = hard_data.get("game_engine", "")
        platforms = hard_data.get("platforms", [])

        # Engine Performance Search
        engine_query = self._build_engine_query(game_name, game_engine)
        try:
            engine_results = await self.tavily_client.search(
                engine_query, max_results=3, search_depth="basic"
            )
            semantic_data["engine_performance"]["sources"] = self._format_tavily_results(
                engine_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Technical Analysis Search
        tech_query = self._build_tech_analysis_query(game_name, platforms)
        try:
            tech_results = await self.tavily_client.search(
                tech_query, max_results=3, search_depth="basic"
            )
            semantic_data["technical_analysis"]["sources"] = self._format_tavily_results(
                tech_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Performance Issues Search
        performance_query = self._build_performance_query(game_name)
        try:
            performance_results = await self.tavily_client.search(
                performance_query, max_results=3, search_depth="basic"
            )
            semantic_data["performance_issues"]["sources"] = self._format_tavily_results(
                performance_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Network/Online Performance Search
        network_query = self._build_network_query(game_name)
        try:
            network_results = await self.tavily_client.search(
                network_query, max_results=2, search_depth="basic"
            )
            semantic_data["network_performance"]["sources"] = self._format_tavily_results(
                network_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        # Developer Technical Interview Search
        dev_tech_query = self._build_dev_tech_query(game_name, game_engine)
        try:
            dev_tech_results = await self.tavily_client.search(
                dev_tech_query, max_results=2, search_depth="basic"
            )
            semantic_data["developer_tech"]["sources"] = self._format_tavily_results(
                dev_tech_results.get("results", [])
            )
        except Exception as e:
            logger.warning("Search failed for %s: %s", game_name, e)
            failed_sources.append("tavily")

        return semantic_data

    async def _fetch_rawg_tech_data(self, rawg_id: int) -> dict[str, Any]:
        """Fetch technical-relevant data from RAWG."""
        try:
            data = await self.rawg_client.get_game_details(rawg_id)
            
            # Extract file size information
            file_size = data.get("website", "")  # RAWG may have size info in various fields
            
            return {
                "platforms": [p["platform"]["name"] for p in data.get("platforms", [])],
                "file_size_info": self._extract_file_size(data),
            }
        except Exception:
            return {}

    async def _fetch_steam_tech_data(self, steam_app_id: int) -> dict[str, Any]:
        """Fetch comprehensive technical data from Steam."""
        try:
            data = await self.steam_client.get_app_details(steam_app_id)
            
            # System requirements are critical
            pc_requirements = data.get("pc_requirements", {})
            minimum_req = pc_requirements.get("minimum", "")
            recommended_req = pc_requirements.get("recommended", "")
            
            # Extract file size and memory info
            file_size_mb = self._extract_system_specs(minimum_req + " " + recommended_req)
            
            # Platform information
            platforms = data.get("platforms", [])
            supported_platforms = []
            if platforms:
                if "windows" in str(platforms).lower():
                    supported_platforms.append("Windows")
                if "mac" in str(platforms).lower():
                    supported_platforms.append("macOS")
                if "linux" in str(platforms).lower():
                    supported_platforms.append("Linux")

            # Network features from categories
            categories = data.get("categories", [])
            network_features = [
                cat["description"] for cat in categories
                if any(keyword in cat["description"].lower() for keyword in ["online", "multi", "network", "pvp"])
            ]

            return {
                "system_requirements": {
                    "minimum": minimum_req[:400] if minimum_req else "",
                    "recommended": recommended_req[:400] if recommended_req else "",
                    "platforms": supported_platforms,
                },
                "platforms": supported_platforms,
                "network_features": network_features,
                "performance_specs": {
                    **file_size_mb,
                },
                "file_size_info": data.get("file_size", ""),
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

    def _extract_tech_keywords(self, keywords: list[dict[str, Any]]) -> list[str]:
        """Extract technology-related keywords from metadata keywords."""
        tech_keywords = []
        tech_terms = [
            "engine", "dx", "directx", "opengl", "vulkan", "unreal", "unity",
            "frostbite", "cryengine", "source", "id tech", "havok", "physics",
            "netcode", "servers", "dedicated", "peer-to-peer", "matchmaking"
        ]
        
        for keyword in keywords:
            keyword_name = keyword.get("name", "").lower()
            if any(tech_term in keyword_name for tech_term in tech_terms):
                tech_keywords.append(keyword.get("name", keyword_name))
                
        return tech_keywords[:15]  # Limit to 15 most relevant

    def _extract_multiplayer_features(self, multiplayer_modes: list[dict[str, Any]]) -> list[str]:
        """Extract multiplayer technology features."""
        features = []
        for mode in multiplayer_modes:
            mode_name = mode.get("name", "").lower()
            if "online" in mode_name:
                features.append("Online Multiplayer")
            elif "offline" in mode_name:
                features.append("Offline Multiplayer")
            elif "co-op" in mode_name:
                features.append("Co-op")
            elif "split" in mode_name:
                features.append("Split Screen")
            elif "lan" in mode_name:
                features.append("LAN Support")
                
        return list(set(features))

    def _extract_file_size(self, data: dict[str, Any]) -> str:
        """Extract file size information from RAWG data."""
        # RAWG may have file size in different fields - this is a basic extraction
        size_fields = ["file_size", "size", "disk_space"]
        for field in size_fields:
            if field in data and data[field]:
                return str(data[field])
        return ""

    def _extract_system_specs(self, requirements: str) -> dict[str, Any]:
        """Extract system specs from requirements string."""
        specs = {"file_size_mb": 0, "memory_gb": 0, "storage_gb": 0}
        
        requirements_lower = requirements.lower()
        
        # Extract memory requirement
        import re
        memory_match = re.search(r'(\d+)\s*gb', requirements_lower)
        if memory_match:
            specs["memory_gb"] = int(memory_match.group(1))
            
        # Extract storage requirement
        storage_match = re.search(r'(\d+)\s*gb', requirements_lower)
        if storage_match:
            specs["storage_gb"] = int(storage_match.group(1))
            
        # Extract file size (if mentioned)
        size_match = re.search(r'(\d+)\s*mb', requirements_lower)
        if size_match:
            specs["file_size_mb"] = int(size_match.group(1))
            
        return specs

    def _build_engine_query(self, game_name: str, game_engine: str) -> str:
        """Build engine performance search query."""
        engine_part = f" {game_engine}" if game_engine else ""
        return f'"{game_name}"{engine_part} game engine performance optimizationfps lag bugs'

    def _build_tech_analysis_query(self, game_name: str, platforms: list[str]) -> str:
        """Build technical analysis search query."""
        platform_part = f" {' '.join(platforms[:2])}" if platforms else ""
        return f'"{game_name}" technical analysis performance issues{platform_part}'

    def _build_performance_query(self, game_name: str) -> str:
        """Build performance issues search query."""
        return f'"{game_name}" performance problems bugs stuttering crashes optimization'

    def _build_network_query(self, game_name: str) -> str:
        """Build network/online performance search query."""
        return f'"{game_name}" online network performance multiplayer lag connectivity'

    def _build_dev_tech_query(self, game_name: str, game_engine: str) -> str:
        """Build developer technical interview search query."""
        engine_part = f" {game_engine}" if game_engine else ""
        return f'"{game_name}" developer interview technical challenges solution{engine_part}'

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
        elif "gamasutra.com" in url_lower or "gamesindustry.biz" in url_lower:
            return "industry"
        elif "github" in url_lower:
            return "technical"
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
        # Critical fields for technical analysis
        critical_fields = ["game_engine", "system_requirements", "platforms"]
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
        
        if hard_data.get("system_requirements", {}).get("minimum"):
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
