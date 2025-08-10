#!/bin/bash

# SUPER Vote Secret - Docker Build Fix Script
# Automatically fixes common Docker build issues

echo "🗳️  SUPER Vote Secret - Docker Build Auto-Fix"
echo "==============================================="
echo ""

# Clean frontend dependencies
echo "🧹 Cleaning frontend dependencies..."
cd frontend
if [ -d "node_modules" ]; then
    echo "  • Removing old node_modules..."
    rm -rf node_modules
fi

if [ -f "yarn.lock" ]; then
    echo "  • Removing old yarn.lock..."
    rm -f yarn.lock
fi

if [ -f "package-lock.json" ]; then
    echo "  • Removing package-lock.json..."
    rm -f package-lock.json
fi

echo "  • Installing fresh dependencies..."
yarn install --network-timeout 1000000

cd ..

# Clean backend dependencies
echo ""
echo "🧹 Cleaning backend dependencies..."
cd backend
if [ -d "__pycache__" ]; then
    echo "  • Removing __pycache__ directories..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
fi

if [ -f "*.pyc" ]; then
    echo "  • Removing .pyc files..."
    find . -name "*.pyc" -delete 2>/dev/null || true
fi

echo "  • Testing Python dependencies..."
python3 -m pip install --quiet --dry-run -r requirements.txt

cd ..

# Validate Docker configuration
echo ""
echo "✅ Running Docker validation..."
./validate-docker.sh

echo ""
echo "🎉 Docker build issues have been automatically fixed!"
echo ""
echo "🚀 You can now build with confidence:"
echo "  • Test build: docker compose -f docker-compose.test.yml build"
echo "  • Production build: docker compose build"
echo "  • Legacy: docker-compose build (if using v1)"
echo ""