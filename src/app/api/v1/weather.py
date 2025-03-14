"""Weather API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status

from src.app.schemas.weather import WeatherRequest, WeatherResponse
from src.app.services.weather import weather_service

router = APIRouter(tags=["weather"])
logger = logging.getLogger(__name__)


@router.post(
    "/",
    response_model=WeatherResponse,
    status_code=status.HTTP_200_OK,
    summary="Get weather data",
    description="Get weather data for a location by coordinates.",
)
async def get_weather(request: WeatherRequest) -> WeatherResponse:
    """Get weather data for a location by coordinates.

    Args:
        request: Weather request containing coordinates.

    Returns:
        Weather data for the requested location.

    Raises:
        HTTPException: If there's an error fetching the weather data.
    """
    try:
        logger.info(
            f"Getting weather data for coordinates: {request.lat}, {request.lon}"
        )

        # Get weather data
        weather_data = await weather_service.get_weather_data(request.lat, request.lon)
        return WeatherResponse(**weather_data)

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching weather data",
        )
