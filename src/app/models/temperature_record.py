"""Temperature record model module."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db.base_class import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.app.models.location import Location


class TemperatureRecord(Base, UUIDMixin, TimestampMixin):
    """Temperature record model for storing temperature data.

    Attributes:
        id: Temperature record ID (UUID).
        temperature: Temperature in Celsius.
        feels_like: Perceived temperature in Celsius.
        humidity: Humidity percentage.
        pressure: Atmospheric pressure in hPa.
        wind_speed: Wind speed in m/s.
        location_id: ID of the location this record belongs to.
        created_at: When the record was created.
        updated_at: When the record was last updated.
    """

    __tablename__ = "temperature_records"

    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    feels_like: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pressure: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Foreign keys
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"), nullable=False)

    # Relationships
    location: Mapped["Location"] = relationship(
        "Location", back_populates="temperature_records"
    )
