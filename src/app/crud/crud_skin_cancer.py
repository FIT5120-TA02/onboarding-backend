"""CRUD operations for skin cancer data."""

from typing import Dict, List, Optional, Union

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from src.app.crud.base import CRUDBase
from src.app.models.skin_cancer_data import SkinCancerData
from src.app.schemas.skin_cancer import SkinCancerFilter


class CRUDSkinCancer(CRUDBase[SkinCancerData, None, None]):
    """CRUD operations for skin cancer data."""

    def get_filtered(
        self, db: Session, *, filters: SkinCancerFilter, skip: int = 0, limit: int = 100
    ) -> List[SkinCancerData]:
        """Get filtered skin cancer data.

        Args:
            db: Database session.
            filters: Filter criteria.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of skin cancer data records matching the filter criteria.
        """
        query = select(self.model)
        query = self._apply_filters(query, filters)
        query = query.offset(skip).limit(limit)
        result = db.execute(query)
        return result.scalars().all()

    def count_filtered(self, db: Session, *, filters: SkinCancerFilter) -> int:
        """Count filtered skin cancer data.

        Args:
            db: Database session.
            filters: Filter criteria.

        Returns:
            Count of records matching the filter criteria.
        """
        query = select(func.count()).select_from(self.model)
        query = self._apply_filters(query, filters)
        result = db.execute(query)
        return result.scalar_one()

    def get_grouped_data(
        self,
        db: Session,
        *,
        filters: SkinCancerFilter,
        group_by: List[str],
        metrics: List[str] = ["count"],
    ) -> Dict:
        """Get grouped skin cancer data for visualization.

        Args:
            db: Database session.
            filters: Filter criteria.
            group_by: Fields to group by.
            metrics: Metrics to aggregate.

        Returns:
            Grouped data for visualization.
        """
        # Validate group_by fields
        valid_fields = [
            "data_type",
            "year",
            "sex",
            "age_group",
        ]
        group_by = [field for field in group_by if field in valid_fields]

        if not group_by:
            raise ValueError("At least one valid field must be specified for grouping")

        # Build select columns
        select_columns = []
        for field in group_by:
            select_columns.append(getattr(self.model, field))

        # Add metrics
        for metric in metrics:
            if metric == "count":
                select_columns.append(func.sum(self.model.count).label("count"))

        # Build query
        query = select(*select_columns)
        query = self._apply_filters(query, filters)
        query = query.group_by(*[getattr(self.model, field) for field in group_by])

        # Execute query
        result = db.execute(query)
        rows = result.all()

        # Format result for visualization
        formatted_data = self._format_grouped_data(rows, group_by, metrics)
        return formatted_data

    def _apply_filters(self, query, filters: SkinCancerFilter):
        """Apply filters to query.

        Args:
            query: SQLAlchemy query.
            filters: Filter criteria.

        Returns:
            Filtered query.
        """
        filter_conditions = []

        # Always filter by cancer_group = "Melanoma of the skin"
        filter_conditions.append(self.model.cancer_group == "Melanoma of the skin")

        if filters.data_type:
            filter_conditions.append(self.model.data_type == filters.data_type)
        if filters.year:
            filter_conditions.append(self.model.year == filters.year)
        if filters.sex:
            filter_conditions.append(self.model.sex == filters.sex)
        if filters.age_group:
            filter_conditions.append(self.model.age_group == filters.age_group)

        if filter_conditions:
            query = query.where(and_(*filter_conditions))

        return query

    def _format_grouped_data(
        self, rows: List, group_by: List[str], metrics: List[str]
    ) -> Dict:
        """Format grouped data for visualization.

        Args:
            rows: Query result rows.
            group_by: Fields used for grouping.
            metrics: Metrics aggregated.

        Returns:
            Formatted data for visualization.
        """
        result = {}

        # Handle different grouping scenarios
        if len(group_by) == 1:
            # Simple grouping by one field
            field = group_by[0]
            result[field] = {}

            for row in rows:
                key = getattr(row, field)
                result[field][key] = {}

                for metric in metrics:
                    result[field][key][metric] = getattr(row, metric)

        elif len(group_by) == 2:
            # Two-dimensional grouping (e.g., year and sex)
            field1, field2 = group_by
            result[f"{field1}_{field2}"] = {}

            for row in rows:
                key1 = getattr(row, field1)
                key2 = getattr(row, field2)

                if key1 not in result[f"{field1}_{field2}"]:
                    result[f"{field1}_{field2}"][key1] = {}

                result[f"{field1}_{field2}"][key1][key2] = {}

                for metric in metrics:
                    result[f"{field1}_{field2}"][key1][key2][metric] = getattr(
                        row, metric
                    )
        else:
            # Multi-dimensional grouping - convert to nested structure
            result["data"] = []

            for row in rows:
                item = {}

                for field in group_by:
                    item[field] = getattr(row, field)

                for metric in metrics:
                    item[metric] = getattr(row, metric)

                result["data"].append(item)

        return result


skin_cancer_crud = CRUDSkinCancer(SkinCancerData)
