#!/bin/bash

# SUPER Vote Secret - Easy Docker Deployment Script
# Domain: vote.super-csn.ca

set -e

echo "🗳️  SUPER Vote Secret - Docker Deployment"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your secure passwords before continuing!"
    echo "📂 File location: $(pwd)/.env"
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

# Pull latest images
echo "📦 Pulling Docker images..."
docker-compose pull

# Build custom images
echo "🔨 Building application images..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Test health endpoints
echo "🩺 Testing health endpoints..."

if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Nginx proxy is healthy"
else
    echo "⚠️  Nginx proxy health check failed"
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
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart: docker-compose restart"
echo "  • Update: git pull && docker-compose up -d --build"
echo ""
echo "🔒 SSL Certificate:"
echo "  • Automatic via Let's Encrypt"
echo "  • May take a few minutes to generate"
echo ""
echo "🗳️  SUPER Vote Secret is ready!"
echo ""