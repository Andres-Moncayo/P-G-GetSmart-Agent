"""
Base class for all macro-skills used in the AI game intelligence system.

This module defines the abstract interface that all macro-skills must implement,
providing common functionality for:
- Model initialization and configuration
- Caching of results
- Error handling and retries
- Abstract methods for skill-specific logic
"""

import abc
import hashlib
import json
import logging
from typing import Any

try:
    import google.genai as genai
    from google.genai.types import HarmCategory, HarmBlockThreshold
    if not hasattr(genai, "configure") or not hasattr(genai, "GenerativeModel"):
        raise ImportError("google.genai does not expose required Gemini APIs")
except ImportError:
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
    except ImportError as exc:
        genai = None
        HarmCategory = None
        HarmBlockThreshold = None

from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_exponential

from ...core.config import settings
from ...tasks.cache_manager import CacheManager
from ..scraper.infrastructure.llm_client import GeminiClient

logger = logging.getLogger(__name__)


class BaseMacroSkill(abc.ABC):
    """Abstract base class for all macro-skills in the AI game intelligence system."""

    # Class configuration - override in subclasses
    skill_id: str
    skill_name: str
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.3
    max_output_tokens: int = 6000
    cache_ttl: int = 86400  # 24h — matches ux_skill.yaml caching config

    def __init__(self) -> None:
        self._model = None
        self._http_client = None

        if settings.gemini_api_key:
            if genai is not None:
                try:
                    if hasattr(genai, "configure"):
                        genai.configure(api_key=settings.gemini_api_key)

                    self._model = genai.GenerativeModel(
                        model_name=self.model_name,
                        system_instruction=self.system_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=self.temperature,
                            max_output_tokens=self.max_output_tokens,
                            response_mime_type="application/json",
                        ),
                        safety_settings={
                            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        }
                    )
                except Exception as exc:
                    logger.warning(
                        "Gemini SDK initialization failed; falling back to HTTP client: %s",
                        exc,
                    )
                    self._model = None
            if self._model is None:
                self._http_client = GeminiClient(api_key=settings.gemini_api_key)
        else:
            logger.warning("GEMINI_API_KEY is not configured for BaseMacroSkill")
            self._http_client = GeminiClient()

    # ------------------------------------------------------------------
    # Abstract interface — subclasses must implement these
    # ------------------------------------------------------------------

    @property
    @abc.abstractmethod
    def system_prompt(self) -> str: ...

    @abc.abstractmethod
    def build_user_prompt(self, mini_context: dict) -> str: ...

    @abc.abstractmethod
    def _fallback_output(self, game_id: str, game_name: str) -> dict: ...

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _cache_key(self, game_id: str, input_hash: str) -> str:
        return f"skill:{self.skill_id}:{game_id}:{input_hash}"

    @staticmethod
    def _input_hash(mini_context: dict) -> str:
        serialized = json.dumps(mini_context, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    # ------------------------------------------------------------------
    # Model call with exponential retry
    # ------------------------------------------------------------------

    async def _call_model(self, prompt: str) -> dict[str, Any]:
        """Call Gemini via SDK when available, else use the HTTP client fallback."""
        if self._model is not None:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=1, max=30),
                reraise=True,
            ):
                with attempt:
                    response = self._model.generate_content(prompt)
                    return json.loads(response.text)

        if self._http_client is not None:
            return await self._http_client.generate_structured_json(
                system_instruction=self.system_prompt,
                user_prompt=prompt,
            )

        raise RuntimeError("No Gemini model or HTTP client available for BaseMacroSkill")

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    async def analyze(self, mini_context: dict) -> dict[str, Any]:
        """
        Run the full analysis pipeline:
        1. Check cache
        2. Build prompt and call model
        3. Store result and return
        Falls back to a minimal error-flagged response on failure.
        """
        game_id = mini_context.get("metadata", {}).get("game_id", "unknown")
        game_name = mini_context.get("metadata", {}).get("game_name", "")
        cache_key = self._cache_key(game_id, self._input_hash(mini_context))

        cached = await CacheManager.get(cache_key)
        if cached:
            logger.info("Cache hit: %s:%s", self.skill_id, game_id)
            return cached

        prompt = self.build_user_prompt(mini_context)

        try:
            result = await self._call_model(prompt)
        except (RetryError, Exception) as exc:
            logger.error("%s analysis failed for %s: %s", self.skill_id, game_id, exc)
            return self._fallback_output(game_id, game_name)

        try:
            await CacheManager.set(cache_key, result, expire=self.cache_ttl)
        except Exception as exc:
            logger.warning("Cache set failed for %s:%s: %s", self.skill_id, game_id, exc)

        logger.info("Analysis complete: %s:%s", self.skill_id, game_id)
        return result