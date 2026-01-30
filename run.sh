#!/bin/bash

# Meetup Organizing Information Support System - Local Development Runner
# This script sets up and runs the application locally for testing
# Can be called from any directory within the repo

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect script location and project root
# This works even when called from subdirectories
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Change to project root to ensure all paths work
cd "$PROJECT_ROOT"

# Parse command line arguments
POPULATE_DATA=false
RUN_SERVER=true
RUN_SETUP=false
RUN_FRONTEND=true

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--populate-data)
            POPULATE_DATA=true
            RUN_SERVER=false
            RUN_FRONTEND=false
            shift
            ;;
        -s|--setup)
            RUN_SETUP=true
            RUN_SERVER=true
            RUN_FRONTEND=true
            shift
            ;;
        --no-populate)
            RUN_SERVER=true
            POPULATE_DATA=false
            shift
            ;;
        --no-frontend)
            RUN_FRONTEND=false
            shift
            ;;
        --backend-only)
            RUN_FRONTEND=false
            shift
            ;;
        -h|--help)
            echo "Usage: ./run.sh [OPTIONS]"
            echo ""
            echo "This script can be run from any directory within the project."
            echo ""
            echo "Options:"
            echo "  -p, --populate-data    Populate database with test data and exit"
            echo "  -s, --setup            Run database setup then start servers"
            echo "      --no-populate      Run servers without populating data (default)"
            echo "      --no-frontend      Run only the backend server"
            echo "      --backend-only     Run only the backend server (same as --no-frontend)"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run.sh                           Run both servers with browser"
            echo "  ./run.sh -s                        Setup database then run servers"
            echo "  ./run.sh --no-frontend             Run only backend server"
            echo "  ./run.sh -p                        Populate test data and exit"
            echo "  cd subdir && ../run.sh               Run from subdirectory"
            exit 0
            ;;
        *)
            echo -e "${RED}[✗]${NC} Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Meetup Organizing System - Runner${NC}"
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

# Cleanup function to stop servers on exit
cleanup() {
    echo ""
    print_info "Stopping servers..."
    
    # Kill backend server
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null || true
        print_status "Backend server stopped"
    fi
    
    # Kill frontend server
    if command -v fuser &> /dev/null; then
        fuser -k 3000/tcp 2>/dev/null || true
    elif command -v lsof &> /dev/null; then
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill any remaining servers
    pkill -f "uvicorn.*8000" 2>/dev/null || true
    pkill -f "next.*dev.*3000" 2>/dev/null || true
    
    print_status "All servers stopped"
    exit 0
}

# Set trap for cleanup on script exit
trap cleanup INT TERM EXIT

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

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    source "$VENV_DIR/bin/activate"
else
    print_status "Virtual environment already activated: $VIRTUAL_ENV"
fi

# Upgrade pip first
python -m pip install --upgrade pip --quiet

# Install requirements
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip install -r "$PROJECT_ROOT/requirements.txt" --quiet
    print_status "Dependencies installed"
else
    print_error "requirements.txt not found at $PROJECT_ROOT/requirements.txt"
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
JIGSAWSTACK_API_KEY=
REPLICATE_API_TOKEN=

# JWT Secret (change this in production!
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

# Run database setup if requested
if [ "$RUN_SETUP" = true ]; then
    echo ""
    echo -e "${BLUE}========================================${NC}"
    print_info "Running database setup..."
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Activate virtual environment if not already activated
    if [ -z "$VIRTUAL_ENV" ]; then
        source "$VENV_DIR/bin/activate"
    else
        print_status "Virtual environment already activated: $VIRTUAL_ENV"
    fi
    cd "$PROJECT_ROOT"
    
    # Initialize database tables
    print_info "Initializing database tables..."
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
    
    # Populate test data
    print_info "Populating database with test data..."
    if [ -f "$PROJECT_ROOT/scripts/populate_test_data.py" ]; then
        python "$PROJECT_ROOT/scripts/populate_test_data.py"
        
        echo ""
        echo "Test credentials:"
        echo "  - Admin: admin / admin123"
        echo "  - Organizer: organizer1 / organizer123"
        echo "  - Assistant: assistant / assistant123"
        echo ""
    else
        print_error "Population script not found"
    fi
    
    deactivate
    print_status "Database setup completed"
    echo ""
fi

# Populate test data if requested (standalone mode)
if [ "$POPULATE_DATA" = true ]; then
    echo ""
    echo -e "${BLUE}========================================${NC}"
    print_info "Populating database with test data..."
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Activate virtual environment if not already activated
    if [ -z "$VIRTUAL_ENV" ]; then
        source "$VENV_DIR/bin/activate"
    else
        print_status "Virtual environment already activated: $VIRTUAL_ENV"
    fi
    cd "$PROJECT_ROOT"
    
    # Run the population script
    if [ -f "$PROJECT_ROOT/scripts/populate_test_data.py" ]; then
        python "$PROJECT_ROOT/scripts/populate_test_data.py"
        
        echo ""
        print_status "Test data populated successfully!"
        echo ""
        echo "Test credentials:"
        echo "  - Admin: admin / admin123"
        echo "  - Organizer: organizer1 / organizer123"
        echo "  - Assistant: assistant / assistant123"
        echo ""
    else
        print_error "Population script not found at $PROJECT_ROOT/scripts/populate_test_data.py"
    fi
    
    deactivate
    
    exit 0
fi

# Kill any existing server processes
print_info "Stopping any existing servers..."

# Find and kill process using port 3000 (Next.js)
if command -v fuser &> /dev/null; then
    fuser -k 3000/tcp 2>/dev/null || true
elif command -v lsof &> /dev/null; then
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
else
    pkill -f "next.*dev.*3000" 2>/dev/null || true
fi

# Find and kill process using port 8000 (FastAPI)
if command -v fuser &> /dev/null; then
    fuser -k 8000/tcp 2>/dev/null || true
elif command -v lsof &> /dev/null; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
else
    pkill -f "uvicorn.*8000" 2>/dev/null || true
fi

sleep 1
print_status "Previous servers stopped"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Meetup Organizing System - Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to open browser (cross-platform)
open_browser() {
    python3 -c "
import webbrowser
import time
import sys

# Wait for servers to start
time.sleep(5)

# Open the frontend
success = webbrowser.open('http://localhost:3000')
if success:
    print('Browser opened successfully to http://localhost:3000!')
else:
    print('Could not open browser automatically. Please open http://localhost:3000 manually.')
    sys.exit(0)
" &
}

# Function to run the FastAPI backend
run_backend() {
    # Activate virtual environment if not already activated
    if [ -z "$VIRTUAL_ENV" ]; then
        source "$VENV_DIR/bin/activate"
    fi
    cd "$PROJECT_ROOT"
    
    # Set environment variable to disable authentication for local development
    export DISABLE_AUTH=true
    
    # Set Replicate API token from .env if available
    if [ -f "$ENV_FILE" ]; then
        REPLICATE_TOKEN=$(grep "^REPLICATE_API_TOKEN=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        if [ -n "$REPLICATE_TOKEN" ]; then
            export REPLICATE_API_TOKEN="$REPLICATE_TOKEN"
        fi
    fi
    
    # Run with uvicorn
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Function to run the Next.js frontend
run_frontend() {
    cd "$PROJECT_ROOT/my-app"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_info "Installing Next.js dependencies..."
        npm install
        print_status "Dependencies installed"
    fi
    
    # Run Next.js development server
    exec npm run dev -- --port 3000
}

# Run both servers
if [ "$RUN_SERVER" = true ]; then
    if [ "$RUN_FRONTEND" = true ]; then
        # Start backend server in background when frontend will also run
        print_info "Starting FastAPI backend server on port 8000..."
        run_backend &
        BACKEND_PID=$!
        print_status "Backend server started (PID: $BACKEND_PID)"
        
        # Wait for backend to be ready
        print_info "Waiting for backend server to be ready..."
        for i in {1..30}; do
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                print_status "Backend server is ready!"
                break
            fi
            sleep 1
        done
        
        if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_warning "Backend server may not be ready yet, continuing..."
        fi
        
        echo ""
        echo -e "FastAPI backend:  ${GREEN}http://localhost:8000${NC}"
        echo -e "Frontend:        ${GREEN}http://localhost:3000${NC}"
        echo ""
        
        # Open browser in background
        print_info "Opening browser..."
        open_browser
        
        # Run frontend server (this will replace the process)
        run_frontend
    else
        # When frontend is not running, run backend directly in foreground
        print_info "Starting FastAPI backend server on port 8000..."
        
        # Activate virtual environment if not already activated
        if [ -z "$VIRTUAL_ENV" ]; then
            source "$VENV_DIR/bin/activate"
        fi
        cd "$PROJECT_ROOT"
        
        # Set environment variable to disable authentication for local development
        export DISABLE_AUTH=true
        
        # Set Replicate API token from .env if available
        if [ -f "$ENV_FILE" ]; then
            REPLICATE_TOKEN=$(grep "^REPLICATE_API_TOKEN=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
            if [ -n "$REPLICATE_TOKEN" ]; then
                export REPLICATE_API_TOKEN="$REPLICATE_TOKEN"
            fi
        fi
        
        echo ""
        echo -e "FastAPI backend is running at: ${GREEN}http://localhost:8000${NC}"
        echo -e "Press ${YELLOW}Ctrl+C${NC} to stop the server"
        echo ""
        
        # Run with uvicorn in foreground
        exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    fi
fi
