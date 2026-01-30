#!/bin/bash

# Meetup Organizing Information Support System - Local Development Runner
# This script sets up and runs the application locally for testing

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Meetup Organizing System - Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Check Python version
print_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
print_status "Python $PYTHON_VERSION found"

# Create virtual environment if it doesn't exist
VENV_DIR="$PROJECT_ROOT/venv"
if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    print_status "Virtual environment created at: $VENV_DIR"
else
    print_status "Virtual environment already exists"
fi

# Activate install dependencies
print_info "Installing dependencies..."
source "$VENV_DIR/bin/activate"

# Upgrade pip first
python -m pip install --upgrade pip --quiet

# Install requirements
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip install -r "$PROJECT_ROOT/requirements.txt" --quiet
    print_status "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

deactivate

# Create necessary directories
print_info "Creating data directory..."
mkdir -p "$PROJECT_ROOT/data"
mkdir -p "$PROJECT_ROOT/static"
print_status "Directories created"

# Create .env file if it doesn't exist
ENV_FILE="$PROJECT_ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
    print_info "Creating .env file with default settings..."
    cat > "$ENV_FILE" << 'EOF'
# Meetup Organizing Information Support System - Environment Variables
# Copy this file and modify for your needs

# API Keys (get these from respective services)
MEETUP_API_KEY=
LUMA_API_KEY=
MINIMAX_API_KEY=
PERPLEXITY_API_KEY=

# JWT Secret (change this in production!)
JWT_SECRET_KEY=dev-secret-key-change-in-production

# Database path
DATABASE_PATH=data/meetup.db

# Application settings
APP_TITLE=Meetup Organizing Information Support System
APP_VERSION=1.0.0
EOF
    print_status ".env file created with default settings"
else
    print_status ".env file already exists"
fi

# Run the application
echo ""
echo -e "${BLUE}========================================${NC}"
print_info "Starting the application..."
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "The application will be available at: ${GREEN}http://localhost:8000${NC}"
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop the server"
echo ""

# Activate virtual environment and run
source "$VENV_DIR/bin/activate"
cd "$PROJECT_ROOT"

# Function to open browser (cross-platform)
open_browser() {
    python3 -c "
import webbrowser
import time
import sys

# Wait a moment for server to start
time.sleep(2)

# Open the browser
success = webbrowser.open('http://localhost:8000')
if success:
    print('Browser opened successfully!')
else:
    print('Could not open browser automatically. Please open http://localhost:8000 manually.')
    sys.exit(0)
" &
}

# Open browser in background
print_info "Opening browser..."
open_browser

# Run with uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
