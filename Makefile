.PHONY: help build deploy dev setup logs status stop clean backup fix validate check ssl

# Default target
help:
	@echo "🗳️  SUPER Vote Secret - Docker Commands"
	@echo "======================================"
	@echo ""
	@echo "Production Commands:"
	@echo "  make deploy     - Deploy to production"
	@echo "  make build      - Build all images"
	@echo "  make logs       - View all logs"
	@echo "  make status     - Check service status"
	@echo "  make stop       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make update     - Update and rebuild"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev        - Start development environment"
	@echo "  make setup      - Setup development environment"
	@echo ""
	@echo "Troubleshooting Commands:"
	@echo "  make fix        - Auto-fix Docker build issues"
	@echo "  make validate   - Validate Docker configuration" 
	@echo "  make check      - Run pre-deployment checks"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make backup     - Backup database"
	@echo "  make clean      - Clean up Docker resources"
	@echo "  make ssl        - Renew SSL certificates"
	@echo ""

# Production commands
deploy:
	@echo "🚀 Deploying SUPER Vote Secret..."
	./deploy.sh

build:
	@echo "🔨 Building Docker images..."
	@docker compose version >/dev/null 2>&1 && docker compose build || docker-compose build

logs:
	@echo "📋 Viewing logs..."
	@docker compose version >/dev/null 2>&1 && docker compose logs -f || docker-compose logs -f

status:
	@echo "📊 Service status:"
	@docker compose version >/dev/null 2>&1 && docker compose ps || docker-compose ps

stop:
	@echo "⏹️  Stopping services..."
	@docker compose version >/dev/null 2>&1 && docker compose down || docker-compose down

restart:
	@echo "🔄 Restarting services..."
	@docker compose version >/dev/null 2>&1 && docker compose restart || docker-compose restart

update:
	@echo "📦 Updating application..."
	git pull
	@docker compose version >/dev/null 2>&1 && docker compose up -d --build || docker-compose up -d --build

# Development commands
dev:
	@echo "🛠️  Starting development environment..."
	npm run dev

setup:
	@echo "⚙️  Setting up development environment..."
	./dev-setup.sh

# Maintenance commands
backup:
	@echo "💾 Creating database backup..."
	mkdir -p ./backups
	docker exec vote-secret-mongodb mongodump --out /tmp/backup
	docker cp vote-secret-mongodb:/tmp/backup ./backups/$(shell date +%Y%m%d_%H%M%S)
	@echo "✅ Backup created in ./backups/"

clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker system prune -f
	docker volume prune -f

ssl:
	@echo "🔒 Renewing SSL certificates..."
	docker-compose exec certbot certbot renew
	docker-compose restart nginx

fix:
	@echo "🔧 Auto-fixing Docker build issues..."
	./fix-docker.sh

validate:
	@echo "✅ Validating Docker configuration..."
	./validate-docker.sh

check:
	@echo "📋 Running pre-deployment checks..."
	./check.sh