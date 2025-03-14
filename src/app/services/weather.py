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


# Create a singleton instance
weather_service = WeatherService()
