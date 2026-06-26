from __future__ import annotations

from typing import Any

from backend.app.scraper.domain.models import (
    GameMetadata,
    MasterContext,
    MasterMetadata,
    MasterPartitions,
    MiniContexts,
)


def _extract_hard_data_summary(worker_payload: dict[str, Any]) -> dict[str, Any]:
    if "hard_data_summary" in worker_payload and isinstance(worker_payload["hard_data_summary"], dict):
        return worker_payload["hard_data_summary"]

    analysis_block = worker_payload.get("analysis")
    if isinstance(analysis_block, dict):
        hard_data_summary = analysis_block.get("hard_data_summary")
        if isinstance(hard_data_summary, dict):
            return hard_data_summary

    return {}


def _extract_confidence_score(worker_payload: dict[str, Any]) -> float:
    candidate = worker_payload.get("confidence_score")
    if isinstance(candidate, (int, float)):
        return float(candidate)

    analysis_block = worker_payload.get("analysis")
    if isinstance(analysis_block, dict):
        nested_candidate = analysis_block.get("confidence_score")
        if isinstance(nested_candidate, (int, float)):
            return float(nested_candidate)

    return 0.0


def _extract_evidence_count(worker_payload: dict[str, Any]) -> int:
    candidate = worker_payload.get("evidence_count")
    if isinstance(candidate, int) and candidate >= 0:
        return candidate

    analysis_block = worker_payload.get("analysis")
    if isinstance(analysis_block, dict):
        nested_candidate = analysis_block.get("evidence_count")
        if isinstance(nested_candidate, int) and nested_candidate >= 0:
            return nested_candidate

    return 0


def assemble_master_json(
    *,
    game_payload: dict[str, Any],
    design_art_json: dict[str, Any],
    user_experience_json: dict[str, Any],
    technology_systems_json: dict[str, Any],
    strategy_market_json: dict[str, Any],
    version: str = "1.0.0",
) -> MasterContext:
    worker_payloads = {
        "design_art": design_art_json,
        "user_experience": user_experience_json,
        "technology_systems": technology_systems_json,
        "strategy_market": strategy_market_json,
    }

    workers_executed: list[str] = []
    workers_failed: list[str] = []

    for worker_name, payload in worker_payloads.items():
        status = payload.get("status")
        if status == "failed":
            workers_failed.append(worker_name)
        else:
            workers_executed.append(worker_name)

    confidence_scores = [_extract_confidence_score(payload) for payload in worker_payloads.values()]
    overall_confidence_score = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    overall_confidence_score = max(0.0, min(1.0, overall_confidence_score))

    total_evidence_count = sum(_extract_evidence_count(payload) for payload in worker_payloads.values())

    mini_contexts = MiniContexts(
        design_art=design_art_json,
        user_experience=user_experience_json,
        technology_systems=technology_systems_json,
        strategy_market=strategy_market_json,
    )

    partitions = MasterPartitions(
        design_and_art=_extract_hard_data_summary(design_art_json),
        user_experience=_extract_hard_data_summary(user_experience_json),
        technology_and_systems=_extract_hard_data_summary(technology_systems_json),
        strategy_and_market=_extract_hard_data_summary(strategy_market_json),
    )

    master_metadata = MasterMetadata(
        game_id=game_payload["game_id"],
        game_name=game_payload["name"],
        version=version,
        workers_executed=workers_executed,
        workers_failed=workers_failed,
        total_evidence_count=total_evidence_count,
        overall_confidence_score=overall_confidence_score,
    )

    game_metadata = GameMetadata(
        game_id=game_payload["game_id"],
        name=game_payload["name"],
        release_year=game_payload["release_year"],
        aliases=game_payload.get("aliases", []),
    )

    return MasterContext(
        metadata=master_metadata,
        game_metadata=game_metadata,
        mini_contexts=mini_contexts,
        partitions=partitions,
    )
