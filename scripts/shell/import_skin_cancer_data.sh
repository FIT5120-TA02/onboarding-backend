#!/bin/bash
# Script to import skin cancer data into the database
# This script can be run in any environment (local, dev, prod)
# Usage: ./scripts/shell/import_skin_cancer_data.sh [env]
#   env: Environment to use (local, dev, prod). Defaults to local.

# Exit on error
set -e

# Default to local environment if not specified
ENV=${1:-local}

# Validate environment parameter
if [ "$ENV" != "local" ] && [ "$ENV" != "dev" ]; then
    echo "Error: Environment must be either 'local' or 'dev'"
    echo "Usage: $0 [local|dev]"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set environment variables based on selected environment
export ENVIRONMENT=$ENV
export ENV_FILE=./env/$ENV.env

# Load environment variables from the env file
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment from $ENV_FILE"
    export $(grep -v '^#' $ENV_FILE | xargs)
else
    echo "Error: Environment file $ENV_FILE not found"
    exit 1
fi

# Add the project root to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the import script
echo "Importing skin cancer data..."
python -m scripts.python.import_skin_cancer_data

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating virtual environment..."
    deactivate
fi

echo "Import completed successfully in $ENV environment!" 