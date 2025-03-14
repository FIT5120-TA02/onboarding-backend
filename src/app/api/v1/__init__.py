"""API v1 package."""

from fastapi import APIRouter

from src.app.api.v1.google_maps import router as google_maps_router
from src.app.api.v1.health import router as health_router
from src.app.api.v1.skin_cancer import router as skin_cancer_router
from src.app.api.v1.weather import router as weather_router

api_router = APIRouter()

# Include all routers
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(
    google_maps_router, prefix="/google-maps", tags=["google-maps"]
)
api_router.include_router(
    skin_cancer_router, prefix="/skin-cancer", tags=["skin-cancer"]
)
api_router.include_router(weather_router, prefix="/weather", tags=["weather"])
