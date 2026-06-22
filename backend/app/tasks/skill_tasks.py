"""
Celery tasks for Macro-Skill execution (Phase 3 — Parallel Analysis).

Each task wraps a skill's async analyze() in asyncio.run() so Celery
workers can dispatch them in parallel without async worker configuration.
"""

import asyncio
import logging

from ..celery_app import celery_app
from ..services.macro_skills.user_experience import UserExperienceSkill

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    name="skills.run_ux_skill",
    serializer="json",
)
def run_ux_skill(self, mini_context: dict) -> dict:
    """
    Execute User Experience Macro-Skill analysis.

    Args:
        mini_context: mini_context_user_experience dict from Master-JSON.

    Returns:
        Structured UX intelligence dict for the Phase 4 Synthesizer.
    """
    skill = UserExperienceSkill()
    try:
        return asyncio.run(skill.analyze(mini_context))
    except Exception as exc:
        game_id = mini_context.get("metadata", {}).get("game_id", "unknown")
        logger.error("run_ux_skill failed for %s (attempt %d): %s", game_id, self.request.retries, exc)
        raise self.retry(exc=exc)
