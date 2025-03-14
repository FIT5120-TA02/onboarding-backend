"""Location CRUD operations module."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.crud.base import CRUDBase
from src.app.models.location import Location
from src.app.schemas.weather import LocationInfo


class LocationCRUD(CRUDBase[Location, LocationInfo, LocationInfo]):
    """CRUD operations for Location model."""

    def get_by_coordinates(
        self, db: Session, *, latitude: float, longitude: float
    ) -> Optional[Location]:
        """Get a location by coordinates.

        Args:
            db: Database session.
            latitude: Latitude of the location.
            longitude: Longitude of the location.

        Returns:
            Location if found, None otherwise.
        """
        result = db.execute(
            select(self.model).where(
                self.model.latitude == latitude, self.model.longitude == longitude
            )
        )
        return result.scalars().first()

    def get_by_user_id(self, db: Session, *, user_id: str) -> List[Location]:
        """Get locations by user ID.

        Args:
            db: Database session.
            user_id: User ID.

        Returns:
            List of locations.
        """
        result = db.execute(select(self.model).where(self.model.user_id == user_id))
        return result.scalars().all()

    def create_with_user(
        self, db: Session, *, obj_in: dict, user_id: str
    ) -> Location:
        """Create a new location with user ID.

        Args:
            db: Database session.
            obj_in: Input data.
            user_id: User ID.

        Returns:
            Created location.
        """
        db_obj = Location(
            latitude=obj_in["lat"],
            longitude=obj_in["lon"],
            city=obj_in.get("city"),
            state=None,  # Not provided in the current API response
            postcode=None,  # Not provided in the current API response
            country=obj_in.get("country"),
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create a singleton instance
location_crud = LocationCRUD(Location)