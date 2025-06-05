# Docker Build Troubleshooting Guide for Restoration-Intel

## Common Build Issues

### 1. requirements.txt Copy Failure

#### Symptoms
- Error: "failed to compute cache key"
- "requirements.txt not found"

#### Diagnostic Steps

1. **Verify File Location**
   ```bash
   # Confirm requirements.txt exists
   ls -l requirements.txt
   
   # Check build context
   pwd
   ```

2. **Build Context Verification**
   - Ensure docker-compose.yml has correct `context` setting
   - Verify Dockerfile's COPY command matches file location

3. **Potential Solutions**
   a. Explicit Path Copying
   ```dockerfile
   # In Dockerfile
   COPY requirements.txt /app/requirements.txt
   ```

   b. Build Argument for Flexibility
   ```dockerfile
   ARG REQUIREMENTS_PATH=requirements.txt
   COPY ${REQUIREMENTS_PATH} /app/requirements.txt
   ```

### 4. Docker Build Context Issues

#### Common Causes
- Incorrect working directory
- Mismatched file paths
- Build context not including required files

#### Debugging Checklist
- [ ] Confirm current working directory
- [ ] Verify docker-compose.yml build context
- [ ] Check Dockerfile COPY commands
- [ ] Ensure all necessary files are in build context

### 5. Dependency Installation Failures

#### Potential Issues
- Missing system dependencies
- Python version incompatibility
- Network connectivity problems

#### Troubleshooting
```bash
# Verify Python version
python --version

# Check pip installation
pip --version

# Test manual dependency install
pip install -r requirements.txt
```

## Recommended Docker Compose Configuration

```yaml
services:
  fastapi:
    build:
      context: .  # Set to project root
      dockerfile: api/Dockerfile
      args:
        - REQUIREMENTS_PATH=requirements.txt
```

## Dockerfile Best Practices

1. Use multi-stage builds
2. Minimize layer count
3. Use .dockerignore
4. Pin dependency versions
5. Use non-root users

## Logging and Debugging

### Verbose Build Logs
```bash
docker-compose build --no-cache --verbose fastapi
```

### Inspect Build Stages
```bash
docker build -t restoration-intel-api --target builder .
```

## Network and Connectivity

- Ensure Docker has internet access
- Check proxy settings
- Verify DNS resolution

## Common Error Resolutions

### Permission Denied
- Check file and directory permissions
- Ensure Docker user has access

### Missing Dependencies
- Install system-level dependencies in Dockerfile
- Use `apt-get` for system packages

## Advanced Debugging

### Build Arguments and Environment
```bash
docker-compose build \
  --build-arg REQUIREMENTS_PATH=requirements.txt \
  --build-arg PYTHON_VERSION=3.11 \
  fastapi
```

## Contact and Support

For persistent issues:
- Check project documentation
- Review recent changes
- Consult project maintainers

---

**Note**: Docker builds can be complex. Systematic debugging and careful configuration are key to resolution.