# SUPER Vote Secret - Makefile pour simplifier les opérations Docker
# Usage: make [command]

# Variables
COMPOSE_FILE = docker-compose.yml
PROJECT_NAME = vote-secret

# Couleurs pour les messages
YELLOW = \033[1;33m
GREEN = \033[1;32m
RED = \033[1;31m
BLUE = \033[1;34m
NC = \033[0m # No Color

.PHONY: help install dev prod quick stop clean logs status restart backup restore

# Commande par défaut
help: ## Afficher cette aide
	@echo "$(BLUE)🗳️  SUPER Vote Secret - Commandes Make$(NC)"
	@echo "$(YELLOW)════════════════════════════════════════$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

# === DÉPLOIEMENT ===

install: ## Déploiement complet interactif avec configuration
	@echo "$(BLUE)🚀 Déploiement SUPER Vote Secret$(NC)"
	./deploy-optimized.sh

dev: ## Déploiement rapide mode développement 
	@echo "$(BLUE)🔧 Déploiement mode développement$(NC)"
	@echo -e "2\ny" | ./deploy-optimized.sh

prod: ## Déploiement production avec SSL
	@echo "$(BLUE)🏭 Déploiement mode production$(NC)"
	@echo -e "1" | ./deploy-optimized.sh

quick: ## Démarrage rapide avec config existante
	@echo "$(BLUE)⚡ Démarrage rapide$(NC)"
	@if [ -f ".env" ]; then \
		docker compose up -d --build; \
		echo "$(GREEN)✅ Application démarrée avec la config existante$(NC)"; \
	else \
		echo "$(RED)❌ Fichier .env manquant - utilisez 'make install' d'abord$(NC)"; \
		exit 1; \
	fi

# === GESTION DES SERVICES ===

start: ## Démarrer tous les services
	@echo "$(BLUE)▶️  Démarrage des services...$(NC)"
	docker compose up -d
	@echo "$(GREEN)✅ Services démarrés$(NC)"

stop: ## Arrêter tous les services
	@echo "$(BLUE)⏹️  Arrêt des services...$(NC)"
	docker compose down
	@echo "$(GREEN)✅ Services arrêtés$(NC)"

restart: ## Redémarrer tous les services
	@echo "$(BLUE)🔄 Redémarrage des services...$(NC)"
	docker compose restart
	@echo "$(GREEN)✅ Services redémarrés$(NC)"

# === MONITORING ET DEBUGGING ===

status: ## Afficher le statut des services
	@echo "$(BLUE)📊 Statut des services:$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(BLUE)🌐 Tests d'accessibilité:$(NC)"
	@curl -s http://localhost/api/health 2>/dev/null && echo "$(GREEN)✅ API accessible$(NC)" || echo "$(RED)❌ API non accessible$(NC)"
	@curl -s http://localhost 2>/dev/null | grep -q "Vote Secret" && echo "$(GREEN)✅ Frontend accessible$(NC)" || echo "$(RED)❌ Frontend non accessible$(NC)"

logs: ## Afficher les logs en temps réel
	@echo "$(BLUE)📋 Logs en temps réel (Ctrl+C pour quitter):$(NC)"
	docker compose logs -f --tail=100

logs-backend: ## Logs du backend uniquement
	@echo "$(BLUE)📋 Logs Backend:$(NC)"
	docker compose logs -f backend

logs-frontend: ## Logs du frontend uniquement
	@echo "$(BLUE)📋 Logs Frontend:$(NC)"
	docker compose logs -f frontend

logs-nginx: ## Logs du nginx uniquement
	@echo "$(BLUE)📋 Logs Nginx:$(NC)"
	docker compose logs -f nginx

health: ## Vérification complète de santé
	@echo "$(BLUE)🏥 Vérification de santé complète:$(NC)"
	@echo ""
	@echo "$(BLUE)🐳 Conteneurs Docker:$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(BLUE)🌐 Endpoints:$(NC)"
	@curl -s -w "%{http_code}\n" -o /dev/null http://localhost/api/health && echo "$(GREEN)✅ API Health: OK$(NC)" || echo "$(RED)❌ API Health: ÉCHEC$(NC)"
	@curl -s -w "%{http_code}\n" -o /dev/null http://localhost && echo "$(GREEN)✅ Frontend: OK$(NC)" || echo "$(RED)❌ Frontend: ÉCHEC$(NC)"

# === MAINTENANCE ===

clean: ## Nettoyer les conteneurs et volumes
	@echo "$(YELLOW)⚠️  ATTENTION: Cette action supprimera tous les conteneurs et volumes$(NC)"
	@read -p "Êtes-vous sûr ? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(BLUE)🧹 Nettoyage en cours...$(NC)"; \
		docker compose down -v --remove-orphans; \
		docker system prune -f; \
		echo "$(GREEN)✅ Nettoyage terminé$(NC)"; \
	else \
		echo "$(BLUE)ℹ️  Nettoyage annulé$(NC)"; \
	fi

rebuild: ## Reconstruire et redémarrer
	@echo "$(BLUE)🔨 Reconstruction et redémarrage...$(NC)"
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo "$(GREEN)✅ Reconstruction terminée$(NC)"

update: ## Mettre à jour et reconstruire
	@echo "$(BLUE)📦 Mise à jour des images...$(NC)"
	docker compose pull
	docker compose build --pull
	docker compose up -d
	@echo "$(GREEN)✅ Mise à jour terminée$(NC)"

# === SAUVEGARDE ===

backup: ## Créer une sauvegarde des données
	@echo "$(BLUE)💾 Création d'une sauvegarde...$(NC)"
	@BACKUP_DATE=$$(date +%Y%m%d_%H%M%S); \
	mkdir -p backups; \
	docker compose exec -T mongodb mongodump --authenticationDatabase admin -u admin -p $(shell grep MONGO_ROOT_PASSWORD .env | cut -d '=' -f2) --archive=/tmp/backup.gz --gzip; \
	docker cp $$(docker compose ps -q mongodb):/tmp/backup.gz backups/mongodb_backup_$$BACKUP_DATE.gz; \
	tar -czf backups/config_backup_$$BACKUP_DATE.tar.gz .env frontend/.env backend/.env docker-compose.yml; \
	echo "$(GREEN)✅ Sauvegarde créée: backups/*_$$BACKUP_DATE.*$(NC)"

# === DÉVELOPPEMENT ===

shell-backend: ## Shell dans le conteneur backend
	docker compose exec backend bash

shell-frontend: ## Shell dans le conteneur frontend
	docker compose exec frontend bash

shell-mongodb: ## Shell MongoDB
	docker compose exec mongodb mongosh -u admin -p $(shell grep MONGO_ROOT_PASSWORD .env | cut -d '=' -f2) --authenticationDatabase admin

# === SSL ===

ssl-status: ## Vérifier le statut SSL
	@echo "$(BLUE)🔒 Statut SSL:$(NC)"
	@if [ -f ".env" ] && grep -q "SSL_ENABLED=true" .env; then \
		docker compose logs certbot | tail -10; \
	else \
		echo "$(YELLOW)ℹ️  SSL désactivé dans la configuration$(NC)"; \
	fi

ssl-renew: ## Renouveler les certificats SSL
	@echo "$(BLUE)🔄 Renouvellement SSL...$(NC)"
	docker compose restart certbot
	docker compose logs -f certbot

# === TESTS ===

test: ## Lancer les tests de l'application
	@echo "$(BLUE)🧪 Tests de l'application...$(NC)"
	./test-docker-build.sh

test-api: ## Tester l'API backend
	@echo "$(BLUE)🔧 Test de l'API...$(NC)"
	@curl -s http://localhost:8001/api/health | jq . || curl -s http://localhost:8001/api/health

# === INFORMATIONS ===

info: ## Afficher les informations du système
	@echo "$(BLUE)ℹ️  Informations système:$(NC)"
	@echo "• Docker: $$(docker --version)"
	@echo "• Docker Compose: $$(docker compose version)"
	@echo "• Espace disque: $$(df -h . | awk 'NR==2 {print $$4}') disponible"
	@echo "• Mémoire: $$(free -h | awk 'NR==2{printf "%.1f/%.1f GB", $$3/1024, $$2/1024}')"
	@if [ -f ".env" ]; then \
		echo "• Domaine configuré: $$(grep DOMAIN .env | cut -d '=' -f2)"; \
		echo "• Mode SSL: $$(grep SSL_ENABLED .env | cut -d '=' -f2)"; \
	fi

urls: ## Afficher les URLs d'accès
	@echo "$(BLUE)🌐 URLs d'accès:$(NC)"
	@if [ -f ".env" ]; then \
		DOMAIN=$$(grep DOMAIN .env | cut -d '=' -f2); \
		SSL_ENABLED=$$(grep SSL_ENABLED .env | cut -d '=' -f2); \
		echo "• Application: http://$$DOMAIN"; \
		[ "$$SSL_ENABLED" = "true" ] && echo "• HTTPS: https://$$DOMAIN"; \
		echo "• API: http://$$DOMAIN/api"; \
		echo "• Local: http://localhost"; \
	else \
		echo "$(RED)❌ Configuration non trouvée - lancez 'make install'$(NC)"; \
	fi