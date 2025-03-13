"""User CRUD operations module."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.crud.base import CRUDBase
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get a user by email.

        Args:
            db: Database session.
            email: User email.

        Returns:
            User if found, None otherwise.
        """
        result = db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create a new user.

        Args:
            db: Database session.
            obj_in: Input data.

        Returns:
            Created user.
        """
        # In a real application, you would hash the password here
        # For example: hashed_password = get_password_hash(obj_in.password)
        hashed_password = obj_in.password  # This is just for demonstration

        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create a singleton instance
user_crud = UserCRUD(User)
