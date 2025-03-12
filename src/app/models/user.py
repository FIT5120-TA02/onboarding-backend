"""User model module."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.db.base_class import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User model for authentication and profile information.

    Attributes:
        id: User ID (UUID).
        email: User email.
        hashed_password: Hashed password.
        is_active: Whether the user is active.
        is_superuser: Whether the user is a superuser.
        created_at: When the user was created.
        updated_at: When the user was last updated.
    """

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Example relationship
    # items: Mapped[List["Item"]] = relationship("Item", back_populates="owner")
