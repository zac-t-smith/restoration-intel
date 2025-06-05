#!/bin/bash
# run_local.sh - Development script for Restoration-Intel

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "Supabase CLI not found. Please install it from https://supabase.com/docs/guides/cli"
    exit 1
fi

# Start Supabase local development
echo "Starting Supabase local development..."
supabase start

# Push database migrations
echo "Applying database migrations..."
supabase db push

# Apply seed data if --seed flag is provided
if [ "$1" == "--seed" ]; then
    echo "Applying seed data..."
    psql $(supabase db connection-string) -f db/seed/seed.sql
fi

# Start FastAPI server in background
echo "Starting FastAPI server..."
cd api/py
uvicorn app:app --reload --port 8000 &
FASTAPI_PID=$!
cd ../..

# Start Next.js development server
echo "Starting Next.js development server..."
npm run dev

# Trap SIGINT to kill background processes when script is terminated
trap "kill $FASTAPI_PID; supabase stop" INT