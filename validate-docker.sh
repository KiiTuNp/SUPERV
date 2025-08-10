#!/bin/bash

# SUPER Vote Secret - Docker Build Validation Script
# Validates all Docker build requirements without actually building

echo "🗳️  SUPER Vote Secret - Docker Build Validation"
echo "==============================================="
echo ""

ERRORS=0
WARNINGS=0

echo "📁 Checking Dockerfile structure..."

# Check frontend Dockerfile
if [ -f "frontend/Dockerfile" ]; then
    echo "  ✅ Frontend Dockerfile exists"
    
    # Check for common issues
    if grep -q "yarn.lock" frontend/Dockerfile && [ ! -f "frontend/yarn.lock" ]; then
        echo "  ❌ Frontend Dockerfile references yarn.lock but file doesn't exist"
        ERRORS=$((ERRORS+1))
    else
        echo "  ✅ Frontend yarn.lock dependency check passed"
    fi
    
    if grep -q "package.json" frontend/Dockerfile && [ ! -f "frontend/package.json" ]; then
        echo "  ❌ Frontend Dockerfile references package.json but file doesn't exist"
        ERRORS=$((ERRORS+1))
    else
        echo "  ✅ Frontend package.json dependency check passed"
    fi
else
    echo "  ❌ Frontend Dockerfile missing"
    ERRORS=$((ERRORS+1))
fi

# Check backend Dockerfile
if [ -f "backend/Dockerfile" ]; then
    echo "  ✅ Backend Dockerfile exists"
    
    if grep -q "requirements.txt" backend/Dockerfile && [ ! -f "backend/requirements.txt" ]; then
        echo "  ❌ Backend Dockerfile references requirements.txt but file doesn't exist"
        ERRORS=$((ERRORS+1))
    else
        echo "  ✅ Backend requirements.txt dependency check passed"
    fi
else
    echo "  ❌ Backend Dockerfile missing"
    ERRORS=$((ERRORS+1))
fi

echo ""
echo "📦 Checking dependency files..."

# Check frontend dependencies
if [ -f "frontend/package.json" ]; then
    echo "  ✅ Frontend package.json exists"
    
    # Check for problematic dependencies
    if grep -q '"react"' frontend/package.json; then
        echo "  ✅ React dependency found"
    else
        echo "  ⚠️  React dependency not found in package.json"
        WARNINGS=$((WARNINGS+1))
    fi
    
    if [ -f "frontend/yarn.lock" ]; then
        echo "  ✅ Frontend yarn.lock exists"
    else
        echo "  ⚠️  Frontend yarn.lock missing (will be generated during build)"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo "  ❌ Frontend package.json missing"
    ERRORS=$((ERRORS+1))
fi

# Check backend dependencies  
if [ -f "backend/requirements.txt" ]; then
    echo "  ✅ Backend requirements.txt exists"
    
    # Check for essential dependencies
    if grep -q "fastapi" backend/requirements.txt; then
        echo "  ✅ FastAPI dependency found"
    else
        echo "  ❌ FastAPI dependency missing"
        ERRORS=$((ERRORS+1))
    fi
    
    if grep -q "uvicorn" backend/requirements.txt; then
        echo "  ✅ Uvicorn dependency found"
    else
        echo "  ❌ Uvicorn dependency missing"
        ERRORS=$((ERRORS+1))
    fi
else
    echo "  ❌ Backend requirements.txt missing"
    ERRORS=$((ERRORS+1))
fi

echo ""
echo "🔧 Checking configuration files..."

# Check Docker Compose
if [ -f "docker-compose.yml" ]; then
    echo "  ✅ Production docker-compose.yml exists"
else
    echo "  ❌ Production docker-compose.yml missing"
    ERRORS=$((ERRORS+1))
fi

if [ -f "docker-compose.test.yml" ]; then
    echo "  ✅ Test docker-compose.test.yml exists"
else
    echo "  ⚠️  Test docker-compose.test.yml missing"
    WARNINGS=$((WARNINGS+1))
fi

# Check Nginx config
if [ -f "frontend/nginx.conf" ]; then
    echo "  ✅ Frontend nginx.conf exists"
else
    echo "  ❌ Frontend nginx.conf missing"
    ERRORS=$((ERRORS+1))
fi

if [ -f "nginx/nginx.conf" ]; then
    echo "  ✅ Production nginx.conf exists"
else
    echo "  ❌ Production nginx.conf missing"
    ERRORS=$((ERRORS+1))
fi

# Check .dockerignore files
if [ -f "frontend/.dockerignore" ]; then
    echo "  ✅ Frontend .dockerignore exists"
else
    echo "  ⚠️  Frontend .dockerignore missing (build may include unnecessary files)"
    WARNINGS=$((WARNINGS+1))
fi

if [ -f "backend/.dockerignore" ]; then
    echo "  ✅ Backend .dockerignore exists"
else
    echo "  ⚠️  Backend .dockerignore missing (build may include unnecessary files)"
    WARNINGS=$((WARNINGS+1))
fi

echo ""
echo "🗄️ Checking database initialization..."

if [ -f "mongo-init.js" ]; then
    echo "  ✅ MongoDB initialization script exists"
else
    echo "  ⚠️  MongoDB initialization script missing"
    WARNINGS=$((WARNINGS+1))
fi

echo ""
echo "🔍 Checking for common Docker build issues..."

# Check for node_modules in frontend
if [ -d "frontend/node_modules" ]; then
    if [ -f "frontend/.dockerignore" ] && grep -q "node_modules" frontend/.dockerignore; then
        echo "  ✅ Frontend node_modules will be ignored during build"
    else
        echo "  ⚠️  Frontend node_modules exists and might be included in build (slow build)"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo "  ✅ No frontend node_modules directory (clean state)"
fi

# Check for __pycache__ in backend
if [ -d "backend/__pycache__" ]; then
    if [ -f "backend/.dockerignore" ] && grep -q "__pycache__" backend/.dockerignore; then
        echo "  ✅ Backend __pycache__ will be ignored during build"
    else
        echo "  ⚠️  Backend __pycache__ exists and might be included in build"
        WARNINGS=$((WARNINGS+1))
    fi
else
    echo "  ✅ No backend __pycache__ directory (clean state)"
fi

# Summary
echo ""
echo "📊 Build Validation Summary"
echo "==========================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ Perfect! No issues found. Docker build should work flawlessly."
    echo ""
    echo "🚀 Ready to build:"
    echo "  • Test build: docker-compose -f docker-compose.test.yml build"
    echo "  • Production build: docker-compose build"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "✅ Build should work with $WARNINGS warning(s)."
    echo ""
    echo "⚠️  Warnings can cause slower builds or minor issues but won't break the build."
    echo ""
    echo "🚀 Ready to build:"
    echo "  • Test build: docker-compose -f docker-compose.test.yml build"
    echo "  • Production build: docker-compose build"
    exit 0
else
    echo "❌ $ERRORS critical error(s) found that will cause build failures."
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠️  Also found $WARNINGS warning(s)."
    fi
    echo ""
    echo "🔧 Please fix the errors above before attempting Docker build."
    exit 1
fi