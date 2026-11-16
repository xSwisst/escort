from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring and Docker healthcheck"""
    return {
        "status": "healthy",
        "service": "photos_service"
    }
