"""Temperature record CRUD operations module."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.crud.base import CRUDBase
from src.app.models.temperature_record import TemperatureRecord


class TemperatureRecordCRUD(CRUDBase[TemperatureRecord, dict, dict]):
    """CRUD operations for TemperatureRecord model."""

    def get_temperature_records(self, db: Session):
        """Getting historical temperature data"""
        return db.execute(select(TemperatureRecord).order_by(TemperatureRecord.created_at.asc())).scalars().all()

    def get_by_location_id(
        self, db: Session, *, location_id: str
    ) -> List[TemperatureRecord]:
        """Get temperature records by location ID.

        Args:
            db: Database session.
            location_id: Location ID.

        Returns:
            List of temperature records.
        """
        result = db.execute(
            select(self.model).where(self.model.location_id == location_id)
        )
        return result.scalars().all()

    def create_from_weather_data(
        self, db: Session, *, weather_data: dict, location_id: str
    ) -> TemperatureRecord:
        """Create a new temperature record from weather data.

        Args:
            db: Database session.
            weather_data: Weather data from OpenWeatherMap API.
            location_id: Location ID.

        Returns:
            Created temperature record.
        """
        current = weather_data.get("current", {})
        
        db_obj = TemperatureRecord(
            temperature=current.get("temp"),
            feels_like=current.get("feels_like"),
            humidity=current.get("humidity"),
            pressure=current.get("pressure"),
            wind_speed=current.get("wind_speed"),
            location_id=location_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create a singleton instance
temperature_record_crud = TemperatureRecordCRUD(TemperatureRecord)