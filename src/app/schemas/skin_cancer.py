"""Skin cancer data schemas."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DataTypeEnum(str, Enum):
    """Data type enumeration."""

    ACTUAL = "Actual"
    PROJECTIONS = "Projections"


class SexEnum(str, Enum):
    """Sex enumeration."""

    FEMALES = "Females"
    MALES = "Males"
    PERSONS = "Persons"


class AgeGroupEnum(str, Enum):
    """Age group enumeration."""

    AGE_00_04 = "00-04"
    AGE_05_09 = "05-09"
    AGE_10_14 = "10-14"
    AGE_15_19 = "15-19"
    AGE_20_24 = "20-24"
    AGE_25_29 = "25-29"
    AGE_30_34 = "30-34"
    AGE_35_39 = "35-39"
    AGE_40_44 = "40-44"
    AGE_45_49 = "45-49"
    AGE_50_54 = "50-54"
    AGE_55_59 = "55-59"
    AGE_60_64 = "60-64"
    AGE_65_69 = "65-69"
    AGE_70_74 = "70-74"
    AGE_75_79 = "75-79"
    AGE_80_84 = "80-84"
    AGE_85_89 = "85-89"
    AGE_90_PLUS = "90+"
    ALL_AGES = "All ages combined"


class SkinCancerFilter(BaseModel):
    """Filter parameters for skin cancer data queries.

    Attributes:
        data_type: Type of data (Actual or Projections)
        year: Year of the data
        sex: Gender category (Females, Males, Persons)
        age_group: Age range in years
    """

    data_type: Optional[DataTypeEnum] = None
    year: Optional[int] = None
    sex: Optional[SexEnum] = None
    age_group: Optional[AgeGroupEnum] = None


class SkinCancerData(BaseModel):
    """Skin cancer data model.

    Attributes:
        id: Record ID (UUID)
        data_type: Type of data (Actual or Projections)
        cancer_group: Type of skin cancer (always "Melanoma of the skin")
        year: Year of the data
        sex: Gender category (Females, Males, Persons)
        age_group: Age range in years
        count: Number of cases
        age_specific_rate: Rate per 100,000 population (if available)
    """

    id: str
    data_type: str
    cancer_group: str = "Melanoma of the skin"
    year: int
    sex: str
    age_group: str
    count: int
    age_specific_rate: Optional[float] = None

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class SkinCancerDataResponse(BaseModel):
    """Response model for skin cancer data.

    Attributes:
        data: List of skin cancer data records
        total: Total number of records matching the filter
    """

    data: List[SkinCancerData]
    total: int = Field(..., description="Total number of records matching the filter")
