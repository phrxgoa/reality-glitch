#!/bin/bash

# --- Colors and formatting ---
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Store the PID of the background scheduler ---
scheduler_pid=""

# Function to clean up Docker containers AND the scheduler
cleanup() {
    tput cnorm # Restore cursor
    echo -e "${CYAN}Reality coherence restored. Synchronization complete.${NC}" > /dev/tty
    
    # Stop the background scheduler process if its PID was stored
    if [ ! -z "$scheduler_pid" ]; then
        kill $scheduler_pid 2>/dev/null || kill -9 $scheduler_pid 2>/dev/null
    fi

    # Stop Docker containers silently
    docker compose down --timeout 10 > /dev/null 2>&1 || true
    
    exit 0
}

# Set up error handling and cleanup on exit/interrupt signals
set -e
trap cleanup SIGINT SIGTERM EXIT

# --- Main script execution ---

# Check if Docker is running (without visible output)
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}" > /dev/tty
    exit 1
fi

# Create virtual environment silently
if [ ! -d "env" ]; then
    python3 -m venv env > /dev/null 2>&1
fi

# Activate virtual environment
source env/bin/activate

# Install requirements if needed (silently)
if [ ! -f "env/.requirements_installed" ] || [ "requirements.txt" -nt "env/.requirements_installed" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    touch env/.requirements_installed
fi

# Build and start Docker containers silently
docker compose build --no-cache > /dev/null 2>&1 && docker compose up -d --remove-orphans > /dev/null 2>&1

# --- Run the scheduler in the background ---
python app/integration/api_scheduler.py > /dev/null 2>&1 &
scheduler_pid=$!

# Set the Python path to include the project root
export PYTHONPATH=$(pwd)

# Check if debug mode was requested
if [ "$1" = "--debug" ]; then
    echo "Starting Reality Glitch in debug mode..."
    python app/game.py --debug
else
    echo "Starting Reality Glitch..."
    python app/game.py
fi