#!/bin/bash

# Restoration-Intel Project Setup Script

set -e  # Exit immediately if a command exits with a non-zero status

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

# Verify required tools
verify_tools() {
    print_status "Verifying required tools..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop."
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+"
        exit 1
    fi

    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install Node.js and npm."
        exit 1
    fi

    print_status "All required tools are installed."
}

# Create environment files
create_env_files() {
    print_status "Creating environment configuration files..."

    # Create .env.docker if not exists
    if [ ! -f .env.docker ]; then
        cp .env.docker.example .env.docker
        print_warning "Created .env.docker from example. Please review and update secrets!"
    fi

    # Create .env.local for Next.js if not exists
    if [ ! -f next-app/.env.local ]; then
        cp next-app/.env.local.example next-app/.env.local
        print_warning "Created next-app/.env.local from example. Please review and update secrets!"
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing project dependencies..."

    # Root project dependencies
    npm install

    # Next.js frontend dependencies
    cd next-app
    npm install
    cd ..

    # Python dependencies
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt

    print_status "All dependencies installed successfully."
}

# Initialize Docker services
start_docker_services() {
    print_status "Starting Docker services..."
    docker-compose up --build -d

    # Wait for services to be ready
    sleep 30

    print_status "Docker services started."
}

# Apply database migrations
apply_migrations() {
    print_status "Applying database migrations..."
    
    # Run Supabase migrations
    docker-compose exec -T supabase psql -U postgres -d postgres -f /docker-entrypoint-initdb.d/202406_root.sql

    print_status "Database migrations applied successfully."
}

# Main setup function
main() {
    clear
    echo "Restoration-Intel Project Setup"
    echo "==============================="

    verify_tools
    create_env_files
    install_dependencies
    start_docker_services
    apply_migrations

    print_status "Project setup completed successfully!"
    echo ""
    echo "Access your services:"
    echo "- Next.js Frontend: http://localhost:3000"
    echo "- FastAPI Backend: http://localhost:8000"
    echo "- Supabase: http://localhost:54321"
}

# Run the main setup function
main