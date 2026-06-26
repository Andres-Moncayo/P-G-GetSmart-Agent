from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from ....core.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Async client for Gemini structured JSON generation and text synthesis with graceful fallback."""

    BASE_URL_TEMPLATE = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "{model}:generateContent?key={api_key}"
    )

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_key = api_key or settings.gemini_api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        
        # Flag to check if API key is available
        self.has_api_key = bool(self.api_key)

    async def generate_structured_json(
        self,
        *,
        system_instruction: str,
        user_prompt: str,
        response_schema: dict[str, Any] | None = None,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """Generate structured JSON response from Gemini.
        
        Returns mock analysis if API key is not configured.
        """
        if not self.has_api_key:
            logger.warning("Gemini API key not configured, returning mock structured analysis")
            return self._mock_structured_response(user_prompt)

        try:
            url = self.BASE_URL_TEMPLATE.format(model=self.model, api_key=self.api_key)

            generation_config: dict[str, Any] = {
                "temperature": temperature,
                "responseMimeType": "application/json",
            }
            if response_schema is not None:
                generation_config["responseSchema"] = response_schema

            payload: dict[str, Any] = {
                "system_instruction": {
                    "parts": [{"text": system_instruction}],
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": user_prompt}],
                    }
                ],
                "generationConfig": generation_config,
            }

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                raw_response = response.json()

            text_output = self._extract_text_from_response(raw_response)
            return self._parse_json_robust(text_output)
        except Exception as e:
            logger.warning("Gemini API call failed: %s", e)
            return self._mock_structured_response(user_prompt, error=str(e))

    async def generate_text(
        self,
        *,
        system_instruction: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        """Generate text response from Gemini.
        
        Returns mock synthesis if API key is not configured.
        """
        if not self.has_api_key:
            logger.warning("Gemini API key not configured, returning mock text synthesis")
            return self._mock_text_response(user_prompt)

        try:
            url = self.BASE_URL_TEMPLATE.format(model=self.model, api_key=self.api_key)

            payload: dict[str, Any] = {
                "system_instruction": {
                    "parts": [{"text": system_instruction}],
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": user_prompt}],
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "responseMimeType": "text/plain",
                },
            }

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                raw_response = response.json()

            return self._extract_text_from_response(raw_response)
        except Exception as e:
            logger.warning("Gemini API call failed: %s", e)
            return self._mock_text_response(user_prompt, error=str(e))

    def _extract_text_from_response(self, payload: dict[str, Any]) -> str:
        candidates = payload.get("candidates", [])
        if not candidates:
            raise ValueError("Gemini response has no candidates")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise ValueError("Gemini response candidate has no parts")

        text = parts[0].get("text")
        if not text or not isinstance(text, str):
            raise ValueError("Gemini response part has no text")

        return text.strip()

    def _parse_json_robust(self, output_text: str) -> dict[str, Any]:
        try:
            parsed = json.loads(output_text)
            if not isinstance(parsed, dict):
                raise ValueError("Gemini JSON output must be an object")
            return parsed
        except json.JSONDecodeError:
            pass

        fenced_match = re.search(r"```json\s*(\{.*\})\s*```", output_text, re.DOTALL)
        if fenced_match:
            try:
                parsed = json.loads(fenced_match.group(1))
                if not isinstance(parsed, dict):
                    raise ValueError("Gemini fenced JSON output must be an object")
                return parsed
            except json.JSONDecodeError as exception:
                raise ValueError("Gemini returned invalid fenced JSON") from exception

        brace_match = re.search(r"(\{.*\})", output_text, re.DOTALL)
        if brace_match:
            try:
                parsed = json.loads(brace_match.group(1))
                if not isinstance(parsed, dict):
                    raise ValueError("Gemini extracted JSON output must be an object")
                return parsed
            except json.JSONDecodeError as exception:
                raise ValueError("Gemini returned non-parseable JSON") from exception

        raise ValueError("Gemini output does not contain valid JSON")

    def _mock_structured_response(self, user_prompt: str, error: str | None = None) -> dict[str, Any]:
        """Return mock structured analysis when API is not available."""
        if error:
            logger.warning("Gemini API error, returning mock structured analysis: %s", error)
        
        # Extract game name from prompt for more realistic mock
        game_name = "Unknown Game"
        if "game" in user_prompt.lower():
            # Try to extract game name from prompt
            match = re.search(r'game[:\s]+([^,\n.]+)', user_prompt, re.IGNORECASE)
            if match:
                game_name = match.group(1).strip()
        
        return {
            "analysis_summary": f"Mock analysis for {game_name}",
            "key_insights": [
                "Mock insight 1: Game demonstrates typical design patterns",
                "Mock insight 2: Audience reception appears mixed",
                "Mock insight 3: Technical implementation is conventional"
            ],
            "strengths": ["Design clarity", "Target audience focus"],
            "weaknesses": ["Limited innovation", "Technical constraints"],
            "opportunities": ["Market expansion", "Feature enhancement"],
            "threats": ["Competitive pressure", "Market saturation"],
            "confidence_score": 0.5,
            "analysis_type": "mock",
            "generated_at": "2025-01-01T00:00:00Z",
            "error": error
        }

    def _mock_text_response(self, user_prompt: str, error: str | None = None) -> str:
        """Return mock text synthesis when API is not available."""
        if error:
            logger.warning("Gemini API error, returning mock text synthesis: %s", error)
        
        # Extract game name from prompt for more realistic mock
        game_name = "Unknown Game"
        if "game" in user_prompt.lower():
            # Try to extract game name from prompt
            match = re.search(r'[:\s]+([A-Z][a-zA-Z\s]+)', user_prompt)
            if match:
                game_name = match.group(1).strip()
        
        return f"""# Mock Game Analysis Report

## Overview
This is a mock analysis report for **{game_name}** generated because the Gemini API key is not configured or the API call failed.

## Key Findings

### Design & Art
- The game demonstrates conventional design patterns
- Visual presentation appears to follow industry standards
- Art direction shows moderate innovation

### Technical Systems
- Implementation follows established technical practices
- Performance characteristics appear typical for the genre
- System architecture demonstrates functional competence

### User Experience
- Player engagement mechanics follow familiar paradigms
- Interface design maintains reasonable usability standards
- Overall player experience meets baseline expectations

### Strategy & Market
- Market positioning follows conventional approaches
- Competitive landscape presents standard challenges
- Business model demonstrates typical monetization strategies

## Recommendations
1. **Enhance Innovation**: Consider introducing more innovative gameplay mechanics
2. **Technical Optimization**: Focus on performance improvements and bug fixes
3. **Market Expansion**: Explore new market segments and distribution channels
4. **Community Building**: Develop stronger community engagement strategies

## Limitations
*This analysis was generated without access to the Gemini AI API due to missing API credentials. For comprehensive game intelligence analysis, please configure the GEMINI_API_KEY in your environment variables.*

*Error details: {error if error else "API key not configured"}*"""