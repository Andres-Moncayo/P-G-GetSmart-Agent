from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import PIPELINE_VERSION, SYNTHESIS_MODEL
from app.models.synthesis.synthesis_models import (
    CATEGORY_NAMES,
    CATEGORY_OWNERSHIP,
    Appendices,
    CategoryId,
    ConfidenceBreakdown,
    ConfidenceMetrics,
    CrossCuttingInsight,
    CrossCuttingInsights,
    ExecutiveSummary,
    FinalReport,
    MacroOutputs,
    ReportMetadata,
    RiskItem,
    SkillId,
    SourceIndexEntry,
    StrategicRecommendation,
    SupportingEvidence,
    SynthesisInput,
    ThematicAnalysis,
    ThematicCategory,
)

SKILL_KEYS: List[SkillId] = [
    "design_art",
    "user_experience",
    "technology_systems",
    "strategy_market",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is None:
            return default
    return current


def _skill_overall_confidence(skill_output: Dict[str, Any]) -> float:
    return float(_safe_get(skill_output, "confidence", "overall_score", default=0.0) or 0.0)


def _category_confidence(skill_output: Dict[str, Any], category_id: str) -> Optional[float]:
    score = _safe_get(skill_output, "confidence", "category_scores", category_id)
    if score is None:
        return None
    return float(score)


def _extract_sources(skill_output: Dict[str, Any], category_id: str) -> List[Dict[str, Any]]:
    analysis = _safe_get(skill_output, "analysis", category_id, default={})
    if not isinstance(analysis, dict):
        return []
    sources = analysis.get("sources_cited", [])
    return sources if isinstance(sources, list) else []


def _extract_overview(skill_output: Dict[str, Any], category_id: str) -> str:
    analysis = _safe_get(skill_output, "analysis", category_id, default={})
    if isinstance(analysis, dict) and analysis.get("overview"):
        return str(analysis["overview"])
    summary = skill_output.get("summary", {})
    if isinstance(summary, dict):
        for key in ("design_philosophy", "ux_philosophy", "technical_posture", "market_position"):
            if summary.get(key):
                return str(summary[key])
    return f"Insufficient analysis available for {category_id}."


def _extract_key_findings(skill_output: Dict[str, Any], category_id: str) -> List[str]:
    analysis = _safe_get(skill_output, "analysis", category_id, default={})
    findings: List[str] = []
    if not isinstance(analysis, dict):
        return findings

    for field in ("key_findings", "key_mechanics", "strengths", "weaknesses"):
        value = analysis.get(field)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    findings.append(item)
                elif isinstance(item, dict):
                    label = item.get("mechanic_name") or item.get("title") or item.get("name")
                    desc = item.get("description") or item.get("detail") or ""
                    if label:
                        findings.append(f"{label}: {desc}".strip(": "))

    feedback = analysis.get("player_feedback", {})
    if isinstance(feedback, dict):
        for key in ("strengths", "weaknesses"):
            for item in feedback.get(key, []) or []:
                if isinstance(item, str):
                    findings.append(item)

    return findings[:5]


def _build_supporting_evidence(
    macro_outputs: MacroOutputs,
    category_id: CategoryId,
) -> List[SupportingEvidence]:
    ownership = CATEGORY_OWNERSHIP[category_id]
    skills_to_check = [ownership["primary"], *ownership.get("cross_refs", [])]
    evidence: List[SupportingEvidence] = []

    for skill_id in skills_to_check:
        skill_output = getattr(macro_outputs, skill_id)
        sources = _extract_sources(skill_output, category_id)
        for source in sources:
            if not isinstance(source, dict):
                continue
            claim = (
                source.get("claim")
                or source.get("snippet")
                or source.get("title")
                or _extract_overview(skill_output, category_id)
            )
            urls = source.get("urls") or source.get("url")
            if isinstance(urls, str):
                urls = [urls]
            if not isinstance(urls, list):
                urls = []
            confidence = float(source.get("confidence", _category_confidence(skill_output, category_id) or 0.5))
            evidence.append(
                SupportingEvidence(
                    source=skill_id,
                    claim=str(claim),
                    confidence=min(confidence, 1.0),
                    urls=[str(url) for url in urls if url],
                )
            )

    if not evidence:
        primary_output = getattr(macro_outputs, ownership["primary"])
        overview = _extract_overview(primary_output, category_id)
        evidence.append(
            SupportingEvidence(
                source=ownership["primary"],
                claim=overview,
                confidence=_category_confidence(primary_output, category_id) or _skill_overall_confidence(primary_output),
                urls=[],
            )
        )
    return evidence[:8]


def _compute_category_confidence(
    macro_outputs: MacroOutputs,
    category_id: CategoryId,
) -> float:
    ownership = CATEGORY_OWNERSHIP[category_id]
    primary_skill = ownership["primary"]
    cross_refs = ownership.get("cross_refs", [])

    primary_output = getattr(macro_outputs, primary_skill)
    primary_score = _category_confidence(primary_output, category_id)
    if primary_score is None:
        primary_score = _skill_overall_confidence(primary_output)

    cross_scores: List[float] = []
    for skill_id in cross_refs:
        cross_output = getattr(macro_outputs, skill_id)
        score = _category_confidence(cross_output, category_id)
        if score is not None:
            cross_scores.append(score)

    if cross_scores:
        cross_avg = sum(cross_scores) / len(cross_scores)
        weighted = (primary_score * 0.6) + (cross_avg * 0.4)
    else:
        weighted = primary_score

    contributors = [primary_score, *cross_scores]
    return min(weighted, max(contributors) if contributors else weighted)


def _build_thematic_category(
    macro_outputs: MacroOutputs,
    category_id: CategoryId,
) -> ThematicCategory:
    ownership = CATEGORY_OWNERSHIP[category_id]
    primary_skill = ownership["primary"]
    primary_output = getattr(macro_outputs, primary_skill)

    overview = _extract_overview(primary_output, category_id)
    key_findings = _extract_key_findings(primary_output, category_id)

    for skill_id in ownership.get("cross_refs", []):
        cross_output = getattr(macro_outputs, skill_id)
        key_findings.extend(_extract_key_findings(cross_output, category_id))

    unique_findings: List[str] = []
    for finding in key_findings:
        if finding not in unique_findings:
            unique_findings.append(finding)

    cross_skill_notes = [
        f"Primary analysis sourced from {primary_skill.replace('_', ' ')}.",
    ]
    if ownership.get("cross_refs"):
        cross_skill_notes.append(
            f"Cross-referenced with {', '.join(skill.replace('_', ' ') for skill in ownership['cross_refs'])}."
        )

    return ThematicCategory(
        category_id=category_id,
        category_name=CATEGORY_NAMES[category_id],
        overview=overview,
        key_findings=unique_findings[:5] or [overview],
        supporting_evidence=_build_supporting_evidence(macro_outputs, category_id),
        confidence=_compute_category_confidence(macro_outputs, category_id),
        cross_skill_notes=cross_skill_notes,
    )


def _build_source_index(macro_outputs: MacroOutputs) -> List[SourceIndexEntry]:
    index: Dict[str, SourceIndexEntry] = {}
    for skill_id in SKILL_KEYS:
        skill_output = getattr(macro_outputs, skill_id)
        analysis = skill_output.get("analysis", {})
        if not isinstance(analysis, dict):
            continue
        for category_data in analysis.values():
            if not isinstance(category_data, dict):
                continue
            for source in category_data.get("sources_cited", []) or []:
                if not isinstance(source, dict):
                    continue
                url = source.get("url") or (source.get("urls") or [None])[0]
                if not url:
                    continue
                platform = str(source.get("platform", "unknown"))
                if url in index:
                    index[url].citation_count += 1
                else:
                    index[url] = SourceIndexEntry(
                        url=str(url),
                        platform=platform,
                        first_cited_by=skill_id,
                        citation_count=1,
                    )
    return list(index.values())


def _classify_report(skill_confidences: List[float], present_skills: int) -> str:
    if present_skills < 2:
        return "error"
    if present_skills < 4:
        return "partial"
    high_confidence = sum(1 for score in skill_confidences if score >= 0.5)
    if high_confidence < 2:
        return "low_confidence"
    return "comprehensive"


class DeterministicSynthesizer:
    """Rule-based synthesizer used when Gemini is unavailable or for deterministic demos."""

    WORKFLOW_STEPS = [
        "validate_inputs",
        "extract_and_index",
        "resolve_conflicts",
        "unify_thematic",
        "generate_cross_cutting",
        "draft_recommendations_risks",
        "finalize_report",
    ]

    def synthesize(self, synthesis_input: SynthesisInput) -> Tuple[FinalReport, List[str]]:
        macro_outputs = synthesis_input.macro_outputs
        master_json = synthesis_input.master_json
        metadata_in = synthesis_input.metadata or {}

        skill_outputs = {
            "design_art": macro_outputs.design_art,
            "user_experience": macro_outputs.user_experience,
            "technology_systems": macro_outputs.technology_systems,
            "strategy_market": macro_outputs.strategy_market,
        }

        present_skills = [skill for skill, output in skill_outputs.items() if output]
        skill_confidences = [_skill_overall_confidence(skill_outputs[skill]) for skill in present_skills]

        game_name = (
            metadata_in.get("game_name")
            or _safe_get(master_json, "metadata", "game_name")
            or "Unknown Game"
        )
        game_id = (
            metadata_in.get("game_id")
            or _safe_get(master_json, "metadata", "game_id")
            or str(uuid.uuid4())
        )

        thematic_categories = {
            category_id: _build_thematic_category(macro_outputs, category_id)
            for category_id in CATEGORY_NAMES
        }
        category_scores = {
            category_id: thematic_categories[category_id].confidence
            for category_id in CATEGORY_NAMES
        }
        overall_score = sum(category_scores.values()) / len(category_scores)

        summaries = []
        for skill_id in present_skills:
            summary = skill_outputs[skill_id].get("summary", {})
            if isinstance(summary, dict):
                for value in summary.values():
                    if isinstance(value, str) and value:
                        summaries.append(value)

        key_insights = []
        for category in list(thematic_categories.values())[:5]:
            if category.key_findings:
                key_insights.append(category.key_findings[0])
        if not key_insights and summaries:
            key_insights = summaries[:5]

        critical_risks = []
        for skill_output in skill_outputs.values():
            summary = skill_output.get("summary", {})
            if isinstance(summary, dict):
                for weakness in summary.get("critical_weaknesses", []) or []:
                    if isinstance(weakness, str):
                        critical_risks.append(weakness)
        if not critical_risks:
            critical_risks = ["Review macro-skill outputs for unresolved production or market risks."]

        recommended_actions = [
            f"Prioritize improvements in {category.category_name.lower()} based on synthesized findings."
            for category in list(thematic_categories.values())[:4]
        ]

        skill_weights_raw = {skill: max(_skill_overall_confidence(skill_outputs[skill]), 0.01) for skill in present_skills}
        weight_total = sum(skill_weights_raw.values())
        skill_weights = {skill: round(value / weight_total, 2) for skill, value in skill_weights_raw.items()}

        cross_cutting = CrossCuttingInsights(
            design_technology_synergy=CrossCuttingInsight(
                insight_id="cci-design-tech",
                title="Design-Technology Alignment",
                narrative=" ".join(summaries[:2]) or "Design and technology analyses should be reviewed jointly for execution feasibility.",
                contributing_skills=["design_art", "technology_systems"],
                confidence=min(
                    _skill_overall_confidence(macro_outputs.design_art),
                    _skill_overall_confidence(macro_outputs.technology_systems),
                ),
            ),
            player_experience_arc=CrossCuttingInsight(
                insight_id="cci-player-arc",
                title="Player Experience Arc",
                narrative=" ".join(summaries[1:3]) or "Player experience themes emerge from UX and design analyses.",
                contributing_skills=["design_art", "user_experience", "strategy_market"],
                confidence=(category_scores.get("ui_ux", 0.5) + category_scores.get("gameplay", 0.5)) / 2,
            ),
            commercial_viability=CrossCuttingInsight(
                insight_id="cci-commercial",
                title="Commercial Viability",
                narrative=_safe_get(macro_outputs.strategy_market, "summary", "market_position", default="Market viability requires cross-skill validation."),
                contributing_skills=["strategy_market", "technology_systems", "user_experience"],
                confidence=_skill_overall_confidence(macro_outputs.strategy_market),
            ),
            competitive_moat=CrossCuttingInsight(
                insight_id="cci-moat",
                title="Competitive Differentiation",
                narrative="Synthesis highlights differentiation across design, technology, and market positioning.",
                contributing_skills=["strategy_market", "design_art", "technology_systems"],
                confidence=overall_score,
            ),
            development_health=CrossCuttingInsight(
                insight_id="cci-dev-health",
                title="Development Health",
                narrative="Production and technical analyses inform delivery risk and team capacity outlook.",
                contributing_skills=["strategy_market", "technology_systems"],
                confidence=category_scores.get("production_business", overall_score),
            ),
        )

        recommendations = [
            StrategicRecommendation(
                id=f"rec-{index + 1:03d}",
                title=f"Strengthen {category.category_name}",
                description=category.overview,
                rationale="Derived from unified thematic synthesis across contributing macro-skills.",
                supporting_categories=[category.category_id],
                impact="high" if category.confidence >= 0.8 else "medium",
                effort="medium",
                time_horizon="3-6 months",
                confidence=category.confidence,
                risk_if_ignored=f"Unresolved gaps in {category.category_name.lower()} may affect product quality and market fit.",
            )
            for index, category in enumerate(list(thematic_categories.values())[:4])
        ]

        risk_items = [
            RiskItem(
                id=f"risk-{index + 1:03d}",
                risk_statement=risk,
                categories_affected=["production_business", "audience"],
                likelihood="medium",
                impact="high",
                mitigation="Address through cross-functional review of macro-skill findings.",
                owner="business",
                timeline="Next planning cycle",
            )
            for index, risk in enumerate(critical_risks[:3])
        ]

        report = FinalReport(
            metadata=ReportMetadata(
                report_id=str(uuid.uuid4()),
                game_id=str(game_id),
                game_name=str(game_name),
                generated_at=_utc_now_iso(),
                pipeline_version=PIPELINE_VERSION,
                synthesis_model=SYNTHESIS_MODEL,
                input_skills=[skill for skill in SKILL_KEYS if skill in present_skills],
                input_confidence_range={
                    "min": min(skill_confidences) if skill_confidences else 0.0,
                    "max": max(skill_confidences) if skill_confidences else 0.0,
                },
                output_formats=["json", "markdown", "pdf_html"],
                report_classification=_classify_report(skill_confidences, len(present_skills)),
            ),
            executive_summary=ExecutiveSummary(
                game_identity=f"{game_name} — unified intelligence profile synthesized from {len(present_skills)} macro-skills.",
                market_position=_safe_get(macro_outputs.strategy_market, "summary", "market_position", default="Market position pending additional strategy analysis."),
                key_insights=key_insights[:5],
                critical_risks=critical_risks[:3],
                recommended_actions=recommended_actions[:4],
                overall_confidence=round(overall_score, 2),
            ),
            thematic_analysis=ThematicAnalysis(**thematic_categories),
            cross_cutting_insights=cross_cutting,
            strategic_recommendations=recommendations,
            risk_assessment=risk_items,
            appendices=Appendices(
                source_index=_build_source_index(macro_outputs),
                confidence_breakdown=ConfidenceBreakdown(
                    per_category=category_scores,
                    per_skill={skill: _skill_overall_confidence(skill_outputs[skill]) for skill in present_skills},
                    adjustment_rationale=[
                        "Deterministic synthesis applied primary-skill weighting (60%) with cross-skill blending (40%)."
                    ],
                ),
                conflict_log=[],
                data_gaps=[
                    category.category_name
                    for category in thematic_categories.values()
                    if category.confidence < 0.5
                ],
                methodology_notes=(
                    f"Deterministic synthesis at {_utc_now_iso()} using GetSmart v{PIPELINE_VERSION}. "
                    "Conflict resolution deferred to Gemini mode when API key is configured."
                ),
            ),
            confidence=ConfidenceMetrics(
                overall_score=round(overall_score, 2),
                category_scores=category_scores,
                skill_contribution_weights=skill_weights,
                data_quality_notes=[
                    "Deterministic synthesis mode — for full conflict resolution enable GEMINI_API_KEY."
                ],
            ),
        )
        return report, self.WORKFLOW_STEPS
