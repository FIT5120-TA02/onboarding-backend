"""CRUD operations package."""

from src.app.crud.crud_skin_cancer import skin_cancer_crud
from src.app.crud.crud_users import user_crud

# For easy imports
__all__ = ["user_crud", "skin_cancer_crud"]
