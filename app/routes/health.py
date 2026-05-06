from fastapi import APIRouter
from app.config import settings
from app.models.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["system"])

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Railway health check endpoint.
    """
    return HealthResponse(
        status="healthy",
        environment=settings.ENVIRONMENT
    )
