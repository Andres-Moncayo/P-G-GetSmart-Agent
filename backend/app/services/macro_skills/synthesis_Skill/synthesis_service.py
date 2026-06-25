from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.models.synthesis.synthesis_models import FinalReport, SynthesisInput, SynthesisResponse
from app.services.macro_skills.synthesis.deterministic_synthesizer import DeterministicSynthesizer
from app.services.macro_skills.synthesis.format_generators import FormatGenerator
from app.services.macro_skills.synthesis.gemini_client import GeminiSynthesizer
from app.services.macro_skills.synthesis.prompt_loader import PromptLoader


class ReportStore:
    """In-memory report cache for API retrieval."""

    def __init__(self) -> None:
        self._reports: Dict[str, SynthesisResponse] = {}

    def save(self, response: SynthesisResponse) -> str:
        report_id = response.report.metadata.report_id
        self._reports[report_id] = response
        return report_id

    def get(self, report_id: str) -> Optional[SynthesisResponse]:
        return self._reports.get(report_id)


report_store = ReportStore()


class SynthesisService:
    def __init__(self) -> None:
        self.prompt_loader = PromptLoader()
        self.deterministic = DeterministicSynthesizer()
        self.gemini = GeminiSynthesizer(self.prompt_loader)
        self.format_generator = FormatGenerator()

    def _build_prompt_context(self, synthesis_input: SynthesisInput) -> Dict[str, Any]:
        metadata = synthesis_input.metadata or {}
        master_json = synthesis_input.master_json
        macro_outputs = synthesis_input.macro_outputs.model_dump()

        hard_data = master_json.get("hard_data", {})
        hard_data_keys = list(hard_data.keys()) if isinstance(hard_data, dict) else []

        return {
            "game_name": metadata.get("game_name") or master_json.get("metadata", {}).get("game_name", "Unknown Game"),
            "game_id": metadata.get("game_id") or master_json.get("metadata", {}).get("game_id", str(uuid.uuid4())),
            "pipeline_version": metadata.get("pipeline_version", "3.0.0"),
            "synthesis_job_id": metadata.get("synthesis_job_id", f"syn-{uuid.uuid4()}"),
            "macro_skills_completed": metadata.get(
                "macro_skills_completed",
                ["design_art", "user_experience", "technology_systems", "strategy_market"],
            ),
            "master_json": master_json,
            "master_json.evidence_count": master_json.get("evidence_count", 0),
            "master_json.confidence_score": master_json.get("confidence_score", 0.0),
            "master_json.hard_data_keys": ", ".join(hard_data_keys),
            "macro_outputs": macro_outputs,
        }

    def synthesize(self, synthesis_input: SynthesisInput, force_deterministic: bool = False) -> SynthesisResponse:
        workflow_steps: List[str]
        synthesis_mode: str

        if self.gemini.is_available and not force_deterministic:
            user_prompt = self.prompt_loader.render_user_prompt(self._build_prompt_context(synthesis_input))
            report = self.gemini.synthesize(user_prompt)
            workflow_steps = self.prompt_loader.get_workflow_steps()
            synthesis_mode = "gemini"
        else:
            report, workflow_steps = self.deterministic.synthesize(synthesis_input)
            synthesis_mode = "deterministic"

        markdown = self.format_generator.to_markdown(report)
        pdf_html = self.format_generator.to_pdf_html(report)

        response = SynthesisResponse(
            report=report,
            markdown=markdown,
            pdf_html=pdf_html,
            synthesis_mode=synthesis_mode,
            workflow_steps_completed=workflow_steps,
        )
        report_store.save(response)
        return response

    def get_report(self, report_id: str) -> Optional[SynthesisResponse]:
        return report_store.get(report_id)
