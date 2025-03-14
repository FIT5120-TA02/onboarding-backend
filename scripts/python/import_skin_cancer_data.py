#!/usr/bin/env python3
"""
Script to import skin cancer data from CSV into the database.

This script will:
1. Drop all existing data from the skin_cancer_data table
2. Import data from the CSV file into the table
3. Work in any environment (local, dev, prod)

Usage:
    python -m scripts.python.import_skin_cancer_data
"""
import csv
import os
import sys
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from src.app.core.config import settings
from src.app.core.db.session import DatabaseSessionManager
from src.app.core.logger import get_logger
from src.app.models.skin_cancer_data import SkinCancerData

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Configure logging
logger = get_logger(__name__)


def import_skin_cancer_data():
    """Import skin cancer data from CSV into the database."""
    # Log the environment
    env = os.environ.get("ENV", "local")
    logger.info(f"Running in {env} environment")
    logger.info(f"Using database: {settings.DATABASE_URL}")

    # Initialize database connection
    db_manager = DatabaseSessionManager()
    if not db_manager.initialize():
        logger.error("Failed to initialize database connection")
        sys.exit(1)

    # Path to the CSV file
    csv_path = (
        Path(__file__).resolve().parent.parent.parent
        / "src"
        / "app"
        / "data"
        / "skin_cancer_data.csv"
    )

    if not csv_path.exists():
        logger.error(f"CSV file not found at {csv_path}")
        sys.exit(1)

    logger.info(f"Importing skin cancer data from {csv_path}")

    try:
        with db_manager.session() as session:
            # Delete existing data
            logger.info("Deleting existing skin cancer data...")
            session.query(SkinCancerData).delete()
            session.commit()
            logger.info("Existing data deleted successfully")

            # Read and import data from CSV
            logger.info("Importing new data from CSV...")
            records_imported = 0

            with open(csv_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                # Process in batches for better performance
                batch_size = 1000
                batch = []

                for row in reader:
                    # Skip rows with missing required data
                    if not all(
                        key in row and row[key]
                        for key in [
                            "Data type",
                            "Cancer group/site",
                            "Year",
                            "Sex",
                            "Age group (years)",
                            "Count",
                        ]
                    ):
                        logger.warning(f"Skipping row with missing data: {row}")
                        continue

                    # Clean and convert data
                    try:
                        # Handle the case where Count might be 'np' (not provided) or other non-numeric values
                        count_value = row["Count"]
                        if count_value.isdigit():
                            count = int(count_value)
                        else:
                            logger.warning(
                                f"Skipping row with non-numeric count: {row}"
                            )
                            continue

                        cleaned_age_group = row["Age group (years)"].replace("'", "")

                        # Create a new record
                        record = SkinCancerData(
                            data_type=row["Data type"],
                            cancer_group=row["Cancer group/site"],
                            year=int(row["Year"]),
                            sex=row["Sex"],
                            age_group=cleaned_age_group,
                            count=count,
                        )

                        batch.append(record)
                        records_imported += 1

                        # Insert batch when it reaches the batch size
                        if len(batch) >= batch_size:
                            session.add_all(batch)
                            session.commit()
                            logger.info(
                                f"Imported {records_imported} records so far..."
                            )
                            batch = []

                    except (ValueError, KeyError) as e:
                        logger.error(f"Error processing row {row}: {str(e)}")
                        continue

                # Insert any remaining records
                if batch:
                    session.add_all(batch)
                    session.commit()

            logger.info(f"Successfully imported {records_imported} records")

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    import_skin_cancer_data()
