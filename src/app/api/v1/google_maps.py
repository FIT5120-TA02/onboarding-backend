"""Google Maps API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status

from src.app.schemas.google_maps import (
    AddressPredictionRequest,
    AddressPredictionResponse,
    GeocodeRequest,
    GeocodeResponse,
    PlaceDetails,
    PlaceDetailsRequest,
)
from src.app.services.google_maps import google_maps_service

router = APIRouter(tags=["google-maps"])
logger = logging.getLogger(__name__)


@router.post(
    "/address-predictions",
    response_model=AddressPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get address predictions",
    description="Get address predictions from Google Places Autocomplete API. Results are restricted to Australia.",
)
async def get_address_predictions(
    request: AddressPredictionRequest,
) -> AddressPredictionResponse:
    """Get address predictions from Google Places Autocomplete API.

    Args:
        request: Address prediction request containing input text and optional session token.

    Returns:
        Address predictions matching the input text.

    Raises:
        HTTPException: If there's an error fetching address predictions.
    """
    try:
        logger.info(f"Getting address predictions for input: {request.input}")
        predictions = await google_maps_service.get_address_predictions(
            request.input, request.session_token
        )
        return AddressPredictionResponse(predictions=predictions)

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting address predictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching address predictions",
        )


@router.post(
    "/place-details",
    response_model=PlaceDetails,
    status_code=status.HTTP_200_OK,
    summary="Get place details",
    description="Get place details from Google Places Details API. Results are restricted to Australia.",
)
async def get_place_details(request: PlaceDetailsRequest) -> PlaceDetails:
    """Get place details from Google Places Details API.

    Args:
        request: Place details request containing place ID and optional session token.

    Returns:
        Place details including coordinates.

    Raises:
        HTTPException: If there's an error fetching place details.
    """
    try:
        logger.info(f"Getting place details for place_id: {request.place_id}")
        place_details = await google_maps_service.get_place_details(
            request.place_id, request.session_token
        )
        return PlaceDetails(**place_details)

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting place details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching place details",
        )


@router.post(
    "/geocode",
    response_model=GeocodeResponse,
    status_code=status.HTTP_200_OK,
    summary="Geocode address",
    description="Geocode an address to get coordinates. Results are restricted to Australia.",
)
async def geocode_address(request: GeocodeRequest) -> GeocodeResponse:
    """Geocode an address to get coordinates.

    Args:
        request: Geocode request containing address.

    Returns:
        Geocoding result with coordinates.

    Raises:
        HTTPException: If there's an error geocoding the address.
    """
    try:
        logger.info(f"Geocoding address: {request.address}")
        geocode_result = await google_maps_service.geocode_address(request.address)
        return GeocodeResponse(**geocode_result)

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error geocoding address: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error geocoding address",
        )
