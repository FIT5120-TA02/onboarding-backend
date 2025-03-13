"""Location model module."""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db.base_class import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.app.models.temperature_record import TemperatureRecord
    from src.app.models.user import User
    from src.app.models.uv_record import UVRecord


class Location(Base, UUIDMixin, TimestampMixin):
    """Location model for storing geographical locations.

    Attributes:
        id: Location ID (UUID).
        latitude: Geographical latitude.
        longitude: Geographical longitude.
        state: State or region name.
        postcode: Postal code.
        city: City or locality name.
        country: Country name.
        user_id: ID of the user who created this location.
        created_at: When the location was created.
        updated_at: When the location was last updated.
    """

    __tablename__ = "locations"

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postcode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Foreign keys
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="locations")
    temperature_records: Mapped[List["TemperatureRecord"]] = relationship(
        "TemperatureRecord", back_populates="location", cascade="all, delete-orphan"
    )
    uv_records: Mapped[List["UVRecord"]] = relationship(
        "UVRecord", back_populates="location", cascade="all, delete-orphan"
    )
