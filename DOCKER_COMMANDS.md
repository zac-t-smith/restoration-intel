# Docker Commands Guide

This document provides instructions for using Docker with this project, with optimized configurations for faster builds and proper context management.

## Fixed Issues

### Path Resolution Error
The error `failed to evaluate path "C:\\Users\\Amber\\CRM Edits/C:\\Users\\Amber\\CRM Edits\\api\\Dockerfile"` was caused by a Windows path resolution issue in Docker Compose. This has been fixed by:

1. Keeping the build context at the root directory while using proper relative paths
2. Using `dockerfile: api/Dockerfile` with the correct path syntax
3. Setting up proper arguments for the requirements.txt location

### Obsolete Version Attribute
The warning `the attribute 'version' is obsolete, it will be ignored` has been removed as modern Docker Compose files don't require the version attribute.

### Optimized Build Context
The build context has been optimized from 742MB+ to a more manageable size by:
1. Using an optimized `.dockerignore` file to exclude unnecessary files
2. Implementing BuildKit caching features for faster builds
3. Using a shell script approach to handle optional files in the Dockerfile

## Docker Build Commands

### Using Build Scripts (Easiest Method)

We've created scripts that automatically set up all optimization flags and build your services:

#### Windows:
```
docker-build.bat [service_name]
```

#### Mac/Linux:
```
chmod +x docker-build.sh  # First time only
./docker-build.sh [service_name]
```

These scripts automatically enable BuildKit and COMPOSE_BAKE for maximum performance.
The service_name parameter is optional - if omitted, all services will be built.

### Using COMPOSE_BAKE for Faster Builds (Manual Method)

Docker Compose supports delegating builds to the BuildKit backend using COMPOSE_BAKE. As shown in the Docker output:
```
Compose can now delegate builds to bake for better performance.
To do so, set COMPOSE_BAKE=true.
```

To manually enable this optimization:

#### Windows:
```cmd
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1
set COMPOSE_BAKE=true
docker compose build fastapi
```

#### Mac/Linux:
```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export COMPOSE_BAKE=true
docker compose build fastapi
```

### Normal Build (Without Optimizations)

```bash
# Build the FastAPI service
docker compose build fastapi
```

## Starting the Services

### Start All Services

```bash
# Start all services in docker-compose.yml
docker compose up
```

### Start Only FastAPI Service

```bash
# Start only the FastAPI service and its dependencies
docker compose up fastapi
```

### Start in Detached Mode

```bash
# Run in background
docker compose up -d fastapi
```

## Monitoring and Management

```bash
# View logs
docker compose logs -f fastapi

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v
```

## BuildKit Caching Features

This project is now configured to use BuildKit's advanced caching features:

1. Apt package cache is preserved between builds with `--mount=type=cache,target=/var/cache/apt`
2. Pip cache is preserved between builds with `--mount=type=cache,target=/root/.cache/pip`
3. Python packages are stored in a named volume for reuse
4. Multi-stage build reduces final image size

To take full advantage of these optimizations, always use the BuildKit-enabled commands with COMPOSE_BAKE=true.

## Build Context Optimization

The Docker build has been optimized by:

1. Using proper `.dockerignore` files to exclude unnecessary files
2. Using a shell script approach in the Dockerfile to handle optional files
3. Optimizing the RUN commands to reduce the number of layers

## Troubleshooting

### Windows Path Issues

If you encounter path issues on Windows:
- Use forward slashes (`/`) instead of backslashes (`\`) in Docker-related paths
- Use relative paths rather than absolute paths whenever possible
- When specifying volume mounts, use the format: `./local/path:/container/path`

### BuildKit Not Working

If BuildKit optimizations aren't working:
- Ensure Docker Desktop is updated to the latest version
- Set the environment variables as shown above
- Add `DOCKER_BUILDKIT=1` to your system environment variables

### Slow Builds

If builds are still slow:
- Check that the `.dockerignore` files are properly excluding large directories
- Ensure your Docker Desktop has enough resources allocated (CPU/Memory)
- Consider increasing the cache size in Docker Desktop settings
- Try using `COMPOSE_BAKE=true` for additional performance improvements