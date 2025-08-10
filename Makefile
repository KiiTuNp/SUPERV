# SUPER Vote Secret - Makefile
# Convenient commands for development and deployment

.PHONY: help deploy dev build test clean logs status health

# Default target
help:
	@echo "SUPER Vote Secret - Available Commands:"
	@echo ""
	@echo "Production Commands:"
	@echo "  make deploy     - Deploy to production"
	@echo "  make build      - Build production images"
	@echo "  make start      - Start production services"
	@echo "  make stop       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev        - Start development environment"
	@echo "  make dev-build  - Build development images"
	@echo "  make dev-stop   - Stop development services"
	@echo ""
	@echo "Monitoring Commands:"
	@echo "  make logs       - Show all logs"
	@echo "  make status     - Show service status"
	@echo "  make health     - Check application health"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make clean      - Clean Docker resources"
	@echo "  make backup     - Backup database"
	@echo "  make update     - Update and restart services"

# Production commands
deploy:
	@echo "🚀 Deploying SUPER Vote Secret to production..."
	./deploy.sh

build:
	@echo "🔨 Building production images..."
	docker-compose build --no-cache

start:
	@echo "▶️  Starting production services..."
	docker-compose up -d

stop:
	@echo "⏹️  Stopping all services..."
	docker-compose down

restart:
	@echo "🔄 Restarting all services..."
	docker-compose restart

# Development commands
dev:
	@echo "🛠️  Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo ""
	@echo "Services available at:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8001"
	@echo "  MongoDB:  mongodb://admin:devpassword123@localhost:27017"

dev-build:
	@echo "🔨 Building development images..."
	docker-compose -f docker-compose.dev.yml build

dev-stop:
	@echo "⏹️  Stopping development services..."
	docker-compose -f docker-compose.dev.yml down

# Monitoring commands
logs:
	@echo "📋 Showing service logs..."
	docker-compose logs -f --tail=100

status:
	@echo "📊 Service status:"
	docker-compose ps

health:
	@echo "🏥 Checking application health..."
	@echo ""
	@echo "Backend Health:"
	@curl -s http://localhost:8001/api/health 2>/dev/null || echo "Backend not accessible"
	@echo ""
	@echo "Frontend Health:"  
	@curl -s http://localhost:3000/health 2>/dev/null || echo "Frontend not accessible"
	@echo ""
	@echo "Nginx Health:"
	@curl -s http://localhost:80/health 2>/dev/null || echo "Nginx not accessible"

# Maintenance commands
clean:
	@echo "🧹 Cleaning Docker resources..."
	docker-compose down --volumes --remove-orphans
	docker system prune -af
	docker volume prune -f

backup:
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	docker-compose exec -T mongodb mongodump --authenticationDatabase admin --out /tmp/backup
	docker cp $$(docker-compose ps -q mongodb):/tmp/backup backups/mongodb-$$(date +%Y%m%d-%H%M%S)
	@echo "✅ Backup created in backups/ directory"

update:
	@echo "🔄 Updating application..."
	git pull
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Update completed"

# SSL certificate management
ssl-status:
	@echo "🔒 SSL Certificate Status:"
	docker-compose exec certbot certbot certificates

ssl-renew:
	@echo "🔄 Renewing SSL certificates..."
	docker-compose exec certbot certbot renew

# Database management
db-shell:
	@echo "🗄️  Opening MongoDB shell..."
	docker-compose exec mongodb mongosh --authenticationDatabase admin

db-stats:
	@echo "📊 Database statistics:"
	docker-compose exec -T mongodb mongosh --quiet --authenticationDatabase admin --eval "db.adminCommand('serverStatus')"