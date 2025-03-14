"""Weather API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, Query, status

from src.app.schemas.weather import (
    TemperatureMapResponse,
    UVIndexHeatmapResponse,
    WeatherRequest,
    WeatherResponse,
)
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


@router.get(
    "/uv-index-heatmap",
    response_model=UVIndexHeatmapResponse,
    status_code=status.HTTP_200_OK,
    summary="Get UV index heatmap",
    description="Get URL for UV index heatmap from Australian Bureau of Meteorology.",
)
async def get_uv_index_heatmap(
    period: str = Query(
        "annual",
        description="Time period for the UV index heatmap (annual or month name)",
    )
) -> UVIndexHeatmapResponse:
    """Get URL for UV index heatmap from Australian Bureau of Meteorology.

    Args:
        period: Time period for the UV index heatmap (annual or month name).

    Returns:
        UV index heatmap URL and metadata.

    Raises:
        HTTPException: If there's an error fetching the UV index heatmap URL.
    """
    try:
        logger.info(f"Getting UV index heatmap for period: {period}")

        # Get UV index heatmap URL
        url = weather_service.get_uv_index_heatmap_url(period)

        # Map period to display name
        period_display = {
            "annual": "Annual",
            "jan": "January",
            "feb": "February",
            "mar": "March",
            "apr": "April",
            "may": "May",
            "jun": "June",
            "jul": "July",
            "aug": "August",
            "sep": "September",
            "oct": "October",
            "nov": "November",
            "dec": "December",
        }

        return UVIndexHeatmapResponse(
            url=url,
            period=period_display.get(period, period.capitalize()),
        )

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting UV index heatmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching UV index heatmap",
        )


@router.get(
    "/temperature-map",
    response_model=TemperatureMapResponse,
    status_code=status.HTTP_200_OK,
    summary="Get temperature map",
    description="Get URL for temperature map from Australian Bureau of Meteorology.",
)
async def get_temperature_map(
    temp_type: str = Query(
        "mean", description="Type of temperature map (mean, max, or min)"
    ),
    region: str = Query(
        "aus", description="Region of Australia (aus, ns, nt, qd, sa, ta, vc, wa)"
    ),
    period: str = Query(
        "annual",
        description="Time period for the temperature map (annual or month name)",
    ),
) -> TemperatureMapResponse:
    """Get URL for temperature map from Australian Bureau of Meteorology.

    Args:
        temp_type: Type of temperature map (mean, max, or min).
        region: Region of Australia (whole Australia or specific state).
        period: Time period for the temperature map (annual or month name).

    Returns:
        Temperature map URL and metadata.

    Raises:
        HTTPException: If there's an error fetching the temperature map URL.
    """
    try:
        logger.info(
            f"Getting temperature map for type: {temp_type}, "
            f"region: {region}, period: {period}"
        )

        # Get temperature map URL
        url = weather_service.get_temperature_map_url(temp_type, region, period)

        # Map temperature type to display name
        temp_type_display = {
            "mean": "Mean Temperature",
            "max": "Maximum Temperature",
            "min": "Minimum Temperature",
        }

        # Map region to display name
        region_display = {
            "aus": "Australia",
            "ns": "New South Wales",
            "nt": "Northern Territory",
            "qd": "Queensland",
            "sa": "South Australia",
            "ta": "Tasmania",
            "vc": "Victoria",
            "wa": "Western Australia",
        }

        # Map period to display name
        period_display = {
            "annual": "Annual",
            "jan": "January",
            "feb": "February",
            "mar": "March",
            "apr": "April",
            "may": "May",
            "jun": "June",
            "jul": "July",
            "aug": "August",
            "sep": "September",
            "oct": "October",
            "nov": "November",
            "dec": "December",
        }

        return TemperatureMapResponse(
            url=url,
            temp_type=temp_type_display.get(temp_type, temp_type.capitalize()),
            region=region_display.get(region, region.upper()),
            period=period_display.get(period, period.capitalize()),
        )

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting temperature map: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching temperature map",
        )
