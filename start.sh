#!/bin/bash
# Function to clean up Docker containers
cleanup() {
    echo "Stopping Docker containers..."
    docker compose down
    exit 0
}

# Set up error handling
set -e
trap cleanup SIGINT SIGTERM EXIT

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
if [ ! -f "env/.requirements_installed" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    touch env/.requirements_installed
fi

# Build and start Docker containers
echo "Building and starting Docker containers..."
docker compose build --no-cache && docker compose up -d

# Run the game
echo "Starting the game..."
python app/game.py
