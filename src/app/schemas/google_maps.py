"""Google Maps API schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class AddressPredictionRequest(BaseModel):
    """Request schema for address prediction.

    Attributes:
        input: The text to get predictions for.
    """

    input: str = Field(
        ..., description="Text to get address predictions for", min_length=2
    )


class StructuredFormatting(BaseModel):
    """Structured formatting for address prediction.

    Attributes:
        main_text: The main text of the prediction.
        secondary_text: The secondary text of the prediction.
    """

    main_text: str = Field(..., description="Main text of the prediction")
    secondary_text: Optional[str] = Field(
        None, description="Secondary text of the prediction"
    )


class AddressPrediction(BaseModel):
    """Address prediction schema.

    Attributes:
        place_id: The place ID of the prediction.
        description: The description of the prediction.
        structured_formatting: Structured formatting of the prediction.
    """

    place_id: str = Field(..., description="Place ID of the prediction")
    description: str = Field(..., description="Description of the prediction")
    structured_formatting: Optional[StructuredFormatting] = Field(
        None, description="Structured formatting of the prediction"
    )


class AddressPredictionResponse(BaseModel):
    """Response schema for address prediction.

    Attributes:
        predictions: List of address predictions.
    """

    predictions: List[AddressPrediction] = Field(
        ..., description="List of address predictions"
    )


class PlaceDetailsRequest(BaseModel):
    """Request schema for place details.

    Attributes:
        place_id: The place ID to get details for.
    """

    place_id: str = Field(..., description="Place ID to get details for")


class PlaceDetails(BaseModel):
    """Place details schema.

    Attributes:
        place_id: The place ID.
        formatted_address: The formatted address.
        name: The name of the place.
        lat: The latitude of the place.
        lng: The longitude of the place.
        city: The city of the place.
        country: The country of the place.
    """

    place_id: str = Field(..., description="Place ID")
    formatted_address: str = Field(..., description="Formatted address")
    name: Optional[str] = Field(None, description="Name of the place")
    lat: float = Field(..., description="Latitude of the place")
    lng: float = Field(..., description="Longitude of the place")
    city: str = Field(..., description="City of the place")
    country: str = Field(..., description="Country of the place")


class GeocodeRequest(BaseModel):
    """Request schema for geocoding.

    Attributes:
        address: The address to geocode.
    """

    address: str = Field(..., description="Address to geocode", min_length=3)


class GeocodeResponse(BaseModel):
    """Response schema for geocoding.

    Attributes:
        formatted_address: The formatted address.
        lat: The latitude of the location.
        lng: The longitude of the location.
        city: The city of the location.
        country: The country of the location.
    """

    formatted_address: str = Field(..., description="Formatted address")
    lat: float = Field(..., description="Latitude of the location")
    lng: float = Field(..., description="Longitude of the location")
    city: str = Field(..., description="City of the location")
    country: str = Field(..., description="Country of the location")
