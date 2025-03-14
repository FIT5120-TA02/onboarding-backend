"""Skin cancer data API endpoints."""

import logging
from typing import List, Optional

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
    SkinCancerGroupedResponse,
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


@router.get(
    "/visualization",
    response_model=SkinCancerGroupedResponse,
    status_code=status.HTTP_200_OK,
    summary="Get skin cancer data for visualization",
    description="Get grouped skin cancer data for visualization with optional filtering.",
)
async def get_skin_cancer_visualization(
    group_by: List[str] = Query(
        ..., description="Fields to group by (data_type, year, sex, age_group)"
    ),
    data_type: Optional[DataTypeEnum] = None,
    year: Optional[int] = None,
    sex: Optional[SexEnum] = None,
    age_group: Optional[AgeGroupEnum] = None,
    db: Session = Depends(get_db),
) -> SkinCancerGroupedResponse:
    """Get grouped skin cancer data for visualization.

    Args:
        group_by: Fields to group by
        data_type: Type of data (Actual or Projections)
        year: Year of the data
        sex: Gender category (Females, Males, Persons)
        age_group: Age range in years
        db: Database session

    Returns:
        Grouped skin cancer data for visualization

    Raises:
        HTTPException: If there's an error fetching or grouping the data
    """
    try:
        logger.info(f"Getting skin cancer visualization data grouped by {group_by}")

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

        # Validate group_by fields
        valid_fields = ["data_type", "year", "sex", "age_group"]
        invalid_fields = [field for field in group_by if field not in valid_fields]

        if invalid_fields:
            raise ValueError(f"Invalid group_by fields: {', '.join(invalid_fields)}")

        # Get grouped data
        data = skin_cancer_crud.get_grouped_data(
            db, filters=filters, group_by=group_by, metrics=["count"]
        )

        # Count total records (for reference)
        total = skin_cancer_crud.count_filtered(db, filters=filters)

        return SkinCancerGroupedResponse(data=data, total=total)

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error getting skin cancer visualization data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching skin cancer visualization data",
        )
