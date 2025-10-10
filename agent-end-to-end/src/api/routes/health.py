from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Simple endpoint to verify that the API is running.
    """
    return {"status": "healthy", "message": "API is up and running"}
