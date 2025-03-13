"""UV record model module."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db.base_class import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.app.models.location import Location


class UVRecord(Base, UUIDMixin, TimestampMixin):
    """UV record model for storing UV index data.

    Attributes:
        id: UV record ID (UUID).
        uv_index: UV index value.
        clouds: Cloud coverage percentage.
        visibility: Visibility in meters.
        location_id: ID of the location this record belongs to.
        created_at: When the record was created.
        updated_at: When the record was last updated.
    """

    __tablename__ = "uv_records"

    uv_index: Mapped[float] = mapped_column(Float, nullable=False)
    clouds: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # Cloud coverage in percentage
    visibility: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # Visibility in meters

    # Foreign keys
    location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"), nullable=False)

    # Relationships
    location: Mapped["Location"] = relationship("Location", back_populates="uv_records")
