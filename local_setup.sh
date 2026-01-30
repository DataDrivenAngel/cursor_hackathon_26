#!/bin/bash

# Database Setup Script - Initializes database and populates with synthetic test data
# This script sets up the complete database with all required tables and sample data

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect script location and project root
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Change to project root to ensure all paths work
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Database Setup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Project root: ${GREEN}$PROJECT_ROOT${NC}"
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

# Virtual environment directory
VENV_DIR="$PROJECT_ROOT/venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    print_status "Virtual environment created at: $VENV_DIR"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    source "$VENV_DIR/bin/activate"
else
    print_status "Virtual environment already activated: $VIRTUAL_ENV"
fi

# Upgrade pip
python -m pip install --upgrade pip --quiet

# Install requirements
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip install -r "$PROJECT_ROOT/requirements.txt" --quiet
    print_status "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

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

# API Keys
MEETUP_API_KEY=
LUMA_API_KEY=
MINIMAX_API_KEY=
PERPLEXITY_API_KEY=
JIGSAWSTACK_API_KEY=
REPLICATE_API_TOKEN=

# JWT Secret
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

echo ""
echo -e "${BLUE}========================================${NC}"
print_info "Initializing database tables..."
echo -e "${BLUE}========================================${NC}"
echo ""

# Initialize database tables
cd "$PROJECT_ROOT"
python -c "
import asyncio
from app.database.connection import init_db

async def setup_database():
    print('Creating database tables...')
    await init_db()
    print('Database tables created successfully!')

asyncio.run(setup_database())
"

print_status "Database tables initialized"

echo ""
echo -e "${BLUE}========================================${NC}"
print_info "Populating database with synthetic test data..."
echo -e "${BLUE}========================================${NC}"
echo ""

# Run the population script
if [ -f "$PROJECT_ROOT/scripts/populate_test_data.py" ]; then
    python "$PROJECT_ROOT/scripts/populate_test_data.py"
    
    echo ""
    print_status "Database setup completed successfully!"
    echo ""
    echo -e "${YELLOW}Test Credentials:${NC}"
    echo "  - Admin: admin / admin123"
    echo "  - Organizer: organizer1 / organizer123"
    echo "  - Assistant: assistant / assistant123"
    echo ""
else
    print_error "Population script not found at $PROJECT_ROOT/scripts/populate_test_data.py"
    exit 1
fi

deactivate

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "You can now run the application with:"
echo "  ./run.sh"
echo ""
