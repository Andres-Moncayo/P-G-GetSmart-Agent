from __future__ import annotations

import asyncio
import json
from typing import Any

from ..infrastructure.llm_client import GeminiClient


STRICT_SYSTEM_INSTRUCTION = """
You are a strict JSON generator for GetSmart pipeline.
Return ONLY one valid JSON object.
Do not include markdown fences.
Do not include explanations.
Follow the requested schema and keep unknown fields out.
""".strip()


def _build_prompt(macro_skill: str, mini_context: dict[str, Any]) -> str:
    return (
        f"Analyze the Mini-Context for macro-skill '{macro_skill}'.\n"
        "Produce a structured JSON output with keys:\n"
        "- macro_skill (string)\n"
        "- confidence_score (number 0..1)\n"
        "- key_findings (array of short strings, max 10)\n"
        "- strengths (array of short strings, max 10)\n"
        "- weaknesses (array of short strings, max 10)\n"
        "- risks (array of short strings, max 10)\n"
        "- opportunities (array of short strings, max 10)\n"
        "- evidence_count (integer >= 0)\n"
        "- summary (string, max 1200 chars)\n\n"
        "Mini-Context JSON:\n"
        f"{json.dumps(mini_context, ensure_ascii=False)}"
    )


def _analysis_response_schema() -> dict[str, Any]:
    return {
        "type": "OBJECT",
        "required": [
            "macro_skill",
            "confidence_score",
            "key_findings",
            "strengths",
            "weaknesses",
            "risks",
            "opportunities",
            "evidence_count",
            "summary",
        ],
        "properties": {
            "macro_skill": {"type": "STRING"},
            "confidence_score": {"type": "NUMBER"},
            "key_findings": {"type": "ARRAY", "items": {"type": "STRING"}},
            "strengths": {"type": "ARRAY", "items": {"type": "STRING"}},
            "weaknesses": {"type": "ARRAY", "items": {"type": "STRING"}},
            "risks": {"type": "ARRAY", "items": {"type": "STRING"}},
            "opportunities": {"type": "ARRAY", "items": {"type": "STRING"}},
            "evidence_count": {"type": "INTEGER"},
            "summary": {"type": "STRING"},
        },
    }


def _validate_analysis_output(output: dict[str, Any], macro_skill: str) -> dict[str, Any]:
    required_keys = {
        "macro_skill",
        "confidence_score",
        "key_findings",
        "strengths",
        "weaknesses",
        "risks",
        "opportunities",
        "evidence_count",
        "summary",
    }

    missing_keys = required_keys - set(output.keys())
    if missing_keys:
        raise ValueError(f"Missing required keys in analysis output: {sorted(missing_keys)}")

    output_macro_skill = output.get("macro_skill")
    if not isinstance(output_macro_skill, str):
        raise ValueError("macro_skill must be a string")

    confidence_score = output.get("confidence_score")
    if not isinstance(confidence_score, (int, float)):
        raise ValueError("confidence_score must be numeric")
    if confidence_score < 0 or confidence_score > 1:
        raise ValueError("confidence_score must be between 0 and 1")

    evidence_count = output.get("evidence_count")
    if not isinstance(evidence_count, int) or evidence_count < 0:
        raise ValueError("evidence_count must be an integer >= 0")

    array_fields = ["key_findings", "strengths", "weaknesses", "risks", "opportunities"]
    for field_name in array_fields:
        field_value = output.get(field_name)
        if not isinstance(field_value, list):
            raise ValueError(f"{field_name} must be an array")
        if not all(isinstance(item, str) for item in field_value):
            raise ValueError(f"{field_name} must contain only strings")

    summary = output.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("summary must be a non-empty string")

    output["macro_skill"] = macro_skill
    output["confidence_score"] = float(confidence_score)
    return output


async def analyze_design_art(mini_context: dict[str, Any], gemini_client: GeminiClient) -> dict[str, Any]:
    macro_skill = "design_art"
    prompt = _build_prompt(macro_skill=macro_skill, mini_context=mini_context)
    output = await gemini_client.generate_structured_json(
        system_instruction=STRICT_SYSTEM_INSTRUCTION,
        user_prompt=prompt,
        response_schema=_analysis_response_schema(),
    )
    return _validate_analysis_output(output=output, macro_skill=macro_skill)


async def analyze_user_experience(mini_context: dict[str, Any], gemini_client: GeminiClient) -> dict[str, Any]:
    macro_skill = "user_experience"
    prompt = _build_prompt(macro_skill=macro_skill, mini_context=mini_context)
    output = await gemini_client.generate_structured_json(
        system_instruction=STRICT_SYSTEM_INSTRUCTION,
        user_prompt=prompt,
        response_schema=_analysis_response_schema(),
    )
    return _validate_analysis_output(output=output, macro_skill=macro_skill)


async def analyze_technology_systems(mini_context: dict[str, Any], gemini_client: GeminiClient) -> dict[str, Any]:
    macro_skill = "technology_systems"
    prompt = _build_prompt(macro_skill=macro_skill, mini_context=mini_context)
    output = await gemini_client.generate_structured_json(
        system_instruction=STRICT_SYSTEM_INSTRUCTION,
        user_prompt=prompt,
        response_schema=_analysis_response_schema(),
    )
    return _validate_analysis_output(output=output, macro_skill=macro_skill)


async def analyze_strategy_market(mini_context: dict[str, Any], gemini_client: GeminiClient) -> dict[str, Any]:
    macro_skill = "strategy_market"
    prompt = _build_prompt(macro_skill=macro_skill, mini_context=mini_context)
    output = await gemini_client.generate_structured_json(
        system_instruction=STRICT_SYSTEM_INSTRUCTION,
        user_prompt=prompt,
        response_schema=_analysis_response_schema(),
    )
    return _validate_analysis_output(output=output, macro_skill=macro_skill)


async def run_parallel_ai_workers(
    *,
    design_art_context: dict[str, Any],
    user_experience_context: dict[str, Any],
    technology_systems_context: dict[str, Any],
    strategy_market_context: dict[str, Any],
    gemini_client: GeminiClient | None = None,
) -> dict[str, Any]:
    """Runs the 4 Phase-2 AI workers in parallel with asyncio.gather()."""
    client = gemini_client or GeminiClient()

    results = await asyncio.gather(
        analyze_design_art(design_art_context, client),
        analyze_user_experience(user_experience_context, client),
        analyze_technology_systems(technology_systems_context, client),
        analyze_strategy_market(strategy_market_context, client),
        return_exceptions=True,
    )

    worker_names = [
        "design_art",
        "user_experience",
        "technology_systems",
        "strategy_market",
    ]

    completed_workers: list[str] = []
    failed_workers: list[str] = []
    analyses: dict[str, Any] = {}

    for worker_name, result in zip(worker_names, results):
        if isinstance(result, Exception):
            failed_workers.append(worker_name)
            analyses[worker_name] = {"status": "failed", "error": str(result)}
            continue

        completed_workers.append(worker_name)
        analyses[worker_name] = {"status": "completed", "analysis": result}

    return {
        "completed_workers": completed_workers,
        "failed_workers": failed_workers,
        "analyses": analyses,
    }
