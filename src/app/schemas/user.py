"""User schemas module."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema.

    Attributes:
        email: User email.
        is_active: Whether the user is active.
        is_superuser: Whether the user is a superuser.
    """

    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    """User creation schema.

    Attributes:
        email: User email.
        password: User password.
    """

    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(UserBase):
    """User update schema.

    Attributes:
        password: User password.
    """

    password: Optional[str] = Field(None, min_length=8)


class UserInDBBase(UserBase):
    """Base user in DB schema.

    Attributes:
        id: User ID.
    """

    id: int

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserResponse(UserInDBBase):
    """User response schema."""
    pass


class UserInDB(UserInDBBase):
    """User in DB schema.

    Attributes:
        hashed_password: Hashed password.
    """

    hashed_password: str