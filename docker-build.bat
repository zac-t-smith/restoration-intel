@echo off
echo Setting up optimized Docker build environment...

:: Enable BuildKit and COMPOSE_BAKE for maximum performance
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1
set COMPOSE_BAKE=true

echo BuildKit and COMPOSE_BAKE enabled for maximum performance

:: Parse command line arguments
if "%1"=="" (
    echo Building all services with optimized settings
    docker compose build
) else (
    echo Building %1 service with optimized settings
    docker compose build %1
)

echo.
echo Build completed. To start the services, run:
echo docker compose up [service_name]