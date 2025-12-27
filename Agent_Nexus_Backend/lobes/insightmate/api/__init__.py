from fastapi import APIRouter
from lobes.insightmate.api.v1.routes import router as v1_router

router = APIRouter()

router.include_router(v1_router, prefix="/v1")

__all__ = ["router"]