#!/bin/bash

# SUPER Vote Secret - Easy Docker Deployment Script
# Domain: vote.super-csn.ca
# Compatible with Docker Compose v2.39.1+

set -e

echo "🗳️  SUPER Vote Secret - Docker Deployment"
echo "========================================="
echo "Docker Version: $(docker --version 2>/dev/null || echo 'Not installed')"
echo "Docker Compose Version: $(docker compose version 2>/dev/null || echo 'Not installed')"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose (v2 syntax)
if ! docker compose version &> /dev/null; then
    if ! docker-compose version &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    else
        echo "⚠️  Using legacy docker-compose command. Consider upgrading to Docker Compose v2."
        COMPOSE_CMD="docker-compose"
    fi
else
    COMPOSE_CMD="docker compose"
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your secure passwords before continuing!"
    echo "📂 File location: $(pwd)/.env"
    echo "🔑 CRITICAL: Change JWT_SECRET and ENCRYPTION_KEY for security!"
    read -p "Press Enter after editing .env file..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p nginx/ssl
mkdir -p data/mongodb
mkdir -p data/certbot
mkdir -p data/letsencrypt

# Set permissions
echo "🔐 Setting permissions..."
chmod +x deploy.sh
chmod +x check.sh
chmod +x validate-docker.sh
chmod +x fix-docker.sh

# Pull latest images
echo "📦 Pulling Docker images..."
$COMPOSE_CMD pull

# Build custom images
echo "🔨 Building application images..."
$COMPOSE_CMD build

# Start services
echo "🚀 Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."
$COMPOSE_CMD ps

# Test health endpoints
echo "🩺 Testing health endpoints..."

if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Nginx proxy is healthy"
else
    echo "⚠️  Nginx proxy health check failed (this is normal during first SSL setup)"
fi

# Show final status
echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo ""
echo "🌐 Application URL: https://vote.super-csn.ca"
echo "📁 Local URL: http://localhost (redirects to HTTPS)"
echo ""
echo "📋 Useful commands:"
echo "  • View logs: $COMPOSE_CMD logs -f"
echo "  • Stop services: $COMPOSE_CMD down"
echo "  • Restart: $COMPOSE_CMD restart"
echo "  • Update: git pull && $COMPOSE_CMD up -d --build"
echo ""
echo "🔒 SSL Certificate:"
echo "  • Automatic via Let's Encrypt"
echo "  • May take a few minutes to generate on first run"
echo "  • Check logs: $COMPOSE_CMD logs certbot"
echo ""
echo "🗳️  SUPER Vote Secret is ready for vote.super-csn.ca!"
echo ""