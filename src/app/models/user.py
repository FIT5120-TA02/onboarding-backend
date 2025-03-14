"""User model module."""

from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db.base_class import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.app.models.location import Location


class User(Base, UUIDMixin, TimestampMixin):
    """User model for storing visitor information.

    Attributes:
        id: User ID (UUID).
        name: User's full name.
        username: Unique username for the user.
        created_at: When the user was created.
        updated_at: When the user was last updated.
    """

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    # Relationships
    locations: Mapped[List["Location"]] = relationship(
        "Location", back_populates="user", cascade="all, delete-orphan"
    )
