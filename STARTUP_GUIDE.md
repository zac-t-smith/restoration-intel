# Restoration-Intel: Application Startup Guide

## Prerequisites
- Visual Studio Code
- Docker Desktop
- Node.js (v18.x)
- npm (v9.x)
- Git

## Step-by-Step Startup Procedure

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/restoration-intel.git
cd restoration-intel
```

### 2. Environment Configuration
1. Copy environment template files
```bash
cp .env.docker.example .env.docker
```

2. Edit `.env.docker` and replace placeholder secrets:
- Set unique values for `JWT_SECRET`
- Update `SUPABASE_ANON_KEY`
- Configure `POSTGRES_PASSWORD`

### 3. Install Root Dependencies
```bash
npm install
```

### 4. Install Next.js Frontend Dependencies
```bash
cd next-app
npm install
cd ..
```

### 5. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 6. Start Docker Services
```bash
# Ensure Docker Desktop is running
docker-compose up --build
```

### 7. Database Migrations (if needed)
```bash
# Run Supabase migrations
docker-compose exec supabase psql -U postgres -d postgres -f /docker-entrypoint-initdb.d/202406_root.sql
```

### 8. Frontend Development Server
In a new terminal:
```bash
cd next-app
npm run dev
```

### 9. Verify Services
- FastAPI: http://localhost:8000
- Next.js: http://localhost:3000
- Supabase: http://localhost:54321

## Troubleshooting

### Common Issues
- Ensure all environment variables are set
- Check Docker service logs: `docker-compose logs <service_name>`
- Verify network connectivity
- Restart services if needed: `docker-compose down && docker-compose up --build`

### Dependency Conflicts
```bash
# Rebuild dependencies if conflicts occur
npm cache clean --force
docker-compose build --no-cache
```

## Development Workflow

### Starting Services
```bash
# Start all services
docker-compose up

# Start specific service
docker-compose up fastapi
```

### Stopping Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Performance Optimization

### Docker Build Caching
- Use `docker-compose build --no-cache` for clean builds
- Leverage multi-stage builds for smaller images

## Security Notes
- Rotate secrets regularly
- Use strong, unique passwords
- Limit network exposure

## Recommended Tools
- Docker Desktop
- VS Code Docker Extension
- Postman (for API testing)

---

**Note**: Always refer to the most recent documentation and project README for the most up-to-date instructions.