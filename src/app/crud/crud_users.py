"""User CRUD operations module."""

from src.app.crud.base import CRUDBase
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""


# Create a singleton instance
user_crud = UserCRUD(User)
