# Docker Compatibility Matrix

## Supported Versions

### Docker Engine
- **Minimum**: 20.10.0
- **Recommended**: 28.3.3+
- **Tested**: 28.3.3

### Docker Compose
- **V2**: 2.0.0+ (Recommended)
- **V1**: 1.29.0+ (Legacy support)
- **Tested**: v2.39.1

## Breaking Changes Fixed

### Docker Compose Format
- ✅ **Removed**: `version: '3.8'` (deprecated)
- ✅ **Modern**: Schema validation automatic
- ✅ **Healthchecks**: Enhanced with `start_period`

### Dockerfile Improvements
- ✅ **Frontend**: Flexible yarn.lock handling
- ✅ **Backend**: Enhanced Python dependencies
- ✅ **Security**: Non-root user (UID 1000)
- ✅ **Performance**: Multi-stage builds optimized

### Command Compatibility
```bash
# Docker Compose V2 (Recommended)
docker compose build
docker compose up -d
docker compose logs -f

# Docker Compose V1 (Legacy)
docker-compose build  
docker-compose up -d
docker-compose logs -f
```

## Architecture Support
- ✅ **linux/amd64** (Primary)
- ✅ **linux/arm64** (Apple Silicon)

## Validation
Run `make validate` to check compatibility before building.