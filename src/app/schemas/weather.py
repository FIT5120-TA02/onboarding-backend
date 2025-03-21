"""Weather API schemas."""

from typing import List, Literal

from pydantic import BaseModel, Field


class WeatherRequest(BaseModel):
    """Request schema for weather data by coordinates.

    Attributes:
        lat: Latitude of the location.
        lon: Longitude of the location.
        name: Name of the user requesting the weather data.
    """

    lat: float = Field(..., description="Latitude of the location", ge=-90, le=90)
    lon: float = Field(..., description="Longitude of the location", ge=-180, le=180)
    name: str = Field(..., description="Name of the user requesting the weather data")


class WeatherCondition(BaseModel):
    """Weather condition schema.

    Attributes:
        id: Weather condition id.
        main: Group of weather parameters (Rain, Snow, Clouds etc.).
        description: Weather condition within the group.
        icon: Weather icon id.
    """

    id: int = Field(..., description="Weather condition id")
    main: str = Field(..., description="Group of weather parameters")
    description: str = Field(..., description="Weather condition within the group")
    icon: str = Field(..., description="Weather icon id")


class CurrentWeather(BaseModel):
    """Current weather data schema.

    Attributes:
        temp: Current temperature in Celsius.
        feels_like: Human perception of temperature in Celsius.
        pressure: Atmospheric pressure in hPa.
        humidity: Humidity percentage.
        uvi: UV index.
        clouds: Cloudiness percentage.
        visibility: Average visibility in meters.
        wind_speed: Wind speed in meters/sec.
        wind_deg: Wind direction in degrees.
        weather: List of weather conditions.
        sunrise: Sunrise time, Unix, UTC.
        sunset: Sunset time, Unix, UTC.
    """

    temp: float = Field(..., description="Current temperature in Celsius")
    feels_like: float = Field(
        ..., description="Human perception of temperature in Celsius"
    )
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    humidity: int = Field(..., description="Humidity percentage")
    uvi: float = Field(..., description="UV index")
    clouds: int = Field(..., description="Cloudiness percentage")
    visibility: int = Field(..., description="Average visibility in meters")
    wind_speed: float = Field(..., description="Wind speed in meters/sec")
    wind_deg: int = Field(..., description="Wind direction in degrees")
    weather: List[WeatherCondition] = Field(..., description="Weather conditions")
    sunrise: int = Field(..., description="Sunrise time, Unix, UTC")
    sunset: int = Field(..., description="Sunset time, Unix, UTC")


class LocationInfo(BaseModel):
    """Location information schema.

    Attributes:
        name: Name of the location.
        address: Full address of the location.
        lat: Latitude of the location.
        lon: Longitude of the location.
        country: Country of the location.
        city: City of the location.
    """

    name: str = Field(..., description="Name of the location")
    address: str = Field(..., description="Full address of the location")
    lat: float = Field(..., description="Latitude of the location")
    lon: float = Field(..., description="Longitude of the location")
    country: str = Field(..., description="Country of the location")
    city: str = Field(..., description="City of the location")


class WeatherResponse(BaseModel):
    """Weather response schema.

    Attributes:
        location: Location information.
        current: Current weather data.
        timestamp: Response timestamp.
    """

    location: LocationInfo = Field(..., description="Location information")
    current: CurrentWeather = Field(..., description="Current weather data")
    timestamp: str = Field(..., description="Response timestamp in ISO format")


class UVIndexHeatmapResponse(BaseModel):
    """Response schema for UV index heatmap.

    Attributes:
        url: URL of the UV index heatmap image.
        period: Time period of the UV index heatmap.
        source: Source of the UV index heatmap data.
    """

    url: str = Field(..., description="URL of the UV index heatmap image")
    period: str = Field(..., description="Time period of the UV index heatmap")
    source: str = Field(
        "Australian Bureau of Meteorology",
        description="Source of the UV index heatmap data",
    )


class TemperatureMapResponse(BaseModel):
    """Response schema for temperature map.

    Attributes:
        url: URL of the temperature map image.
        temp_type: Type of temperature (mean, maximum, or minimum).
        region: Region of Australia.
        period: Time period of the temperature map.
        source: Source of the temperature map data.
    """

    url: str = Field(..., description="URL of the temperature map image")
    temp_type: str = Field(
        ..., description="Type of temperature (mean, maximum, or minimum)"
    )
    region: str = Field(..., description="Region of Australia")
    period: str = Field(..., description="Time period of the temperature map")
    source: str = Field(
        "Australian Bureau of Meteorology",
        description="Source of the temperature map data",
    )
