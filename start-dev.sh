#!/bin/bash

# AI Business Simulation - Development Server Startup Script
# This script starts both the frontend and backend servers simultaneously

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Function to print colored output
print_status() {
    echo -e "${CYAN}[DEV SERVER]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to cleanup background processes
cleanup() {
    print_status "Shutting down servers..."
    kill $(jobs -p) 2>/dev/null || true
    print_success "All servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Print banner
echo -e "\n${BLUE}${BOLD}============================================================"
echo "🚀 AI Business Simulation - Development Server"
echo -e "============================================================${NC}"
echo -e "${BLUE}Backend:${NC} http://localhost:5001"
echo -e "${GREEN}Frontend:${NC} http://localhost:8080"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}\n"

# Check if directories exist
if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

# Check if required files exist
if [ ! -f "$BACKEND_DIR/app.py" ]; then
    print_error "Backend app.py not found"
    exit 1
fi

if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    print_error "Frontend package.json not found"
    exit 1
fi

print_success "All required files found"

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        print_status "Activating Python virtual environment..."
        source venv/bin/activate
    fi
    
    # Start Flask backend
    python -c "from app import create_app; app = create_app(); app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)" 2>&1 | while IFS= read -r line; do
        echo -e "${BLUE}[Backend]${NC} $line"
    done &
    
    BACKEND_PID=$!
    print_success "Backend server started (PID: $BACKEND_PID)"
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "Installing frontend dependencies..."
        npm install
        print_success "Frontend dependencies installed"
    fi
    
    # Start frontend dev server
    npm run dev 2>&1 | while IFS= read -r line; do
        echo -e "${GREEN}[Frontend]${NC} $line"
    done &
    
    FRONTEND_PID=$!
    print_success "Frontend server started (PID: $FRONTEND_PID)"
}

# Start both servers
start_backend
sleep 3  # Give backend time to start

start_frontend
sleep 3  # Give frontend time to start

# Print final status
echo ""
print_success "🎉 Development servers are running!"
echo -e "${BLUE}Backend API:${NC} http://localhost:5001"
echo -e "${GREEN}Frontend App:${NC} http://localhost:8080"
echo ""
print_warning "Press Ctrl+C to stop all servers"
echo ""

# Wait for user to stop the servers
wait