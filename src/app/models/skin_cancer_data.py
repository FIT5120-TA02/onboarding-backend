"""Skin cancer data model module."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.core.db.base_class import Base, TimestampMixin, UUIDMixin


class SkinCancerData(Base, UUIDMixin, TimestampMixin):
    """Skin cancer data model for storing statistical information.

    Attributes:
        id: Record ID (UUID).
        cancer_group: Type of skin cancer.
        year: Year of the data.
        sex: Gender category (Male, Female, All).
        age_group: Age range in years.
        count: Number of cases.
        age_specific_rate: Rate per 100,000 population.
        created_at: When the record was created.
        updated_at: When the record was last updated.
    """

    __tablename__ = "skin_cancer_data"

    data_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    cancer_group: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    sex: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    age_group: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
