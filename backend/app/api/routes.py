from fastapi import APIRouter
from .macro_skills.design_art_skill import router as design_art_router

router = APIRouter()
router.include_router(design_art_router, prefix='/macro-skills/design-art', tags=['macro-skills'])

@router.get('/health')
async def health():
    return {'status': 'ok'}
