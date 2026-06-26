from __future__ import annotations

import json
from typing import Any

from backend.app.scraper.infrastructure.llm_client import GeminiClient


SYNTHESIZER_SYSTEM_INSTRUCTION = """
You are a senior game analysis synthesis assistant for GetSmart.
Generate ONLY Markdown (no JSON, no code fences unless needed inside Markdown examples).
Use concise headings, bullet points, and evidence-oriented language.
""".strip()


def _build_markdown_synthesis_prompt(master_json: dict[str, Any]) -> str:
    return (
        "Create the final report in Markdown from this Master-JSON.\n"
        "Requirements:\n"
        "1) Include sections: Executive Summary, Design & Art, User Experience, "
        "Technology & Systems, Strategy & Market, Risks, Opportunities, Final Verdict.\n"
        "2) Keep the analysis grounded in available evidence.\n"
        "3) If evidence is missing, explicitly state assumptions and uncertainty.\n"
        "4) Use tables where useful for comparative clarity.\n"
        "5) Keep output valid Markdown only.\n\n"
        "Master-JSON input:\n"
        f"{json.dumps(master_json, ensure_ascii=False)}"
    )


async def synthesize_markdown_report(
    master_json: dict[str, Any],
    gemini_client: GeminiClient | None = None,
) -> str:
    """
    Phase 4: Takes Master-JSON from Phase 3 and generates final Markdown report
    using Gemini-2.5-pro.
    """
    client = gemini_client or GeminiClient(model="gemini-2.5-pro")

    prompt = _build_markdown_synthesis_prompt(master_json)
    markdown_result = await client.generate_text(
        system_instruction=SYNTHESIZER_SYSTEM_INSTRUCTION,
        user_prompt=prompt,
        temperature=0.3,
    )

    return markdown_result.strip()
