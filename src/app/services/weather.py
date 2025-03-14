"""Weather service module for interacting with OpenWeatherMap API."""

import logging
from datetime import datetime
from typing import Any, Dict

import httpx

from src.app.core.config import settings
from src.app.services.google_maps import google_maps_service

logger = logging.getLogger(__name__)

# Add OpenWeatherMap API key to settings
if not hasattr(settings, "OPENWEATHERMAP_API_KEY"):
    logger.warning(
        "OPENWEATHERMAP_API_KEY not found in settings. Weather API calls will fail."
    )


class WeatherService:
    """Service for interacting with OpenWeatherMap API."""

    def __init__(self):
        """Initialize the weather service."""
        self.api_key = getattr(settings, "OPENWEATHERMAP_API_KEY", None)
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.bom_uv_base_url = (
            "http://www.bom.gov.au/climate/maps/averages/uv-index/maps"
        )
        self.bom_temp_base_url = (
            "http://www.bom.gov.au/climate/maps/averages/temperature/maps"
        )

    async def get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get weather data from OpenWeatherMap API.

        Args:
            lat: Latitude of the location.
            lon: Longitude of the location.

        Returns:
            Weather data from OpenWeatherMap API.

        Raises:
            ValueError: If the API key is not configured.
            httpx.HTTPError: If there's an error with the HTTP request.
        """
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key is not configured")

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",  # Use metric units (Celsius)
            "exclude": "minutely,hourly,daily,alerts",  # Only get current weather
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                # Get location information using Google Maps service
                try:
                    location_info = await google_maps_service.reverse_geocode(lat, lon)
                except Exception as e:
                    logger.warning(f"Error getting location info from Google Maps: {e}")
                    # Fallback to basic location info if Google Maps fails
                    location_info = {
                        "lat": lat,
                        "lng": lon,
                        "city": "Unknown",
                        "country": "Unknown",
                        "formatted_address": "Unknown",
                    }

                # Format the response
                return {
                    "location": {
                        "name": location_info.get("formatted_address", "Unknown"),
                        "address": location_info.get("formatted_address", "Unknown"),
                        "lat": lat,
                        "lon": lon,
                        "country": location_info.get("country", "Unknown"),
                        "city": location_info.get("city", "Unknown"),
                    },
                    "current": data["current"],
                    "timestamp": datetime.now().isoformat(),
                }
        except httpx.HTTPError as e:
            logger.error(f"Error fetching weather data: {e}")
            raise ValueError(f"Error fetching weather data: {str(e)}")

    def get_uv_index_heatmap_url(self, period: str) -> str:
        """Get URL for UV index heatmap from Australian Bureau of Meteorology.

        Args:
            period: Time period for the UV index heatmap (annual or month name).

        Returns:
            URL of the UV index heatmap image.

        Raises:
            ValueError: If the period is invalid.
        """
        # Map period to URL suffix
        period_map = {
            "annual": "uv-an.png",
            "jan": "uv-jan.png",
            "feb": "uv-feb.png",
            "mar": "uv-mar.png",
            "apr": "uv-apr.png",
            "may": "uv-may.png",
            "jun": "uv-jun.png",
            "jul": "uv-jul.png",
            "aug": "uv-aug.png",
            "sep": "uv-sep.png",
            "oct": "uv-oct.png",
            "nov": "uv-nov.png",
            "dec": "uv-dec.png",
        }

        if period.lower() not in period_map:
            raise ValueError(
                f"Invalid period: {period}. Must be 'annual' or a three-letter month abbreviation."
            )

        # Construct the URL
        return f"{self.bom_uv_base_url}/{period_map[period.lower()]}"

    def get_temperature_map_url(self, temp_type: str, region: str, period: str) -> str:
        """Get URL for temperature map from Australian Bureau of Meteorology.

        Args:
            temp_type: Type of temperature map (mean, max, or min).
            region: Region of Australia (whole Australia or specific state).
            period: Time period for the temperature map (annual or month name).

        Returns:
            URL of the temperature map image.

        Raises:
            ValueError: If any of the parameters are invalid.
        """
        # Map temperature type to URL path
        temp_type_map = {
            "mean": "mean",
            "max": "mxt",
            "min": "mnt",
        }

        # Map period to URL suffix
        period_map = {
            "annual": "an.png",
            "jan": "jan.png",
            "feb": "feb.png",
            "mar": "mar.png",
            "apr": "apr.png",
            "may": "may.png",
            "jun": "jun.png",
            "jul": "jul.png",
            "aug": "aug.png",
            "sep": "sep.png",
            "oct": "oct.png",
            "nov": "nov.png",
            "dec": "dec.png",
        }

        # Validate parameters
        if temp_type.lower() not in temp_type_map:
            raise ValueError(
                f"Invalid temperature type: {temp_type}. Must be 'mean', 'max', or 'min'."
            )

        if region.lower() not in ["aus", "ns", "nt", "qd", "sa", "ta", "vc", "wa"]:
            raise ValueError(
                f"Invalid region: {region}. Must be 'aus', 'ns', 'nt', 'qd', 'sa', 'ta', 'vc', or 'wa'."
            )

        if period.lower() not in period_map:
            raise ValueError(
                f"Invalid period: {period}. Must be 'annual' or a three-letter month abbreviation."
            )

        # Construct the URL
        return f"{self.bom_temp_base_url}/{temp_type_map[temp_type.lower()]}/{region.lower()}/{temp_type_map[temp_type.lower()]}{region.lower()}{period_map[period.lower()]}"


# Create a singleton instance
weather_service = WeatherService()
