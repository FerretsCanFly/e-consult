"""Actuator endpoints for application health and info."""

from fastapi import APIRouter

# Create a router for actuator endpoints
router = APIRouter(prefix="/actuator", tags=["actuator"])


@router.get("/health")
def health():
    """Health check endpoint in actuator style."""
    return {"status": "UP"}


@router.get("/info")
def info():
    """Application information endpoint."""
    return {
        "app": {"name": "python-ai-service", "version": "1.0.0"}
    }
