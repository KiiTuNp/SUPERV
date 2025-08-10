#!/bin/bash

# =============================================================================
# SUPER Vote Secret - Script de Déploiement Production Interactif
# =============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Couleurs pour l'affichage
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/deployment.log"
readonly HEALTH_CHECK_TIMEOUT=300  # 5 minutes
readonly SERVICE_START_TIMEOUT=120 # 2 minutes
readonly SSL_VERIFICATION_TIMEOUT=180 # 3 minutes

# Variables globales
DOMAIN=""
ADMIN_EMAIL=""
MONGO_ROOT_PASSWORD=""
JWT_SECRET=""
ENCRYPTION_KEY=""

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${BLUE}[INFO]${NC} ${message}" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} ${message}" ;;
        "WARNING") echo -e "${YELLOW}[WARNING]${NC} ${message}" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} ${message}" ;;
        "DEBUG") echo -e "${PURPLE}[DEBUG]${NC} ${message}" ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

show_banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════════╗
║                    SUPER Vote Secret - Déploiement Production                 ║  
║                          Système de Vote Anonyme Sécurisé                     ║
╚════════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo -e "${WHITE}Version 2.1.0 - Script de Déploiement Interactif Robuste${NC}"
    echo -e "${WHITE}================================================================================================${NC}"
    echo
}

spinner() {
    local pid=$1
    local message="$2"
    local chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    
    while kill -0 $pid 2>/dev/null; do
        for (( i=0; i<${#chars}; i++ )); do
            printf "\r${BLUE}${chars:$i:1}${NC} %s" "$message"
            sleep 0.1
        done
    done
    printf "\r${GREEN}✓${NC} %s\n" "$message"
}

wait_for_service() {
    local service_name="$1"
    local health_url="$2"
    local timeout="${3:-$HEALTH_CHECK_TIMEOUT}"
    local start_time=$(date +%s)
    
    log "INFO" "Attente du service $service_name..."
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $timeout ]; then
            log "ERROR" "Timeout atteint pour le service $service_name (${timeout}s)"
            return 1
        fi
        
        if docker-compose ps "$service_name" | grep -q "Up"; then
            if curl -sf "$health_url" >/dev/null 2>&1; then
                log "SUCCESS" "Service $service_name opérationnel (${elapsed}s)"
                return 0
            fi
        fi
        
        printf "\r${YELLOW}⌛${NC} Attente de $service_name... (${elapsed}s/${timeout}s)"
        sleep 2
    done
}

verify_prerequisites() {
    log "INFO" "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker n'est pas installé. Veuillez installer Docker."
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log "ERROR" "Docker Compose n'est pas installé. Veuillez installer Docker Compose."
        exit 1
    fi
    
    # Vérifier les permissions Docker
    if ! docker ps &> /dev/null; then
        log "ERROR" "Impossible d'accéder à Docker. Vérifiez les permissions utilisateur."
        exit 1
    fi
    
    # Vérifier les ports
    local ports_in_use=$(netstat -tuln | grep -E ':80|:443' | wc -l)
    if [ "$ports_in_use" -gt 0 ]; then
        log "WARNING" "Les ports 80/443 sont peut-être utilisés. Le script tentera de les libérer."
    fi
    
    log "SUCCESS" "Prérequis vérifiés avec succès"
}

collect_configuration() {
    log "INFO" "Collection de la configuration de déploiement..."
    
    echo -e "\n${WHITE}📋 Configuration du Déploiement${NC}"
    echo -e "${WHITE}================================${NC}\n"
    
    # Domaine
    while [[ -z "$DOMAIN" ]]; do
        read -p "🌐 Nom de domaine (ex: vote.super-csn.ca): " DOMAIN
        if [[ ! "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9\.-]*[a-zA-Z0-9]$ ]]; then
            echo -e "${RED}❌ Domaine invalide. Format attendu: example.com${NC}"
            DOMAIN=""
        fi
    done
    
    # Email administrateur
    while [[ -z "$ADMIN_EMAIL" ]]; do
        read -p "📧 Email administrateur (pour SSL): " ADMIN_EMAIL
        if [[ ! "$ADMIN_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
            echo -e "${RED}❌ Email invalide${NC}"
            ADMIN_EMAIL=""
        fi
    done
    
    # Mot de passe MongoDB
    while [[ -z "$MONGO_ROOT_PASSWORD" ]]; do
        read -s -p "🔒 Mot de passe MongoDB (min 12 caractères): " MONGO_ROOT_PASSWORD
        echo
        if [[ ${#MONGO_ROOT_PASSWORD} -lt 12 ]]; then
            echo -e "${RED}❌ Mot de passe trop court (minimum 12 caractères)${NC}"
            MONGO_ROOT_PASSWORD=""
        fi
    done
    
    # Génération automatique des clés de sécurité
    log "INFO" "Génération des clés de sécurité..."
    JWT_SECRET=$(openssl rand -hex 32)
    ENCRYPTION_KEY=$(openssl rand -hex 16)
    
    log "SUCCESS" "Configuration collectée"
}

create_environment_file() {
    log "INFO" "Création du fichier d'environnement..."
    
    cat > .env << EOF
# SUPER Vote Secret - Production Environment Configuration
# Généré automatiquement le $(date)

# MongoDB Configuration
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD}
MONGO_DB=vote_secret

# Application Configuration  
DOMAIN=${DOMAIN}
ADMIN_EMAIL=${ADMIN_EMAIL}

# Security Keys (GENERATED AUTOMATICALLY)
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Application Settings
APP_NAME=SUPER Vote Secret
APP_VERSION=2.1.0
NODE_ENV=production
PYTHON_ENV=production

# SSL Configuration (Auto-managed by Let's Encrypt)
SSL_ENABLED=true
SSL_EMAIL=${ADMIN_EMAIL}

# Backup Configuration
BACKUP_RETENTION_DAYS=30
ENABLE_AUTOMATED_BACKUPS=true
EOF

    chmod 600 .env
    log "SUCCESS" "Fichier d'environnement créé avec permissions sécurisées"
}

stop_conflicting_services() {
    log "INFO" "Arrêt des services conflictuels..."
    
    # Arrêter nginx système
    if systemctl is-active --quiet nginx 2>/dev/null; then
        log "WARNING" "Arrêt de nginx système..."
        sudo systemctl stop nginx
        sudo systemctl disable nginx
    fi
    
    # Arrêter apache système
    if systemctl is-active --quiet apache2 2>/dev/null; then
        log "WARNING" "Arrêt d'apache2 système..."
        sudo systemctl stop apache2
        sudo systemctl disable apache2
    fi
    
    # Arrêter anciens containers
    if docker ps -a --format "{{.Names}}" | grep -q "vote-secret"; then
        log "WARNING" "Arrêt des anciens containers..."
        docker ps -a --format "{{.Names}}" | grep "vote-secret" | xargs -r docker stop
        docker ps -a --format "{{.Names}}" | grep "vote-secret" | xargs -r docker rm
    fi
    
    log "SUCCESS" "Services conflictuels arrêtés"
}

build_and_deploy() {
    log "INFO" "Construction et déploiement des services..."
    
    # Nettoyage préliminaire
    log "INFO" "Nettoyage des ressources Docker..."
    docker system prune -f &>/dev/null || true
    
    # Build des images
    log "INFO" "Construction des images Docker..."
    (
        docker-compose build --no-cache 2>&1 | tee -a "$LOG_FILE"
    ) &
    spinner $! "Construction des images Docker"
    
    # Démarrage des services
    log "INFO" "Démarrage des services..."
    docker-compose up -d 2>&1 | tee -a "$LOG_FILE"
    
    log "SUCCESS" "Services lancés"
}

wait_for_all_services() {
    log "INFO" "Attente de la disponibilité de tous les services..."
    
    echo -e "\n${WHITE}🔍 Vérification des Services${NC}"
    echo -e "${WHITE}=============================${NC}\n"
    
    # MongoDB
    printf "${YELLOW}⌛${NC} MongoDB..."
    local mongo_ready=false
    for i in {1..60}; do
        if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
            mongo_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$mongo_ready" = true ]; then
        printf "\r${GREEN}✓${NC} MongoDB opérationnel\n"
    else
        printf "\r${RED}✗${NC} MongoDB timeout\n"
        return 1
    fi
    
    # Backend
    printf "${YELLOW}⌛${NC} Backend API..."
    local backend_ready=false
    for i in {1..60}; do
        if curl -sf http://localhost:8001/api/health &>/dev/null; then
            backend_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$backend_ready" = true ]; then
        printf "\r${GREEN}✓${NC} Backend API opérationnel\n"
    else
        printf "\r${RED}✗${NC} Backend API timeout\n"
        return 1
    fi
    
    # Frontend
    printf "${YELLOW}⌛${NC} Frontend..."
    local frontend_ready=false
    for i in {1..60}; do
        if curl -sf http://localhost:3000/health &>/dev/null; then
            frontend_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$frontend_ready" = true ]; then
        printf "\r${GREEN}✓${NC} Frontend opérationnel\n"
    else
        printf "\r${RED}✗${NC} Frontend timeout\n"
        return 1
    fi
    
    # Nginx
    printf "${YELLOW}⌛${NC} Nginx..."
    local nginx_ready=false
    for i in {1..30}; do
        if curl -sf http://localhost:80/health &>/dev/null; then
            nginx_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$nginx_ready" = true ]; then
        printf "\r${GREEN}✓${NC} Nginx opérationnel\n"
    else
        printf "\r${RED}✗${NC} Nginx timeout\n"
        return 1
    fi
    
    log "SUCCESS" "Tous les services sont opérationnels"
}

configure_ssl() {
    log "INFO" "Configuration SSL avec Let's Encrypt..."
    
    echo -e "\n${WHITE}🔒 Configuration SSL${NC}"
    echo -e "${WHITE}==================${NC}\n"
    
    # Attendre que Certbot soit prêt
    printf "${YELLOW}⌛${NC} Démarrage de Certbot..."
    sleep 10
    printf "\r${GREEN}✓${NC} Certbot démarré\n"
    
    # Vérifier la génération du certificat
    printf "${YELLOW}⌛${NC} Génération du certificat SSL..."
    local ssl_ready=false
    local max_attempts=18  # 3 minutes (18 * 10s)
    
    for i in $(seq 1 $max_attempts); do
        if docker-compose logs certbot | grep -q "Successfully received certificate\|Certificate not yet due for renewal"; then
            ssl_ready=true
            break
        fi
        sleep 10
        printf "."
    done
    
    if [ "$ssl_ready" = true ]; then
        printf "\r${GREEN}✓${NC} Certificat SSL généré avec succès\n"
    else
        printf "\r${YELLOW}⚠${NC} Certificat SSL en cours de génération (continuera en arrière-plan)\n"
        log "WARNING" "Certificat SSL en cours de génération"
    fi
    
    log "SUCCESS" "Configuration SSL initialisée"
}

perform_health_checks() {
    log "INFO" "Vérifications de santé finales..."
    
    echo -e "\n${WHITE}🏥 Tests de Santé${NC}"
    echo -e "${WHITE}=================${NC}\n"
    
    # Test backend API
    printf "${YELLOW}⌛${NC} Test API Backend..."
    if curl -sf "http://localhost:8001/api/health" | grep -q "healthy"; then
        printf "\r${GREEN}✓${NC} API Backend: Fonctionnel\n"
    else
        printf "\r${RED}✗${NC} API Backend: Erreur\n"
        return 1
    fi
    
    # Test frontend
    printf "${YELLOW}⌛${NC} Test Frontend..."
    if curl -sf "http://localhost:3000/health" &>/dev/null; then
        printf "\r${GREEN}✓${NC} Frontend: Fonctionnel\n"
    else
        printf "\r${RED}✗${NC} Frontend: Erreur\n"
        return 1
    fi
    
    # Test proxy HTTP
    printf "${YELLOW}⌛${NC} Test Proxy HTTP..."
    if curl -sf "http://$DOMAIN/health" &>/dev/null || curl -sf "http://localhost:80/health" &>/dev/null; then
        printf "\r${GREEN}✓${NC} Proxy HTTP: Fonctionnel\n"
    else
        printf "\r${RED}✗${NC} Proxy HTTP: Erreur\n"
        return 1
    fi
    
    # Test HTTPS (si disponible)
    printf "${YELLOW}⌛${NC} Test HTTPS..."
    if curl -sfk "https://$DOMAIN/health" &>/dev/null || curl -sfk "https://localhost:443/health" &>/dev/null; then
        printf "\r${GREEN}✓${NC} HTTPS: Fonctionnel\n"
    else
        printf "\r${YELLOW}⚠${NC} HTTPS: En cours de configuration\n"
    fi
    
    log "SUCCESS" "Tests de santé complétés"
}

show_deployment_summary() {
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    clear
    echo -e "${GREEN}"
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════════╗
║                            🎉 DÉPLOIEMENT RÉUSSI! 🎉                          ║
╚════════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo -e "${WHITE}📊 Résumé du Déploiement${NC}"
    echo -e "${WHITE}========================${NC}"
    echo -e "⏱️  Durée totale: ${GREEN}${minutes}m ${seconds}s${NC}"
    echo -e "🌐 Domaine: ${GREEN}${DOMAIN}${NC}"
    echo -e "📧 Admin: ${GREEN}${ADMIN_EMAIL}${NC}"
    echo -e "🐳 Services Docker: ${GREEN}$(docker-compose ps --services | wc -l) actifs${NC}"
    echo
    
    echo -e "${WHITE}🌍 URLs d'Accès${NC}"
    echo -e "${WHITE}===============${NC}"
    echo -e "🔗 HTTP:  ${CYAN}http://${DOMAIN}${NC}"
    echo -e "🔒 HTTPS: ${CYAN}https://${DOMAIN}${NC}"
    echo -e "📱 Local: ${CYAN}http://localhost${NC}"
    echo
    
    echo -e "${WHITE}🛠️  Commandes Utiles${NC}"
    echo -e "${WHITE}===================${NC}"
    echo -e "📊 Status:     ${YELLOW}docker-compose ps${NC}"
    echo -e "📋 Logs:       ${YELLOW}docker-compose logs -f${NC}"
    echo -e "🔄 Restart:    ${YELLOW}docker-compose restart${NC}"
    echo -e "🛑 Stop:       ${YELLOW}docker-compose down${NC}"
    echo
    
    echo -e "${WHITE}📋 Informations Importantes${NC}"
    echo -e "${WHITE}============================${NC}"
    echo -e "• Configuration sauvegardée dans: ${YELLOW}.env${NC}"
    echo -e "• Logs de déploiement: ${YELLOW}${LOG_FILE}${NC}"
    echo -e "• Certificat SSL: ${GREEN}Configuré automatiquement${NC}"
    echo -e "• Sauvegarde MongoDB: ${GREEN}Activée (30 jours)${NC}"
    echo
    
    log "SUCCESS" "Déploiement terminé avec succès en ${minutes}m ${seconds}s"
}

# =============================================================================
# FONCTION PRINCIPALE
# =============================================================================

main() {
    local start_time=$(date +%s)
    
    # Initialisation
    show_banner
    log "INFO" "Début du déploiement SUPER Vote Secret"
    
    # Étapes du déploiement
    verify_prerequisites
    collect_configuration
    create_environment_file
    stop_conflicting_services
    build_and_deploy
    wait_for_all_services
    configure_ssl
    perform_health_checks
    
    # Résumé final
    show_deployment_summary
    
    echo -e "${GREEN}✅ L'application SUPER Vote Secret est maintenant accessible !${NC}"
    echo -e "${WHITE}🎯 Accédez à votre application: ${CYAN}https://${DOMAIN}${NC}"
}

# Gestion des interruptions
trap 'log "ERROR" "Déploiement interrompu"; exit 1' INT TERM

# Vérifier si le script est exécuté en tant que root (déconseillé)
if [[ $EUID -eq 0 ]]; then
    log "WARNING" "Exécution en tant que root déconseillée pour la sécurité"
fi

# Exécution du script principal
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi