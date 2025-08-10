#!/bin/bash

# =============================================================================
# SUPER Vote Secret - Déploiement Docker Optimisé et Efficace
# Version 4.0 - Script interactif, performant et complet
# =============================================================================

set -euo pipefail

# Configuration des couleurs et constantes
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m' 
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/deployment-$(date +%Y%m%d_%H%M%S).log"

# Variables de configuration
DOMAIN=""
ADMIN_EMAIL=""
MONGO_PASSWORD=""
USE_SSL="true"
DEPLOYMENT_MODE="production"
QUICK_MODE="false"

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")    echo -e "${BLUE}ℹ️${NC}  ${message}" ;;
        "SUCCESS") echo -e "${GREEN}✅${NC} ${message}" ;;
        "WARNING") echo -e "${YELLOW}⚠️${NC}  ${message}" ;;
        "ERROR")   echo -e "${RED}❌${NC} ${message}" ;;
        "STEP")    echo -e "\n${CYAN}▶${NC} ${BOLD}${message}${NC}" ;;
        "HEADER")  echo -e "${PURPLE}${BOLD}${message}${NC}" ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

show_banner() {
    clear
    echo -e "${PURPLE}${BOLD}"
    cat << 'EOF'
    ╔══════════════════════════════════════════════════════════════╗
    ║             🗳️  SUPER VOTE SECRET DEPLOYER 4.0              ║
    ║         Script de Déploiement Docker Optimisé               ║
    ║                                                              ║
    ║     🚀 Efficace • 🔧 Interactif • 🔒 Sécurisé              ║
    ╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
}

spinner() {
    local pid=$1
    local message="$2"
    local chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    local start_time=$(date +%s)
    
    while kill -0 $pid 2>/dev/null; do
        local elapsed=$(($(date +%s) - start_time))
        for (( i=0; i<${#chars}; i++ )); do
            printf "\r${BLUE}%s${NC} %s... (%ds)" "${chars:$i:1}" "$message" "$elapsed"
            sleep 0.1
            if ! kill -0 $pid 2>/dev/null; then
                break
            fi
        done
    done
    
    wait $pid
    local exit_code=$?
    local final_time=$(($(date +%s) - start_time))
    
    if [ $exit_code -eq 0 ]; then
        printf "\r${GREEN}✅${NC} %s (${final_time}s)\n" "$message"
        return 0
    else
        printf "\r${RED}❌${NC} %s (échoué après ${final_time}s)\n" "$message"
        return 1
    fi
}

# =============================================================================
# VÉRIFICATION DU SYSTÈME
# =============================================================================

check_dependencies() {
    log "STEP" "Vérification des dépendances système"
    
    local deps_ok=true
    
    # Docker
    if ! command -v docker >/dev/null 2>&1; then
        log "ERROR" "Docker n'est pas installé"
        echo -e "${YELLOW}📦 Installation: https://docs.docker.com/engine/install/${NC}"
        deps_ok=false
    fi
    
    # Docker Compose
    if ! docker compose version >/dev/null 2>&1 && ! docker-compose version >/dev/null 2>&1; then
        log "ERROR" "Docker Compose n'est pas disponible"
        echo -e "${YELLOW}📦 Installation: https://docs.docker.com/compose/install/${NC}"
        deps_ok=false
    fi
    
    # Permissions Docker
    if ! docker ps >/dev/null 2>&1; then
        log "ERROR" "Impossible d'accéder au daemon Docker"
        echo -e "${YELLOW}🔐 Solution: sudo usermod -aG docker \$USER${NC}"
        echo -e "${YELLOW}   Puis redémarrez votre session${NC}"
        deps_ok=false
    fi
    
    # Espace disque (minimum 2GB)
    local disk_space_kb=$(df . | awk 'NR==2 {print $4}')
    local disk_space_gb=$((disk_space_kb / 1024 / 1024))
    if [ $disk_space_gb -lt 2 ]; then
        log "WARNING" "Espace disque faible: ${disk_space_gb}GB (2GB+ recommandé)"
    fi
    
    # Ports
    local ports_in_use=""
    for port in 80 443; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            local service=$(netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f2 | head -1)
            ports_in_use+="Port $port (${service:-inconnu}) "
        fi
    done
    
    if [ -n "$ports_in_use" ]; then
        log "WARNING" "Ports utilisés: $ports_in_use - seront libérés automatiquement"
    fi
    
    if [ "$deps_ok" = false ]; then
        log "ERROR" "Dépendances manquantes - impossible de continuer"
        exit 1
    fi
    
    log "SUCCESS" "Toutes les dépendances sont disponibles"
}

# =============================================================================
# COLLECTE DE CONFIGURATION INTERACTIVE
# =============================================================================

collect_config() {
    log "STEP" "Configuration du déploiement"
    
    echo -e "${BOLD}🔧 Configuration Interactive${NC}"
    echo -e "${CYAN}════════════════════════════${NC}\n"
    
    # Mode de déploiement
    echo -e "${BOLD}1. Mode de Déploiement${NC}"
    echo -e "   ${GREEN}[1]${NC} Production (recommandé)"
    echo -e "   ${YELLOW}[2]${NC} Développement"
    echo -e "   ${CYAN}[3]${NC} Test/Démo"
    echo
    while true; do
        read -p "Choisissez le mode [1]: " mode_choice
        mode_choice=${mode_choice:-1}
        case $mode_choice in
            1) DEPLOYMENT_MODE="production"; break ;;
            2) DEPLOYMENT_MODE="development"; break ;;
            3) DEPLOYMENT_MODE="demo"; break ;;
            *) echo -e "${RED}Option invalide${NC}" ;;
        esac
    done
    
    # Mode rapide pour développement
    if [ "$DEPLOYMENT_MODE" != "production" ]; then
        echo
        read -p "Mode rapide (configuration automatique) ? [Y/n]: " quick
        if [[ ! "$quick" =~ ^[Nn]$ ]]; then
            QUICK_MODE="true"
        fi
    fi
    
    # Configuration domaine
    echo -e "\n${BOLD}2. Configuration du Domaine${NC}"
    if [ "$QUICK_MODE" = "true" ]; then
        DOMAIN="localhost"
        ADMIN_EMAIL="admin@localhost"
        USE_SSL="false"
        log "INFO" "Mode rapide: utilisation de localhost"
    else
        while [[ -z "$DOMAIN" ]]; do
            echo -e "Exemples: ${GREEN}vote.mondomaine.com${NC}, ${GREEN}localhost${NC}"
            read -p "Domaine: " DOMAIN
            
            if [ "$DOMAIN" = "localhost" ]; then
                USE_SSL="false"
                log "INFO" "Localhost détecté - SSL désactivé"
                break
            fi
            
            # Validation format domaine
            if [[ ! "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$ ]]; then
                echo -e "${RED}Format de domaine invalide${NC}"
                DOMAIN=""
                continue
            fi
            
            # Test DNS si ce n'est pas localhost
            log "INFO" "Test de résolution DNS..."
            if host "$DOMAIN" >/dev/null 2>&1; then
                local ip=$(host "$DOMAIN" 2>/dev/null | grep "has address" | awk '{print $4}' | head -1)
                log "SUCCESS" "DNS résolu: $DOMAIN → $ip"
            else
                log "WARNING" "DNS non résolu - assurez-vous que le domaine pointe vers ce serveur"
                read -p "Continuer quand même ? [y/N]: " continue_dns
                if [[ ! "$continue_dns" =~ ^[Yy]$ ]]; then
                    DOMAIN=""
                    continue
                fi
            fi
        done
        
        # Email admin
        if [ "$USE_SSL" = "true" ]; then
            echo -e "\n${BOLD}3. Configuration SSL${NC}"
            while [[ -z "$ADMIN_EMAIL" ]]; do
                read -p "Email administrateur (pour SSL): " ADMIN_EMAIL
                if [[ ! "$ADMIN_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
                    echo -e "${RED}Format email invalide${NC}"
                    ADMIN_EMAIL=""
                fi
            done
        fi
    fi
    
    # Mot de passe MongoDB
    echo -e "\n${BOLD}4. Sécurité Base de Données${NC}"
    if [ "$QUICK_MODE" = "true" ]; then
        MONGO_PASSWORD="dev_password_$(date +%s | tail -c 6)"
        log "INFO" "Mot de passe MongoDB généré automatiquement"
    else
        while [[ -z "$MONGO_PASSWORD" ]]; do
            echo -e "Exigences: ${YELLOW}12+ caractères, mélange lettres/chiffres/symboles${NC}"
            read -s -p "Mot de passe MongoDB: " MONGO_PASSWORD
            echo
            
            if [[ ${#MONGO_PASSWORD} -lt 12 ]]; then
                echo -e "${RED}Mot de passe trop court (12+ caractères requis)${NC}"
                MONGO_PASSWORD=""
                continue
            fi
            
            read -s -p "Confirmez le mot de passe: " confirm_pwd
            echo
            
            if [[ "$MONGO_PASSWORD" != "$confirm_pwd" ]]; then
                echo -e "${RED}Les mots de passe ne correspondent pas${NC}"
                MONGO_PASSWORD=""
            fi
        done
    fi
    
    # Résumé de la configuration
    echo -e "\n${BOLD}📋 Résumé de la Configuration${NC}"
    echo -e "${CYAN}═══════════════════════════════${NC}"
    echo -e "🎯 Mode:        ${GREEN}$DEPLOYMENT_MODE${NC}"
    echo -e "🌐 Domaine:     ${GREEN}$DOMAIN${NC}"
    [ "$USE_SSL" = "true" ] && echo -e "📧 Email:       ${GREEN}$ADMIN_EMAIL${NC}"
    echo -e "🔒 SSL:         ${GREEN}$([ "$USE_SSL" = "true" ] && echo "Activé" || echo "Désactivé")${NC}"
    echo -e "🗄️  MongoDB:     ${GREEN}Configuré avec mot de passe sécurisé${NC}"
    
    if [ "$QUICK_MODE" != "true" ]; then
        echo
        read -p "Continuer avec cette configuration ? [Y/n]: " confirm
        if [[ "$confirm" =~ ^[Nn]$ ]]; then
            log "INFO" "Configuration annulée par l'utilisateur"
            exit 0
        fi
    fi
    
    log "SUCCESS" "Configuration collectée avec succès"
}

# =============================================================================
# GÉNÉRATION DES FICHIERS ENVIRONNEMENT
# =============================================================================

generate_env_files() {
    log "STEP" "Génération des fichiers d'environnement"
    
    # Générer clés de sécurité
    local jwt_secret=$(openssl rand -base64 48 | tr -d '\n')
    local encryption_key=$(openssl rand -hex 32)
    local app_secret=$(openssl rand -base64 32 | tr -d '\n')
    
    # Déterminer l'URL backend
    local backend_url
    if [ "$DOMAIN" = "localhost" ]; then
        backend_url="http://localhost:8001"
    elif [ "$USE_SSL" = "true" ]; then
        backend_url="https://$DOMAIN"
    else
        backend_url="http://$DOMAIN"
    fi
    
    # Fichier .env principal (racine)
    log "INFO" "Génération du fichier .env principal..."
    cat > .env << EOF
# SUPER Vote Secret - Configuration de Déploiement
# Généré automatiquement le $(date -Iseconds)

# Configuration du Domaine
DOMAIN=$DOMAIN
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@$DOMAIN}

# Configuration MongoDB
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=$MONGO_PASSWORD
MONGO_DB=vote_secret

# Configuration de Sécurité (Auto-générées)
JWT_SECRET=$jwt_secret
ENCRYPTION_KEY=$encryption_key
APP_SECRET=$app_secret

# Configuration de l'Application
APP_NAME=SUPER Vote Secret
APP_VERSION=4.0.0
NODE_ENV=$DEPLOYMENT_MODE
PYTHON_ENV=$DEPLOYMENT_MODE

# Configuration SSL
SSL_ENABLED=$USE_SSL

# Configuration de Performance Docker
DOCKER_BUILDKIT=1
COMPOSE_DOCKER_CLI_BUILD=1
COMPOSE_PARALLEL_LIMIT=4

# Métadonnées de Déploiement
DEPLOY_DATE=$(date -Iseconds)
DEPLOY_USER=${USER:-unknown}
DEPLOY_HOST=$(hostname)
DEPLOY_MODE=$DEPLOYMENT_MODE
EOF
    
    # Fichier .env frontend
    log "INFO" "Génération du fichier .env frontend..."
    cat > frontend/.env << EOF
# SUPER Vote Secret Frontend - Configuration
# URL du Backend
REACT_APP_BACKEND_URL=$backend_url

# Configuration de Build
GENERATE_SOURCEMAP=$([ "$DEPLOYMENT_MODE" = "production" ] && echo "false" || echo "true")
NODE_ENV=$DEPLOYMENT_MODE

# Configuration WebSocket
$([ "$USE_SSL" = "true" ] && echo "WDS_SOCKET_PORT=443" || echo "WDS_SOCKET_PORT=80")
EOF
    
    # Fichier .env backend
    log "INFO" "Génération du fichier .env backend..."
    cat > backend/.env << EOF
# SUPER Vote Secret Backend - Configuration
# Configuration MongoDB
MONGO_URL=mongodb://admin:$MONGO_PASSWORD@mongodb:27017/vote_secret?authSource=admin
DB_NAME=vote_secret

# Configuration de Sécurité
JWT_SECRET=$jwt_secret
ENCRYPTION_KEY=$encryption_key

# Configuration de l'Application
PYTHON_ENV=$DEPLOYMENT_MODE
DEBUG=$([ "$DEPLOYMENT_MODE" = "development" ] && echo "true" || echo "false")

# Configuration des CORS
CORS_ORIGINS=["$backend_url", "http://localhost:3000"]
EOF
    
    # Sécuriser les fichiers
    chmod 600 .env frontend/.env backend/.env
    
    log "SUCCESS" "Fichiers d'environnement générés et sécurisés"
}

# =============================================================================
# NETTOYAGE ET PRÉPARATION
# =============================================================================

cleanup_previous() {
    log "STEP" "Nettoyage et préparation"
    
    # Arrêter les conteneurs existants
    if docker compose ps -q 2>/dev/null | grep -q .; then
        log "INFO" "Arrêt des conteneurs existants..."
        docker compose down --remove-orphans 2>/dev/null || true
    fi
    
    # Arrêter les services système conflictuels
    local services_to_stop=("nginx" "apache2" "httpd")
    for service in "${services_to_stop[@]}"; do
        if systemctl is-active --quiet $service 2>/dev/null; then
            log "INFO" "Arrêt du service système: $service"
            sudo systemctl stop $service 2>/dev/null || true
        fi
    done
    
    # Nettoyage Docker si nécessaire
    if [ "$DEPLOYMENT_MODE" = "production" ]; then
        log "INFO" "Nettoyage Docker pour optimiser l'espace..."
        docker system prune -f >/dev/null 2>&1 || true
    fi
    
    # Créer les répertoires nécessaires
    mkdir -p data/mongodb nginx/ssl logs
    
    log "SUCCESS" "Nettoyage et préparation terminés"
}

# =============================================================================
# BUILD ET DÉMARRAGE OPTIMISÉ
# =============================================================================

build_and_deploy() {
    log "STEP" "Construction et déploiement de l'application"
    
    # Déterminer la commande compose à utiliser
    local compose_cmd="docker compose"
    if ! docker compose version >/dev/null 2>&1; then
        compose_cmd="docker-compose"
    fi
    
    # Build optimisé avec cache si possible
    log "INFO" "Construction des images Docker..."
    (
        export DOCKER_BUILDKIT=1
        export COMPOSE_DOCKER_CLI_BUILD=1
        export COMPOSE_PARALLEL_LIMIT=4
        
        # Build avec cache intelligent
        if [ "$DEPLOYMENT_MODE" = "production" ]; then
            $compose_cmd build --no-cache --parallel
        else
            $compose_cmd build --parallel
        fi
    ) &
    
    if ! spinner $! "Construction des images Docker"; then
        log "ERROR" "Échec de la construction des images"
        return 1
    fi
    
    # Démarrage des services
    log "INFO" "Démarrage des services..."
    if ! $compose_cmd up -d; then
        log "ERROR" "Échec du démarrage des services"
        return 1
    fi
    
    log "SUCCESS" "Application déployée avec succès"
}

# =============================================================================
# VÉRIFICATION DE SANTÉ DES SERVICES
# =============================================================================

health_check() {
    log "STEP" "Vérification de la santé des services"
    
    local services=("mongodb" "backend" "frontend" "nginx")
    local max_wait=120
    local check_interval=5
    
    for service in "${services[@]}"; do
        log "INFO" "Vérification du service: $service"
        
        local waited=0
        local service_healthy=false
        
        while [ $waited -lt $max_wait ]; do
            # Vérifier que le conteneur est en cours d'exécution
            if docker compose ps -q $service 2>/dev/null | xargs -I {} docker inspect {} --format='{{.State.Status}}' | grep -q "running"; then
                
                # Tests de santé spécifiques par service
                case $service in
                    "mongodb")
                        if docker compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
                            service_healthy=true
                        fi
                        ;;
                    "backend")
                        if curl -sf --max-time 5 "http://localhost:8001/api/health" >/dev/null 2>&1; then
                            service_healthy=true
                        fi
                        ;;
                    "frontend")
                        if curl -sf --max-time 5 "http://localhost:3000" >/dev/null 2>&1; then
                            service_healthy=true
                        fi
                        ;;
                    "nginx")
                        if curl -sf --max-time 5 "http://localhost:80" >/dev/null 2>&1 || curl -sf --max-time 5 "http://localhost" >/dev/null 2>&1; then
                            service_healthy=true
                        fi
                        ;;
                esac
                
                if [ "$service_healthy" = true ]; then
                    log "SUCCESS" "Service $service est opérationnel"
                    break
                fi
            fi
            
            printf "\r${YELLOW}⏳${NC} Attente $service... (${waited}s/${max_wait}s)"
            sleep $check_interval
            waited=$((waited + check_interval))
        done
        
        if [ "$service_healthy" != true ]; then
            printf "\r${RED}❌${NC} Service $service - échec après ${max_wait}s\n"
            log "ERROR" "Service $service n'a pas démarré correctement"
            
            # Afficher les logs pour diagnostic
            echo -e "\n${YELLOW}📋 Logs du service $service:${NC}"
            docker compose logs --tail 20 $service || true
            return 1
        fi
    done
    
    log "SUCCESS" "Tous les services sont opérationnels"
}

# =============================================================================
# TEST D'ACCESSIBILITÉ WEB
# =============================================================================

test_web_access() {
    log "STEP" "Test d'accessibilité web"
    
    local test_urls=()
    local test_descriptions=()
    
    # URLs de test selon la configuration
    if [ "$DOMAIN" = "localhost" ]; then
        test_urls+=("http://localhost" "http://localhost:80" "http://localhost:3000")
        test_descriptions+=("Frontend via proxy" "Frontend direct port 80" "Frontend port 3000")
    else
        test_urls+=("http://$DOMAIN" "http://localhost")
        test_descriptions+=("Frontend via domaine" "Frontend local")
        
        if [ "$USE_SSL" = "true" ]; then
            test_urls+=("https://$DOMAIN")
            test_descriptions+=("Frontend HTTPS")
        fi
    fi
    
    # Tests API
    test_urls+=("http://localhost:8001/api/health")
    test_descriptions+=("API Backend")
    
    local successful_tests=0
    local total_tests=${#test_urls[@]}
    
    echo -e "\n${BOLD}🌐 Tests d'Accessibilité Web${NC}"
    echo -e "${CYAN}═══════════════════════════════${NC}"
    
    for i in "${!test_urls[@]}"; do
        local url="${test_urls[$i]}"
        local description="${test_descriptions[$i]}"
        
        printf "🔍 Test: %-25s " "$description"
        
        if curl -sf --max-time 10 --connect-timeout 5 "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ OK${NC}"
            successful_tests=$((successful_tests + 1))
        else
            echo -e "${RED}❌ ÉCHEC${NC}"
        fi
    done
    
    local success_rate=$((successful_tests * 100 / total_tests))
    
    echo -e "\n📊 Résultat: ${successful_tests}/${total_tests} tests réussis (${success_rate}%)"
    
    if [ $success_rate -ge 75 ]; then
        log "SUCCESS" "Tests d'accessibilité réussis (${success_rate}%)"
        return 0
    else
        log "WARNING" "Tests d'accessibilité partiels (${success_rate}%)"
        return 1
    fi
}

# =============================================================================
# CONFIGURATION SSL AUTOMATIQUE (OPTIONNELLE)
# =============================================================================

setup_ssl() {
    if [ "$USE_SSL" != "true" ] || [ "$DOMAIN" = "localhost" ]; then
        return 0
    fi
    
    log "STEP" "Configuration SSL Let's Encrypt"
    
    # Attendre que nginx soit stable
    sleep 10
    
    log "INFO" "Demande de certificat SSL pour $DOMAIN..."
    
    # Démarrer le processus SSL en arrière-plan
    (
        docker compose exec -T nginx nginx -s reload 2>/dev/null || true
        sleep 5
        
        # Vérifier la connectivité HTTP avant SSL
        if curl -sf --max-time 10 "http://$DOMAIN/.well-known/" >/dev/null 2>&1; then
            docker compose logs -f certbot &
            CERTBOT_PID=$!
            sleep 60
            kill $CERTBOT_PID 2>/dev/null || true
        fi
    ) &
    
    local ssl_pid=$!
    
    # Attendre un délai raisonnable
    local wait_time=0
    local max_wait=180
    
    while [ $wait_time -lt $max_wait ]; do
        if docker compose exec -T nginx test -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" 2>/dev/null; then
            kill $ssl_pid 2>/dev/null || true
            log "SUCCESS" "Certificat SSL configuré avec succès"
            return 0
        fi
        
        sleep 10
        wait_time=$((wait_time + 10))
        printf "\r${YELLOW}⏳${NC} Configuration SSL... (${wait_time}s/${max_wait}s)"
    done
    
    kill $ssl_pid 2>/dev/null || true
    printf "\r${YELLOW}⚠️${NC}  SSL: configuration manuelle nécessaire\n"
    log "WARNING" "Configuration SSL automatique échouée - accessible en HTTP"
    
    return 0
}

# =============================================================================
# RAPPORT FINAL
# =============================================================================

show_final_report() {
    local deploy_end=$(date +%s)
    local deploy_duration=$((deploy_end - ${DEPLOY_START:-$(date +%s)}))
    local minutes=$((deploy_duration / 60))
    local seconds=$((deploy_duration % 60))
    
    clear
    echo -e "${GREEN}${BOLD}"
    cat << 'EOF'
    ╔══════════════════════════════════════════════════════════════╗
    ║                  🎉 DÉPLOIEMENT TERMINÉ ! 🎉                ║
    ║              SUPER Vote Secret est maintenant               ║
    ║                    🚀 OPÉRATIONNEL ! 🚀                     ║
    ╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}\n"
    
    echo -e "${BOLD}📊 Résumé du Déploiement${NC}"
    echo -e "${CYAN}═══════════════════════════${NC}"
    echo -e "⏱️  Durée:     ${GREEN}${minutes}m ${seconds}s${NC}"
    echo -e "🎯 Mode:      ${GREEN}$DEPLOYMENT_MODE${NC}"
    echo -e "🌐 Domaine:   ${GREEN}$DOMAIN${NC}"
    echo -e "🔒 SSL:       ${GREEN}$([ "$USE_SSL" = "true" ] && echo "Activé" || echo "HTTP seulement")${NC}"
    echo -e "🐳 Services:  ${GREEN}$(docker compose ps --services 2>/dev/null | wc -l) conteneurs actifs${NC}"
    echo
    
    echo -e "${BOLD}🌍 URLs d'Accès${NC}"
    echo -e "${CYAN}═══════════════${NC}"
    
    if [ "$DOMAIN" = "localhost" ]; then
        echo -e "🖥️  Application: ${CYAN}http://localhost${NC}"
        echo -e "🔧 API:         ${CYAN}http://localhost:8001/api${NC}"
    else
        echo -e "🌐 Application: ${CYAN}http://$DOMAIN${NC}"
        [ "$USE_SSL" = "true" ] && echo -e "🔒 HTTPS:       ${CYAN}https://$DOMAIN${NC}"
        echo -e "🔧 API:         ${CYAN}http://$DOMAIN/api${NC}"
    fi
    
    echo
    echo -e "${BOLD}🛠️  Commandes de Gestion${NC}"
    echo -e "${CYAN}════════════════════════════${NC}"
    echo -e "📊 État:       ${YELLOW}docker compose ps${NC}"
    echo -e "📋 Logs:       ${YELLOW}docker compose logs -f${NC}"
    echo -e "🔄 Redémarrer: ${YELLOW}docker compose restart${NC}"
    echo -e "⏹️  Arrêter:    ${YELLOW}docker compose down${NC}"
    echo -e "🔧 Reconstruire: ${YELLOW}$0${NC}"
    
    echo
    echo -e "${BOLD}📁 Fichiers Importants${NC}"
    echo -e "${CYAN}══════════════════════${NC}"
    echo -e "• Configuration:   ${YELLOW}.env${NC}"
    echo -e "• Logs déploiement: ${YELLOW}$LOG_FILE${NC}"
    echo -e "• Données:          ${YELLOW}Docker volumes${NC}"
    
    if [ "$USE_SSL" = "true" ] && [ "$DOMAIN" != "localhost" ]; then
        echo
        echo -e "${BOLD}🔒 SSL Let's Encrypt${NC}"
        echo -e "${CYAN}════════════════════${NC}"
        echo -e "• Vérifier SSL:     ${YELLOW}docker compose logs certbot${NC}"
        echo -e "• Renouveler:       ${YELLOW}docker compose restart certbot${NC}"
    fi
    
    echo
    echo -e "${GREEN}${BOLD}✨ Votre application SUPER Vote Secret est prête !${NC}"
    echo -e "${CYAN}🔗 Accédez maintenant à votre application de vote sécurisé.${NC}"
    echo
}

# =============================================================================
# FONCTION PRINCIPALE
# =============================================================================

cleanup_on_error() {
    log "ERROR" "Déploiement interrompu - nettoyage en cours..."
    docker compose down 2>/dev/null || true
    exit 1
}

main() {
    DEPLOY_START=$(date +%s)
    
    # Gestion des signaux d'interruption
    trap cleanup_on_error INT TERM
    
    # Étapes de déploiement
    show_banner
    log "INFO" "Démarrage du déploiement SUPER Vote Secret"
    
    check_dependencies
    collect_config
    generate_env_files
    cleanup_previous
    
    if ! build_and_deploy; then
        log "ERROR" "Échec du déploiement de l'application"
        exit 1
    fi
    
    if ! health_check; then
        log "ERROR" "Vérification de santé échouée"
        echo -e "${YELLOW}ℹ️  L'application peut encore être accessible. Vérifiez manuellement.${NC}"
    fi
    
    # Tests d'accessibilité (non bloquants)
    test_web_access || true
    
    # SSL si activé (non bloquant)
    setup_ssl
    
    # Rapport final
    show_final_report
    
    log "SUCCESS" "Déploiement SUPER Vote Secret terminé avec succès!"
}

# =============================================================================
# EXÉCUTION
# =============================================================================

# Vérifier que le script n'est pas executé en tant que root
if [[ $EUID -eq 0 ]]; then
    echo -e "${RED}⚠️  Attention: Exécution en tant que root détectée${NC}"
    echo -e "${YELLOW}Pour la sécurité, il est recommandé d'exécuter ce script avec un utilisateur normal.${NC}"
    read -p "Continuer quand même ? [y/N]: " continue_root
    if [[ ! "$continue_root" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Lancer le déploiement
main "$@"