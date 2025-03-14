"""User CRUD operations module."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.crud.base import CRUDBase
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""

    def get_by_name(self, db: Session, *, name: str) -> Optional[User]:
        """Get a user by name.

        Args:
            db: Database session.
            name: User's name.

        Returns:
            User if found, None otherwise.
        """
        result = db.execute(select(self.model).where(self.model.name == name))
        return result.scalars().first()

    def get_or_create(self, db: Session, *, name: str) -> User:
        """Get a user by name or create a new one if not found.

        Args:
            db: Database session.
            name: User's name.

        Returns:
            User object.
        """
        user = self.get_by_name(db, name=name)
        if not user:
            # Generate a username from the name (lowercase, no spaces)
            username = name.lower().replace(" ", "_")

            # Check if username exists, append a number if it does
            base_username = username
            counter = 1
            while (
                db.execute(select(self.model).where(self.model.username == username))
                .scalars()
                .first()
            ):
                username = f"{base_username}_{counter}"
                counter += 1

            # Create a new user
            user = User(name=name, username=username)
            db.add(user)
            db.commit()
            db.refresh(user)

        return user


# Create a singleton instance
user_crud = UserCRUD(User)
