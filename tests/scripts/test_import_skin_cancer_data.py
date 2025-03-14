"""Tests for the skin cancer data import script."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.python.import_skin_cancer_data import import_skin_cancer_data
from src.app.models.skin_cancer_data import SkinCancerData


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_db_manager(mock_session):
    """Create a mock database manager."""
    with patch(
        "scripts.import_skin_cancer_data.DatabaseSessionManager"
    ) as mock_db_manager_class:
        db_manager = mock_db_manager_class.return_value
        db_manager.initialize.return_value = True
        db_manager.session.return_value.__enter__.return_value = mock_session
        yield db_manager


@pytest.fixture
def mock_csv_file():
    """Create a mock CSV file."""
    csv_content = """Data type,Cancer group/site,Year,Sex,Age group (years),Count
Actual,Melanoma of the skin,2020,Males,'00-04,0
Actual,Melanoma of the skin,2020,Males,'05-09,1
Actual,Melanoma of the skin,2020,Females,'00-04,2
"""
    csv_path = (
        Path(__file__).resolve().parent.parent.parent
        / "src"
        / "app"
        / "data"
        / "skin_cancer_data.csv"
    )

    # Ensure the directory exists
    os.makedirs(csv_path.parent, exist_ok=True)

    # Create a temporary CSV file for testing
    with open(csv_path, "w") as f:
        f.write(csv_content)

    yield csv_path

    # Clean up - remove the file after the test
    if csv_path.exists():
        os.remove(csv_path)


@patch("scripts.import_skin_cancer_data.logger")
def test_import_skin_cancer_data(
    mock_logger, mock_db_manager, mock_session, mock_csv_file
):
    """Test the import_skin_cancer_data function."""
    # Set up mock query and delete
    mock_query = mock_session.query.return_value
    mock_query.delete.return_value = None

    # Call the function
    import_skin_cancer_data()

    # Verify the database was initialized
    mock_db_manager.initialize.assert_called_once()

    # Verify existing data was deleted
    mock_session.query.assert_called_with(SkinCancerData)
    mock_query.delete.assert_called_once()

    # Verify new data was added
    assert mock_session.add_all.call_count == 1

    # Get the batch of records that was added
    added_records = mock_session.add_all.call_args[0][0]

    # Verify the correct number of records was added
    assert len(added_records) == 3

    # Verify the records have the correct data
    assert added_records[0].data_type == "Actual"
    assert added_records[0].cancer_group == "Melanoma of the skin"
    assert added_records[0].year == 2020
    assert added_records[0].sex == "Males"
    assert added_records[0].age_group == "'00-04"
    assert added_records[0].count == 0

    # Verify commit was called
    assert mock_session.commit.call_count >= 2  # Once for delete, at least once for add

    # Verify success message was logged
    mock_logger.info.assert_any_call("Successfully imported 3 records")
