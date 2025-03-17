"""Weather API endpoints."""

import logging
import httpx
import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.app.crud.crud_temperature_records import temperature_record_crud
from src.app.crud.crud_uv_records import uv_record_crud

from fastapi import Response
from fastapi.responses import StreamingResponse

from src.app.api.dependencies import get_db
from src.app.crud.crud_locations import location_crud
from src.app.crud.crud_temperature_records import temperature_record_crud
from src.app.crud.crud_users import user_crud
from src.app.crud.crud_uv_records import uv_record_crud
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
    description="Get weather data for a location by coordinates and save to database.",
)
async def get_weather(
    request: WeatherRequest, db: Session = Depends(get_db)
) -> WeatherResponse:
    """Get weather data for a location by coordinates and save to database.

    Args:
        request: Weather request containing coordinates and user name.
        db: Database session.

    Returns:
        Weather data for the requested location.

    Raises:
        HTTPException: If there's an error fetching the weather data.
    """
    try:
        logger.info(
            f"Getting weather data for coordinates: {request.lat}, {request.lon} for user: {request.name}"
        )

        # Get weather data
        weather_data = await weather_service.get_weather_data(request.lat, request.lon)

        # Save data to database
        try:
            # Get or create user
            user = user_crud.get_or_create(db, name=request.name)
            logger.info(f"User found/created: {user.id} - {user.name}")

            # Create or get location
            location_info = weather_data["location"]
            existing_location = location_crud.get_by_coordinates(
                db, latitude=request.lat, longitude=request.lon
            )

            if existing_location:
                location = existing_location
                logger.info(f"Using existing location: {location.id}")
            else:
                location = location_crud.create_with_user(
                    db,
                    obj_in={
                        "lat": request.lat,
                        "lon": request.lon,
                        "city": location_info.get("city"),
                        "country": location_info.get("country"),
                    },
                    user_id=user.id,
                )
                logger.info(f"Created new location: {location.id}")

            # Create temperature record
            temperature_record = temperature_record_crud.create_from_weather_data(
                db, weather_data=weather_data, location_id=location.id
            )
            logger.info(f"Created temperature record: {temperature_record.id}")

            # Create UV record
            uv_record = uv_record_crud.create_from_weather_data(
                db, weather_data=weather_data, location_id=location.id
            )
            logger.info(f"Created UV record: {uv_record.id}")

        except Exception as e:
            logger.error(f"Error saving data to database: {e}")
            # Continue with the response even if database operations fail
            # This ensures the API still returns weather data to the user

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
    "/proxy-image",
    summary="Proxy for image requests",
    description="Proxy endpoint to retrieve images from HTTP sources and serve them via HTTPS",
)
async def proxy_image(
    url: str = Query(..., description="URL of the image to proxy")
) -> StreamingResponse:
    """Proxy for image requests.
    
    Retrieves images from external HTTP sources and serves them via this HTTPS endpoint.
    
    Args:
        url: The URL of the image to proxy.
        
    Returns:
        The image content with appropriate content type.
        
    Raises:
        HTTPException: If there's an error fetching the image.
    """
    try:
        logger.info(f"Proxying image from: {url}")
        if url.startswith('/api/v1/weather/proxy-image'):
            nested_url = url.split('url=', 1)[1]
            url = urllib.parse.unquote(nested_url)
            logger.info(f"Extracted nested URL: {url}")

        if not url.startswith('http://') and not url.startswith('https://'):
            url = f"http://{url}"
            logger.info(f"Added protocol to URL: {url}")
        
        # Use httpx for async HTTP requests
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to retrieve the image from the source"
                )
            
            # Get the content type from the original response
            content_type = response.headers.get("content-type", "image/png")
            
            # Return the image content
            return StreamingResponse(
                content=iter([response.content]),
                media_type=content_type
            )
            
    except Exception as e:
        logger.error(f"Error proxying image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error proxying image"
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

        # Get original UV index heatmap URL
        original_url = weather_service.get_uv_index_heatmap_url(period)
        
        # Create proxied URL
        base_url = "/api/v1/weather/proxy-image"
        proxied_url = f"{base_url}?url={original_url}"

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
            url=proxied_url,
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
    

@router.get("/temperature-records")
def read_temperature_records(db: Session = Depends(get_db)):
    """Getting historical temperature data"""
    return temperature_record_crud.get_temperature_records(db)

@router.get("/uv-records")
def read_uv_records(db: Session = Depends(get_db)):
    """Get all historical UV index records"""
    return uv_record_crud.get_uv_records(db)

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

        # Get original temperature map URL
        original_url = weather_service.get_temperature_map_url(temp_type, region, period)
        
        # Create proxied URL
        base_url = "/api/v1/weather/proxy-image"
        proxied_url = f"{base_url}?url={original_url}"

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
            url=proxied_url,
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