#!/bin/bash

# SUPER Vote Secret - Development Setup Script

set -e

echo "🗳️  SUPER Vote Secret - Development Setup"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 20+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "📦 Installing dependencies..."

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd frontend && yarn install && cd ..

# Install backend dependencies
echo "⚙️  Installing backend dependencies..."
cd backend && pip3 install -r requirements.txt && cd ..

# Start development database
echo "🗄️  Starting development database..."
docker-compose -f docker-compose.dev.yml up -d mongodb

# Wait for MongoDB to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

echo ""
echo "🎉 Development Environment Ready!"
echo "================================"
echo ""
echo "🚀 To start development:"
echo "  npm run dev"
echo ""
echo "🌐 Development URLs:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend: http://localhost:8001"
echo "  • MongoDB: mongodb://admin:devpassword123@localhost:27017/vote_secret_dev"
echo ""
echo "📋 Available commands:"
echo "  • npm run dev - Start both frontend and backend"
echo "  • npm run dev:frontend - Start only frontend"
echo "  • npm run dev:backend - Start only backend"
echo "  • docker-compose -f docker-compose.dev.yml logs -f mongodb - View database logs"
echo ""