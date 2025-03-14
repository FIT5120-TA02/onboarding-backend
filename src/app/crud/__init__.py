"""CRUD operations package."""

from src.app.crud.crud_locations import location_crud
from src.app.crud.crud_temperature_records import temperature_record_crud
from src.app.crud.crud_users import user_crud
from src.app.crud.crud_uv_records import uv_record_crud

# For easy imports
__all__ = ["location_crud", "temperature_record_crud", "uv_record_crud", "user_crud"]
