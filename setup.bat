@echo off
setlocal enabledelayedexpansion

:: Restoration-Intel Project Setup Script for Windows

:: Color codes for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

:: Function to print status messages
:print_status
echo %GREEN%[✓] %~1%NC%
exit /b

:: Function to print warning messages
:print_warning
echo %YELLOW%[!] %~1%NC%
exit /b

:: Function to print error messages
:print_error
echo %RED%[✗] %~1%NC%
exit /b

:: Verify required tools
:verify_tools
call :print_status "Verifying required tools..."

:: Check Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "Docker is not installed. Please install Docker Desktop."
    exit /b 1
)

:: Check Docker Compose
where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "Docker Compose is not installed. Please install Docker Compose."
    exit /b 1
)

:: Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "Python is not installed. Please install Python 3.11+"
    exit /b 1
)

:: Check npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "npm is not installed. Please install Node.js and npm."
    exit /b 1
)

call :print_status "All required tools are installed."
exit /b 0

:: Create environment files
:create_env_files
call :print_status "Creating environment configuration files..."

:: Create .env.docker if not exists
if not exist .env.docker (
    copy .env.docker.example .env.docker
    call :print_warning "Created .env.docker from example. Please review and update secrets!"
)

:: Create .env.local for Next.js if not exists
if not exist next-app\.env.local (
    copy next-app\.env.local.example next-app\.env.local
    call :print_warning "Created next-app\.env.local from example. Please review and update secrets!"
)

call :print_status "Environment files created."
exit /b 0

:: Install dependencies
:install_dependencies
call :print_status "Installing project dependencies..."

:: Root project dependencies
call npm install

:: Next.js frontend dependencies
cd next-app
call npm install
cd ..

:: Python dependencies
call python -m pip install --upgrade pip
call python -m pip install -r requirements.txt

call :print_status "All dependencies installed successfully."
exit /b 0

:: Initialize Docker services
:start_docker_services
call :print_status "Starting Docker services..."
call docker-compose up --build -d

:: Wait for services to be ready
timeout /t 30 /nobreak > nul

call :print_status "Docker services started."
exit /b 0

:: Apply database migrations
:apply_migrations
call :print_status "Applying database migrations..."

:: Run Supabase migrations
call docker-compose exec -T supabase psql -U postgres -d postgres -f /docker-entrypoint-initdb.d/202406_root.sql

call :print_status "Database migrations applied successfully."
exit /b 0

:: Main setup function
:main
cls
echo Restoration-Intel Project Setup
echo ===============================

call :verify_tools
if %errorlevel% neq 0 exit /b 1

call :create_env_files
call :install_dependencies
call :start_docker_services
call :apply_migrations

call :print_status "Project setup completed successfully!"
echo.
echo Access your services:
echo - Next.js Frontend: http://localhost:3000
echo - FastAPI Backend: http://localhost:8000
echo - Supabase: http://localhost:54321

exit /b 0

:: Run the main setup function
call :main