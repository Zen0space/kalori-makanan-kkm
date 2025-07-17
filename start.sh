#!/bin/bash

# Startup script for Kalori Makanan API on Render

# Exit on any error
set -e

echo "🚀 Starting Kalori Makanan API..."

# Check if required environment variables are set
if [ -z "$TURSO_DATABASE_URL" ]; then
    echo "❌ Error: TURSO_DATABASE_URL environment variable is not set"
    exit 1
fi

if [ -z "$TURSO_DATABASE_TOKEN" ]; then
    echo "❌ Error: TURSO_DATABASE_TOKEN environment variable is not set"
    exit 1
fi

# Set default port if not provided
PORT=${PORT:-8000}

echo "✅ Environment variables verified"
echo "📡 Starting API server on port $PORT..."

# Start the FastAPI application with uvicorn
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --access-log \
    --no-use-colors
