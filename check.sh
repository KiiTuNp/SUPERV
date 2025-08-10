#!/bin/bash

# SUPER Vote Secret - Pre-deployment Check

echo "🗳️  SUPER Vote Secret - Pre-deployment Check"
echo "============================================="
echo ""

ERRORS=0

# Check required files
echo "📁 Checking required files..."
REQUIRED_FILES=("docker-compose.yml" "backend/Dockerfile" "frontend/Dockerfile" "nginx/nginx.conf" "mongo-init.js")

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        ERRORS=$((ERRORS+1))
    fi
done

# Check environment file
echo ""
echo "🔧 Checking environment configuration..."
if [ -f ".env" ]; then
    echo "  ✅ .env file exists"
    
    # Check critical variables
    if grep -q "MONGO_ROOT_PASSWORD=securepassword123" .env; then
        echo "  ⚠️  Using default MongoDB password (please change it)"
    else
        echo "  ✅ MongoDB password customized"
    fi
    
    if grep -q "JWT_SECRET=your-super-secret" .env; then
        echo "  ❌ JWT_SECRET not changed from default"
        ERRORS=$((ERRORS+1))
    else
        echo "  ✅ JWT_SECRET customized"
    fi
    
    if grep -q "ENCRYPTION_KEY=your-32-character" .env; then
        echo "  ❌ ENCRYPTION_KEY not changed from default"
        ERRORS=$((ERRORS+1))
    else
        echo "  ✅ ENCRYPTION_KEY customized"
    fi
else
    echo "  ❌ .env file missing (copy from .env.example)"
    ERRORS=$((ERRORS+1))
fi

# Check Docker
echo ""
echo "🐳 Checking Docker..."
if command -v docker &> /dev/null; then
    echo "  ✅ Docker installed"
    if docker info &> /dev/null; then
        echo "  ✅ Docker service running"
    else
        echo "  ❌ Docker service not running"
        ERRORS=$((ERRORS+1))
    fi
else
    echo "  ❌ Docker not installed"
    ERRORS=$((ERRORS+1))
fi

if command -v docker-compose &> /dev/null; then
    echo "  ✅ Docker Compose installed"
else
    echo "  ❌ Docker Compose not installed"
    ERRORS=$((ERRORS+1))
fi

# Check DNS (if domain is configured)
echo ""
echo "🌐 Checking domain configuration..."
if [ -f ".env" ] && grep -q "DOMAIN=vote.super-csn.ca" .env; then
    DOMAIN=$(grep "DOMAIN=" .env | cut -d'=' -f2)
    
    if nslookup "$DOMAIN" &> /dev/null; then
        IP=$(nslookup "$DOMAIN" | grep "Address:" | tail -1 | awk '{print $2}')
        echo "  ✅ Domain $DOMAIN resolves to $IP"
    else
        echo "  ⚠️  Domain $DOMAIN does not resolve (SSL may fail)"
    fi
else
    echo "  ⚠️  Domain not configured in .env"
fi

# Check ports
echo ""
echo "🔌 Checking ports..."
PORTS=(80 443)

for port in "${PORTS[@]}"; do
    if netstat -tuln 2>/dev/null | grep ":$port " > /dev/null; then
        echo "  ⚠️  Port $port is already in use"
    else
        echo "  ✅ Port $port is available"
    fi
done

# Summary
echo ""
echo "📊 Summary"
echo "==========="
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed! Ready for deployment."
    echo ""
    echo "🚀 To deploy: ./deploy.sh"
    exit 0
else
    echo "❌ $ERRORS error(s) found. Please fix them before deployment."
    echo ""
    echo "📖 See DOCKER.md for troubleshooting guide."
    exit 1
fi