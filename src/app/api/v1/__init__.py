"""API v1 package."""

from fastapi import APIRouter

from src.app.api.v1 import google_maps, health, weather

api_router = APIRouter()

# Include all routers
api_router.include_router(health.router, prefix="/health")
api_router.include_router(weather.router, prefix="/weather")
api_router.include_router(google_maps.router, prefix="/maps")
