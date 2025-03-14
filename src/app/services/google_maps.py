"""Google Maps API service module."""

import logging
from typing import Any, Dict, List, Optional

import httpx

from src.app.core.config import settings

logger = logging.getLogger(__name__)

# Check if Google Maps API key is configured
if not hasattr(settings, "GOOGLE_MAPS_API_KEY"):
    logger.warning(
        "GOOGLE_MAPS_API_KEY not found in settings. Google Maps API calls will fail."
    )


class GoogleMapsService:
    """Service for interacting with Google Maps API."""

    def __init__(self):
        """Initialize the Google Maps service."""
        self.api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
        self.places_autocomplete_url = (
            "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        )
        self.places_details_url = (
            "https://maps.googleapis.com/maps/api/place/details/json"
        )
        self.geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"

        # Australia bounds (approximate)
        self.australia_bounds = {
            "southwest": {"lat": -43.6345972634, "lng": 113.338953078},
            "northeast": {"lat": -10.6681857235, "lng": 153.569469029},
        }

    async def get_address_predictions(self, input_text: str) -> List[Dict[str, Any]]:
        """Get address predictions from Google Places Autocomplete API.

        Args:
            input_text: The text to get predictions for.

        Returns:
            List of address predictions.

        Raises:
            ValueError: If the API key is not configured or if there's an error with the request.
        """
        if not self.api_key:
            raise ValueError("Google Maps API key is not configured")

        params = {
            "input": input_text,
            "key": self.api_key,
            "components": "country:au",  # Restrict to Australia
            "types": "address",  # Only return addresses
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.places_autocomplete_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data["status"] != "OK" and data["status"] != "ZERO_RESULTS":
                    logger.error(f"Google Places API error: {data['status']}")
                    raise ValueError(f"Google Places API error: {data['status']}")

                predictions = []
                for prediction in data.get("predictions", []):
                    predictions.append(
                        {
                            "place_id": prediction.get("place_id"),
                            "description": prediction.get("description"),
                            "structured_formatting": prediction.get(
                                "structured_formatting", {}
                            ),
                        }
                    )

                return predictions
        except httpx.HTTPError as e:
            logger.error(f"Error fetching address predictions: {e}")
            raise ValueError(f"Error fetching address predictions: {str(e)}")

    async def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Get place details from Google Places Details API.

        Args:
            place_id: The place ID to get details for.

        Returns:
            Place details including coordinates.

        Raises:
            ValueError: If the API key is not configured or if there's an error with the request.
        """
        if not self.api_key:
            raise ValueError("Google Maps API key is not configured")

        params = {
            "place_id": place_id,
            "key": self.api_key,
            "fields": "formatted_address,geometry,name,address_component",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.places_details_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data["status"] != "OK":
                    logger.error(f"Google Places API error: {data['status']}")
                    raise ValueError(f"Google Places API error: {data['status']}")

                result = data.get("result", {})

                # Check if the place is in Australia
                is_in_australia = False
                for component in result.get("address_components", []):
                    if (
                        "country" in component.get("types", [])
                        and component.get("short_name") == "AU"
                    ):
                        is_in_australia = True
                        break

                if not is_in_australia:
                    raise ValueError("Location is not in Australia")

                # Extract location details
                geometry = result.get("geometry", {})
                location = geometry.get("location", {})

                # Extract city and country from address components
                city = "Unknown"
                country = "Unknown"
                for component in result.get("address_components", []):
                    if "locality" in component.get("types", []):
                        city = component.get("long_name")
                    elif (
                        "administrative_area_level_1" in component.get("types", [])
                        and not city
                        or city == "Unknown"
                    ):
                        # Use administrative area if locality is not available
                        city = component.get("long_name")
                    elif "country" in component.get("types", []):
                        country = component.get("long_name")

                return {
                    "place_id": place_id,
                    "formatted_address": result.get("formatted_address"),
                    "name": result.get("name"),
                    "lat": location.get("lat"),
                    "lng": location.get("lng"),
                    "city": city,
                    "country": country,
                }
        except httpx.HTTPError as e:
            logger.error(f"Error fetching place details: {e}")
            raise ValueError(f"Error fetching place details: {str(e)}")

    async def geocode_address(self, address: str) -> Dict[str, Any]:
        """Geocode an address to get coordinates.

        Args:
            address: The address to geocode.

        Returns:
            Geocoding result with coordinates.

        Raises:
            ValueError: If the API key is not configured, if there's an error with the request,
                       or if the location is not in Australia.
        """
        if not self.api_key:
            raise ValueError("Google Maps API key is not configured")

        params = {
            "address": address,
            "key": self.api_key,
            "components": "country:au",  # Restrict to Australia
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.geocode_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data["status"] != "OK":
                    logger.error(f"Google Geocoding API error: {data['status']}")
                    raise ValueError(f"Google Geocoding API error: {data['status']}")

                result = data.get("results", [])[0]

                # Check if the place is in Australia
                is_in_australia = False
                for component in result.get("address_components", []):
                    if (
                        "country" in component.get("types", [])
                        and component.get("short_name") == "AU"
                    ):
                        is_in_australia = True
                        break

                if not is_in_australia:
                    raise ValueError("Location is not in Australia")

                # Extract location details
                geometry = result.get("geometry", {})
                location = geometry.get("location", {})

                # Extract city and country from address components
                city = "Unknown"
                country = "Unknown"
                for component in result.get("address_components", []):
                    if "locality" in component.get("types", []):
                        city = component.get("long_name")
                    elif (
                        "administrative_area_level_1" in component.get("types", [])
                        and not city
                        or city == "Unknown"
                    ):
                        # Use administrative area if locality is not available
                        city = component.get("long_name")
                    elif "country" in component.get("types", []):
                        country = component.get("long_name")

                return {
                    "formatted_address": result.get("formatted_address"),
                    "lat": location.get("lat"),
                    "lng": location.get("lng"),
                    "city": city,
                    "country": country,
                }
        except httpx.HTTPError as e:
            logger.error(f"Error geocoding address: {e}")
            raise ValueError(f"Error geocoding address: {str(e)}")

    async def reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
        """Reverse geocode coordinates to get address information.

        Args:
            lat: Latitude of the location.
            lng: Longitude of the location.

        Returns:
            Reverse geocoding result with address information.

        Raises:
            ValueError: If the API key is not configured, if there's an error with the request,
                       or if the location is not in Australia.
        """
        if not self.api_key:
            raise ValueError("Google Maps API key is not configured")

        params = {
            "latlng": f"{lat},{lng}",
            "key": self.api_key,
            "result_type": "street_address|locality|administrative_area_level_1|country",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.geocode_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data["status"] != "OK" and data["status"] != "ZERO_RESULTS":
                    logger.error(
                        f"Google Reverse Geocoding API error: {data['status']}"
                    )
                    raise ValueError(
                        f"Google Reverse Geocoding API error: {data['status']}"
                    )

                if not data.get("results"):
                    return {"lat": lat, "lng": lng}

                result = data.get("results", [])[0]

                # Check if the place is in Australia
                is_in_australia = False
                for component in result.get("address_components", []):
                    if (
                        "country" in component.get("types", [])
                        and component.get("short_name") == "AU"
                    ):
                        is_in_australia = True
                        break

                if not is_in_australia:
                    raise ValueError("Location is not in Australia")

                # Extract city and country from address components
                city = "Unknown"
                country = "Unknown"
                for component in result.get("address_components", []):
                    if "locality" in component.get("types", []):
                        city = component.get("long_name")
                    elif (
                        "administrative_area_level_1" in component.get("types", [])
                        and not city
                        or city == "Unknown"
                    ):
                        # Use administrative area if locality is not available
                        city = component.get("long_name")
                    elif "country" in component.get("types", []):
                        country = component.get("long_name")

                return {
                    "formatted_address": result.get("formatted_address"),
                    "name": result.get("formatted_address"),
                    "lat": lat,
                    "lng": lng,
                    "city": city,
                    "country": country,
                }
        except httpx.HTTPError as e:
            logger.error(f"Error reverse geocoding: {e}")
            raise ValueError(f"Error reverse geocoding: {str(e)}")


# Create a singleton instance
google_maps_service = GoogleMapsService()
