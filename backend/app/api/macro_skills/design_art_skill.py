from fastapi import APIRouter

from ...models.macro_skills.design_art_models import DesignArtInputModel, DesignArtOutputModel
from ...services.macro_skills.design_art_service import DesignArtService

router = APIRouter()
service = DesignArtService()


@router.post('/', response_model=DesignArtOutputModel, status_code=200)
async def analyze_design_art(input_data: DesignArtInputModel):
    """Analyze design and art mini-context and return structured intelligence."""
    return await service.analyze(input_data)
