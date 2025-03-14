"""Skin cancer data API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.app.api.dependencies import get_db
from src.app.crud.crud_skin_cancer import skin_cancer_crud
from src.app.schemas.skin_cancer import (
    AgeGroupEnum,
    DataTypeEnum,
    SexEnum,
    SkinCancerDataResponse,
    SkinCancerFilter,
)

router = APIRouter(tags=["skin_cancer"])
logger = logging.getLogger(__name__)


@router.get(
    "/",
    response_model=SkinCancerDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get skin cancer data",
    description="Get skin cancer data with optional filtering.",
)
async def get_skin_cancer_data(
    data_type: Optional[DataTypeEnum] = None,
    year: Optional[int] = None,
    sex: Optional[SexEnum] = None,
    age_group: Optional[AgeGroupEnum] = None,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db),
) -> SkinCancerDataResponse:
    """Get skin cancer data with optional filtering.

    Args:
        data_type: Type of data (Actual or Projections)
        year: Year of the data
        sex: Gender category (Females, Males, Persons)
        age_group: Age range in years
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        Filtered skin cancer data

    Raises:
        HTTPException: If there's an error fetching the data
    """
    try:
        logger.info("Getting skin cancer data with filters")

        # Create filter object
        filters = SkinCancerFilter(
            data_type=data_type,
            year=year,
            sex=sex,
            age_group=age_group,
        )

        # Set cancer_group filter to "Melanoma of the skin"
        filters_dict = filters.model_dump(exclude_none=True)
        filters_dict["cancer_group"] = "Melanoma of the skin"

        # Get filtered data
        data = skin_cancer_crud.get_filtered(
            db, filters=filters, skip=skip, limit=limit
        )
        total = skin_cancer_crud.count_filtered(db, filters=filters)

        return SkinCancerDataResponse(data=data, total=total)

    except Exception as e:
        logger.error(f"Error getting skin cancer data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching skin cancer data",
        )
