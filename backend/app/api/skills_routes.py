"""
FastAPI routes for Macro-Skill execution.

POST /api/skills/user-experience       → dispatches Celery task, returns job_id
GET  /api/skills/jobs/{job_id}         → polls task status and result
POST /api/skills/user-experience/sync  → runs synchronously (dev/testing only)
"""

import logging

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from ..celery_app import celery_app
from ..skills.user_experience.schemas import JobStatusResponse, TaskResponse, UXMiniContext
from ..skills.user_experience import UserExperienceSkill
from ..tasks.skill_tasks import run_ux_skill

logger = logging.getLogger(__name__)

skills_router = APIRouter(prefix="/skills", tags=["Skills"])


@skills_router.post(
    "/user-experience",
    response_model=TaskResponse,
    summary="Dispatch UX analysis (async via Celery)",
)
async def analyze_user_experience(mini_context: UXMiniContext) -> TaskResponse:
    """
    Dispatch the User Experience Macro-Skill as a Celery task.
    Returns a job_id to poll for the result.
    """
    task = run_ux_skill.delay(mini_context.model_dump())
    return TaskResponse(
        job_id=task.id,
        status="queued",
        skill_id="user_experience",
        game_id=mini_context.metadata.game_id,
    )


@skills_router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Poll Celery task status",
)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Check the status and result of any dispatched skill task.
    status values: PENDING · STARTED · SUCCESS · FAILURE · RETRY
    """
    result = AsyncResult(job_id, app=celery_app)
    response = JobStatusResponse(job_id=job_id, status=result.status)

    if result.ready():
        if result.successful():
            response.result = result.get()
        else:
            response.error = str(result.result)

    return response


@skills_router.post(
    "/user-experience/sync",
    summary="Run UX analysis synchronously (dev/testing only)",
)
async def analyze_user_experience_sync(mini_context: UXMiniContext) -> dict:
    """
    Run User Experience analysis in-process without Celery.
    Use for local development and testing — not suitable for production load.
    """
    skill = UserExperienceSkill()
    return await skill.analyze(mini_context.model_dump())
