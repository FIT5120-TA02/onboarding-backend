"""UV record CRUD operations module."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.crud.base import CRUDBase
from src.app.models.uv_record import UVRecord


class UVRecordCRUD(CRUDBase[UVRecord, dict, dict]):
    """CRUD operations for UVRecord model."""
    def get_uv_records(self, db: Session):
        """Get all historical UV index records"""
        return db.execute(select(UVRecord).order_by(UVRecord.created_at.asc())).scalars().all()

    def get_by_location_id(self, db: Session, *, location_id: str) -> List[UVRecord]:
        """Get UV records by location ID.

        Args:
            db: Database session.
            location_id: Location ID.

        Returns:
            List of UV records.
        """
        result = db.execute(
            select(self.model).where(self.model.location_id == location_id)
        )
        return result.scalars().all()

    def create_from_weather_data(
        self, db: Session, *, weather_data: dict, location_id: str
    ) -> UVRecord:
        """Create a new UV record from weather data.

        Args:
            db: Database session.
            weather_data: Weather data from OpenWeatherMap API.
            location_id: Location ID.

        Returns:
            Created UV record.
        """
        current = weather_data.get("current", {})
        
        db_obj = UVRecord(
            uv_index=current.get("uvi"),
            clouds=current.get("clouds"),
            visibility=current.get("visibility"),
            location_id=location_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create a singleton instance
uv_record_crud = UVRecordCRUD(UVRecord)