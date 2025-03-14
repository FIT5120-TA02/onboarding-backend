"""Database models package."""

from src.app.models.location import Location
from src.app.models.skin_cancer_data import SkinCancerData
from src.app.models.temperature_record import TemperatureRecord
from src.app.models.user import User
from src.app.models.uv_record import UVRecord

# For Alembic to detect models
__all__ = [
    "User",
    "Location",
    "TemperatureRecord",
    "UVRecord",
    "SkinCancerData",
]
