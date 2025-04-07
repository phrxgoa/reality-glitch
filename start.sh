#!/bin/bash

# --- Store the PID of the background scheduler ---
scheduler_pid=""

# Function to clean up Docker containers AND the scheduler
cleanup() {
    echo "Cleaning up..."

    # Stop the background scheduler process if its PID was stored
    if [ ! -z "$scheduler_pid" ]; then
        echo "Stopping scheduler (PID: $scheduler_pid)..."
        # Send SIGTERM first (graceful shutdown), then SIGKILL if needed
        kill $scheduler_pid 2>/dev/null || kill -9 $scheduler_pid 2>/dev/null
    fi

    echo "Stopping Docker containers..."
    # Use docker compose down with timeout, ignore errors if already stopped
    docker compose down --timeout 10 2>/dev/null || true

    echo "Cleanup finished."
    exit 0
}

# Set up error handling and cleanup on exit/interrupt signals
set -e
trap cleanup SIGINT SIGTERM EXIT # EXIT trap ensures cleanup runs even if game finishes normally

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if virtual environment exists, if not create it
if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source env/bin/activate

# Install requirements if needed
# (Consider running this less often once installed, maybe check requirements.txt timestamp?)
if [ ! -f "env/.requirements_installed" ] || [ "requirements.txt" -nt "env/.requirements_installed" ]; then
    echo "Installing/updating requirements..."
    pip install -r requirements.txt
    touch env/.requirements_installed
fi

# Build and start Docker containers
echo "Building and starting Docker containers..."
docker compose build --no-cache && docker compose up -d --remove-orphans

# --- Run the scheduler in the background ---
echo "Starting the scheduler in the background..."
python app/integration/api_scheduler.py &

# --- Capture the PID of the background scheduler ---
scheduler_pid=$!
echo "Scheduler started with PID: $scheduler_pid"

# Allow a moment for scheduler to start
sleep 2

# Run the game in the foreground
echo "Starting the game..."
python app/game.py