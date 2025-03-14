#!/bin/bash

# Exit on error
set -e

# Activate virtual environment
source venv/bin/activate

# Run the application
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000