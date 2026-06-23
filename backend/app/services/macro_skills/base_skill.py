"""
Abstract base class for all GetSmart Macro-Skills.

Each of the 4 Macro-Skills (Design & Art, UX, Technology & Systems,
Strategy & Market) extends this class and implements:
  - system_prompt  — the LLM persona and output schema instructions
  - build_user_prompt  — formats the mini_context dict into a model prompt
  - _fallback_output   — safe minimal response when analysis fails
"""

from __future__ import annotations

import abc
import hashlib
import json
import logging
from typing import Any

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from tenacity import AsyncRetrying, RetryError, stop_after_attempt, wait_exponential

from ...core.config import GEMINI_API_KEY
from ...tasks.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class BaseMacroSkill(abc.ABC):
    skill_id: str
    skill_name: str
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.3
    max_output_tokens: int = 6000
    cache_ttl: int = 86400  # 24h — matches ux_skill.yaml caching config

    def __init__(self) -> None:
        genai.configure(api_key=GEMINI_API_KEY)
        self._model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
                response_mime_type="application/json",  # forces structured JSON output
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

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
        """Call Gemini with up to 3 retries and exponential backoff."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=30),
            reraise=True,
        ):
            with attempt:
                response = self._model.generate_content(prompt)
                return json.loads(response.text)

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