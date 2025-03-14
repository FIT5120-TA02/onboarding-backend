#!/bin/bash
# Script to import skin cancer data into the database
# This script can be run in any environment (local, dev, prod)
# Usage: ./scripts/shell/import_skin_cancer_data.sh [env]
#   env: Environment to use (local, dev, prod). Defaults to local.

# Exit on error
set -e

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Parse command line arguments
ENV=${1:-local}  # Default to local if no argument provided

# Validate environment argument
if [[ "$ENV" != "local" && "$ENV" != "dev" && "$ENV" != "prod" ]]; then
    echo "Error: Invalid environment. Must be one of: local, dev, prod"
    echo "Usage: ./scripts/shell/import_skin_cancer_data.sh [env]"
    exit 1
fi

echo "Using $ENV environment..."

# Export the environment variable for the Python script
export ENV="$ENV"

# Set environment variables based on the selected environment
if [[ "$ENV" == "local" ]]; then
    # Use local environment variables if .env file exists
    if [ -f "$PROJECT_ROOT/.env" ]; then
        echo "Loading environment variables from .env file..."
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
    else
        echo "Warning: .env file not found. Using default environment variables."
    fi
elif [[ "$ENV" == "dev" ]]; then
    # Use dev environment variables if .env.dev file exists
    if [ -f "$PROJECT_ROOT/.env.dev" ]; then
        echo "Loading environment variables from .env.dev file..."
        export $(grep -v '^#' "$PROJECT_ROOT/.env.dev" | xargs)
    else
        echo "Warning: .env.dev file not found. Using default environment variables."
    fi
elif [[ "$ENV" == "prod" ]]; then
    # Use prod environment variables if .env.prod file exists
    if [ -f "$PROJECT_ROOT/.env.prod" ]; then
        echo "Loading environment variables from .env.prod file..."
        export $(grep -v '^#' "$PROJECT_ROOT/.env.prod" | xargs)
    else
        echo "Warning: .env.prod file not found. Using default environment variables."
    fi
fi

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -d "$PROJECT_ROOT/env" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_ROOT/env/bin/activate"
fi

# Change to project root directory
cd "$PROJECT_ROOT"

# Run the import script
echo "Importing skin cancer data..."
python -m scripts.python.import_skin_cancer_data

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating virtual environment..."
    deactivate
fi

echo "Import completed successfully in $ENV environment!" 