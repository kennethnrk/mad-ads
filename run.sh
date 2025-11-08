#!/bin/bash
# Simple script to run the FastAPI application

# Activate virtual environment
source venv/bin/activate

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

