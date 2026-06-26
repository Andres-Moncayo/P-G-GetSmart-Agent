from __future__ import annotations

import json
import re
from typing import Any, Dict

from app.core.config import GEMINI_API_KEY, SYNTHESIS_MODEL
from app.models.synthesis.synthesis_models import FinalReport
from app.services.macro_skills.synthesis_Skill.prompt_loader import PromptLoader


class GeminiSynthesizer:
    def __init__(self, prompt_loader: PromptLoader | None = None) -> None:
        self.prompt_loader = prompt_loader or PromptLoader()

    @property
    def is_available(self) -> bool:
        return bool(GEMINI_API_KEY)

    def synthesize(self, user_prompt: str) -> FinalReport:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise RuntimeError("google-generativeai package is required for Gemini synthesis") from exc

        model_config = self.prompt_loader.get_model_config()
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=model_config.get("name", SYNTHESIS_MODEL),
            system_instruction=self.prompt_loader.get_system_prompt(),
        )

        response = model.generate_content(
            user_prompt,
            generation_config={
                "temperature": model_config.get("temperature", 0.2),
                "max_output_tokens": model_config.get("max_output_tokens", 16000),
                "top_p": model_config.get("top_p", 0.95),
                "top_k": model_config.get("top_k", 40),
                "response_mime_type": "application/json",
            },
        )

        raw_text = response.text or ""
        payload = self._parse_json(raw_text)
        return FinalReport.model_validate(payload)

    @staticmethod
    def _parse_json(raw_text: str) -> Dict[str, Any]:
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return json.loads(cleaned)
