#!/bin/bash

# Create a new Alembic migration
# Usage: ./scripts/create_migration.sh "description"

set -e

if [ -z "$1" ]; then
    echo "❌ Error: Migration description required"
    echo "Usage: ./scripts/create_migration.sh \"description\""
    exit 1
fi

echo "📝 Creating new migration: $1"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create migration
alembic revision --autogenerate -m "$1"

echo "✅ Migration created successfully!"
echo "📋 To apply: alembic upgrade head"

