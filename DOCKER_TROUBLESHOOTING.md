# 🐳 Docker Build Troubleshooting Guide

## Quick Fix Commands

If you encounter Docker build issues:

```bash
# Automatic fix for common issues
./fix-docker.sh

# Manual validation
./validate-docker.sh

# Check what specific issue you have
./check.sh
```

---

## Common Build Errors & Solutions

### 1. Frontend Build Errors

#### Error: `yarn install --frozen-lockfile` failed
```bash
# Solution 1: Clean and reinstall
cd frontend
rm -rf node_modules yarn.lock package-lock.json
yarn install

# Solution 2: Use different install method
# Edit frontend/Dockerfile to use:
RUN yarn install --network-timeout 1000000
```

#### Error: `COPY yarn.lock ./` - no such file
```bash
# Generate yarn.lock
cd frontend
yarn install

# Or modify Dockerfile to be more flexible:
COPY package.json ./
COPY yarn.loc[k] ./  # Optional copy
```

#### Error: React build fails
```bash
# Check if all React dependencies are present
cd frontend
yarn add react react-dom react-scripts

# Increase memory limit
# In Dockerfile add:
ENV NODE_OPTIONS="--max-old-space-size=4096"
```

### 2. Backend Build Errors

#### Error: `pip install -r requirements.txt` failed
```bash
# Solution 1: Update pip first
# In Dockerfile:
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Solution 2: Install system dependencies
# Add to Dockerfile:
RUN apt-get update && apt-get install -y gcc g++ python3-dev
```

#### Error: Cryptography build fails
```bash
# Add system dependencies for cryptography
# In backend/Dockerfile:
RUN apt-get update && apt-get install -y \
    gcc g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
```

#### Error: ReportLab or other native extensions fail
```bash
# Add more build tools
RUN apt-get update && apt-get install -y \
    gcc g++ \
    build-essential \
    libjpeg-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*
```

### 3. Docker Compose Issues

#### Error: Service won't start
```bash
# Check logs
docker-compose logs [service-name]

# Rebuild specific service
docker-compose build [service-name]

# Force rebuild
docker-compose build --no-cache [service-name]
```

#### Error: Port already in use
```bash
# Find what's using the port
sudo netstat -tulpn | grep :8001
sudo netstat -tulpn | grep :3000

# Stop conflicting services
sudo systemctl stop nginx
sudo systemctl stop apache2
```

#### Error: MongoDB connection failed
```bash
# Wait for MongoDB to be ready
# Add to docker-compose.yml:
depends_on:
  mongodb:
    condition: service_healthy
```

### 4. Network Issues

#### Error: Can't connect between services
```bash
# Make sure services are in same network
# Check docker-compose.yml has:
networks:
  vote-secret-network:
    driver: bridge

# Use service names in URLs, not localhost
MONGO_URL: mongodb://admin:pass@mongodb:27017/db
# Not: mongodb://admin:pass@localhost:27017/db
```

---

## Build Optimization Tips

### 1. Faster Builds

```bash
# Use Docker layer caching
# Copy requirements/package.json first:
COPY requirements.txt ./
RUN pip install -r requirements.txt
# Then copy code:
COPY . ./
```

### 2. Smaller Images

```bash
# Use multi-stage builds
# Remove dev dependencies in production
RUN yarn install --production

# Use .dockerignore files
echo "node_modules" > .dockerignore
echo "__pycache__" > .dockerignore
```

### 3. Build Speed

```bash
# Parallel builds
docker-compose build --parallel

# Increase memory
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1
```

---

## Debug Commands

### Check Build Context

```bash
# See what's being sent to Docker
docker-compose config

# Check specific service config  
docker-compose config frontend
```

### Inspect Failed Builds

```bash
# Build with more verbose output
docker-compose build --progress=plain

# Run intermediate container for debugging
docker run -it <image-id> /bin/bash
```

### Monitor Resources

```bash
# Check Docker disk usage
docker system df

# Clean up
docker system prune -a
```

---

## Environment-Specific Issues

### On ARM64 (M1/M2 Macs)

```bash
# Specify platform
docker-compose build --build-arg BUILDPLATFORM=linux/amd64

# Or in Dockerfile:
FROM --platform=linux/amd64 node:20-alpine
```

### On Low Memory Systems

```bash
# Reduce parallel builds
docker-compose build --parallel 1

# Or set memory limits in docker-compose.yml:
services:
  frontend:
    build: .
    mem_limit: 1g
```

---

## Complete Reset

If all else fails:

```bash
# Nuclear option - reset everything
docker-compose down -v
docker system prune -a --volumes
docker rmi $(docker images -q)

# Then rebuild from scratch
./fix-docker.sh
docker-compose build
```

---

## Validation Checklist

Before building:

- [ ] `./validate-docker.sh` passes
- [ ] All Dockerfile files exist
- [ ] Dependencies files (package.json, requirements.txt) exist
- [ ] .dockerignore files present
- [ ] No old node_modules or __pycache__ directories
- [ ] Environment variables configured
- [ ] Ports not already in use

Build with confidence! 🚀