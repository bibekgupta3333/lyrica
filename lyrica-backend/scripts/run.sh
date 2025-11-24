#!/bin/bash

# Lyrica Backend Run Script

set -e

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application
echo "🚀 Starting Lyrica Backend..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info

