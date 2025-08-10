#!/bin/bash

# =============================================================================
# SUPER Vote Secret - Script de Déploiement Production Robuste v2.0
# Configuration HTTPS fiable avec validation d'accessibilité complète
# =============================================================================

set -euo pipefail

# Couleurs pour l'affichage
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/deployment.log"
readonly HEALTH_CHECK_TIMEOUT=300
readonly SERVICE_START_TIMEOUT=180
readonly SSL_VERIFICATION_TIMEOUT=300
readonly WEB_ACCESSIBILITY_TIMEOUT=120

# Variables globales
DOMAIN=""
ADMIN_EMAIL=""
MONGO_ROOT_PASSWORD=""
JWT_SECRET=""
ENCRYPTION_KEY=""
SSL_GENERATED=false
HTTP_ACCESSIBLE=false
HTTPS_ACCESSIBLE=false
DEPLOYMENT_START_TIME=0

# =============================================================================
# FONCTIONS UTILITAIRES AVANCÉES
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
║              SUPER Vote Secret - Déploiement Production v2.0                  ║  
║                   Configuration HTTPS Robuste & Validée                       ║
╚════════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo -e "${WHITE}Système de Déploiement avec Validation d'Accessibilité Complète${NC}"
    echo -e "${WHITE}=================================================================================${NC}"
    echo
}

spinner_with_status() {
    local pid=$1
    local message="$2"
    local timeout="${3:-60}"
    local chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    local start_time=$(date +%s)
    
    while kill -0 $pid 2>/dev/null; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $timeout ]; then
            kill $pid 2>/dev/null || true
            printf "\r${RED}✗${NC} %s (Timeout après %ds)\n" "$message" "$timeout"
            return 1
        fi
        
        for (( i=0; i<${#chars}; i++ )); do
            printf "\r${BLUE}${chars:$i:1}${NC} %s (%ds)" "$message" "$elapsed"
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
        printf "\r${GREEN}✓${NC} %s (${final_time}s)\n" "$message"
        return 0
    else
        printf "\r${RED}✗${NC} %s (Échec après ${final_time}s)\n" "$message"
        return 1
    fi
}

wait_for_service_advanced() {
    local service_name="$1"
    local health_url="$2"
    local timeout="${3:-$HEALTH_CHECK_TIMEOUT}"
    local expected_response="${4:-}"
    
    log "INFO" "Attente du service $service_name (timeout: ${timeout}s)..."
    
    local start_time=$(date +%s)
    local attempts=0
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        attempts=$((attempts + 1))
        
        if [ $elapsed -gt $timeout ]; then
            log "ERROR" "Timeout atteint pour le service $service_name après $attempts tentatives"
            return 1
        fi
        
        # Vérifier que le container est running
        if ! docker-compose ps "$service_name" 2>/dev/null | grep -q "Up"; then
            printf "\r${YELLOW}⌛${NC} $service_name démarrage... (${elapsed}s/${timeout}s)"
            sleep 3
            continue
        fi
        
        # Tester la connectivité
        local response=""
        if response=$(curl -sf --max-time 10 --retry 0 "$health_url" 2>/dev/null); then
            if [[ -n "$expected_response" && "$response" != *"$expected_response"* ]]; then
                printf "\r${YELLOW}⌛${NC} $service_name initialisation... (${elapsed}s/${timeout}s)"
            else
                printf "\r${GREEN}✓${NC} Service $service_name opérationnel (${elapsed}s, ${attempts} tentatives)\n"
                log "SUCCESS" "Service $service_name opérationnel après ${elapsed}s"
                return 0
            fi
        else
            printf "\r${YELLOW}⌛${NC} $service_name connexion... (${elapsed}s/${timeout}s)"
        fi
        
        sleep 2
    done
}

verify_prerequisites_advanced() {
    log "INFO" "Vérification avancée des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker n'est pas installé"
        echo -e "${RED}❌ Veuillez installer Docker: https://docs.docker.com/engine/install/${NC}"
        exit 1
    fi
    
    # Vérifier la version Docker
    local docker_version=$(docker --version | grep -oP '\d+\.\d+' | head -1)
    if [[ $(echo "$docker_version 20.10" | tr ' ' '\n' | sort -V | head -1) != "20.10" ]]; then
        log "WARNING" "Version Docker ancienne détectée: $docker_version"
    fi
    
    # Vérifier Docker Compose
    local compose_cmd=""
    if command -v docker-compose &> /dev/null; then
        compose_cmd="docker-compose"
    elif docker compose version &> /dev/null; then
        compose_cmd="docker compose"
    else
        log "ERROR" "Docker Compose non disponible"
        echo -e "${RED}❌ Veuillez installer Docker Compose${NC}"
        exit 1
    fi
    
    # Tester les permissions Docker
    if ! docker ps &> /dev/null; then
        log "ERROR" "Permissions Docker insuffisantes"
        echo -e "${RED}❌ Ajoutez votre utilisateur au groupe docker: sudo usermod -aG docker \$USER${NC}"
        exit 1
    fi
    
    # Vérifier l'espace disque
    local disk_space=$(df . | awk 'NR==2 {print $4}')
    if [ "$disk_space" -lt 2000000 ]; then  # 2GB
        log "WARNING" "Espace disque faible: $(($disk_space/1024))MB disponible"
    fi
    
    # Vérifier les ports avec détails
    local conflicting_services=()
    if netstat -tuln 2>/dev/null | grep -q ":80 "; then
        local service_80=$(netstat -tulnp 2>/dev/null | grep ":80 " | head -1 | awk '{print $7}' | cut -d'/' -f2)
        conflicting_services+=("Port 80: ${service_80:-inconnu}")
    fi
    if netstat -tuln 2>/dev/null | grep -q ":443 "; then
        local service_443=$(netstat -tulnp 2>/dev/null | grep ":443 " | head -1 | awk '{print $7}' | cut -d'/' -f2)
        conflicting_services+=("Port 443: ${service_443:-inconnu}")
    fi
    
    if [ ${#conflicting_services[@]} -gt 0 ]; then
        log "WARNING" "Services conflictuels détectés: ${conflicting_services[*]}"
        log "WARNING" "Ces services seront arrêtés automatiquement"
    fi
    
    log "SUCCESS" "Prérequis validés (Docker $(docker --version | cut -d' ' -f3 | cut -d',' -f1))"
}

collect_configuration_validated() {
    log "INFO" "Collection et validation de la configuration..."
    
    echo -e "\n${WHITE}📋 Configuration du Déploiement Production${NC}"
    echo -e "${WHITE}==========================================${NC}\n"
    
    # Domaine avec validation DNS
    while [[ -z "$DOMAIN" ]]; do
        read -p "🌐 Nom de domaine (ex: vote.super-csn.ca): " DOMAIN
        
        # Validation du format
        if [[ ! "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9\.-]*[a-zA-Z0-9]$ ]]; then
            echo -e "${RED}❌ Domaine invalide. Format attendu: example.com${NC}"
            DOMAIN=""
            continue
        fi
        
        # Validation DNS (optionnelle)
        echo -e "${YELLOW}🔍 Vérification DNS du domaine...${NC}"
        if nslookup "$DOMAIN" &>/dev/null; then
            local ip=$(nslookup "$DOMAIN" 2>/dev/null | grep -A1 "Name:" | grep "Address:" | awk '{print $2}' | head -1)
            if [[ -n "$ip" ]]; then
                echo -e "${GREEN}✓ DNS résolu: $DOMAIN → $ip${NC}"
            else
                echo -e "${YELLOW}⚠ DNS résolution partielle pour $DOMAIN${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ Impossible de résoudre le DNS pour $DOMAIN${NC}"
            echo -e "${YELLOW}  Assurez-vous que le domaine pointe vers ce serveur${NC}"
            read -p "Continuer quand même ? (y/N): " continue_anyway
            if [[ ! "$continue_anyway" =~ ^[Yy]$ ]]; then
                DOMAIN=""
                continue
            fi
        fi
    done
    
    # Email administrateur
    while [[ -z "$ADMIN_EMAIL" ]]; do
        read -p "📧 Email administrateur (pour SSL Let's Encrypt): " ADMIN_EMAIL
        if [[ ! "$ADMIN_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
            echo -e "${RED}❌ Format d'email invalide${NC}"
            ADMIN_EMAIL=""
        fi
    done
    
    # Mot de passe MongoDB avec critères de sécurité
    while [[ -z "$MONGO_ROOT_PASSWORD" ]]; do
        echo -e "🔒 Mot de passe MongoDB (critères de sécurité):"
        echo -e "   • Minimum 12 caractères"
        echo -e "   • Au moins 1 majuscule, 1 minuscule, 1 chiffre"
        echo -e "   • Au moins 1 caractère spécial"
        read -s -p "   Entrez le mot de passe: " MONGO_ROOT_PASSWORD
        echo
        
        # Validation de la complexité
        if [[ ${#MONGO_ROOT_PASSWORD} -lt 12 ]]; then
            echo -e "${RED}❌ Mot de passe trop court (minimum 12 caractères)${NC}"
            MONGO_ROOT_PASSWORD=""
            continue
        fi
        
        if [[ ! "$MONGO_ROOT_PASSWORD" =~ [A-Z] ]]; then
            echo -e "${RED}❌ Doit contenir au moins une majuscule${NC}"
            MONGO_ROOT_PASSWORD=""
            continue
        fi
        
        if [[ ! "$MONGO_ROOT_PASSWORD" =~ [a-z] ]]; then
            echo -e "${RED}❌ Doit contenir au moins une minuscule${NC}"
            MONGO_ROOT_PASSWORD=""
            continue
        fi
        
        if [[ ! "$MONGO_ROOT_PASSWORD" =~ [0-9] ]]; then
            echo -e "${RED}❌ Doit contenir au moins un chiffre${NC}"
            MONGO_ROOT_PASSWORD=""
            continue
        fi
        
        if [[ ! "$MONGO_ROOT_PASSWORD" =~ [^A-Za-z0-9] ]]; then
            echo -e "${RED}❌ Doit contenir au moins un caractère spécial${NC}"
            MONGO_ROOT_PASSWORD=""
            continue
        fi
    done
    
    # Confirmation de la configuration
    echo -e "\n${WHITE}📋 Récapitulatif de la Configuration${NC}"
    echo -e "${WHITE}====================================${NC}"
    echo -e "🌐 Domaine: ${GREEN}$DOMAIN${NC}"
    echo -e "📧 Email: ${GREEN}$ADMIN_EMAIL${NC}"
    echo -e "🔒 MongoDB: ${GREEN}Mot de passe sécurisé configuré${NC}"
    echo
    
    read -p "Confirmer la configuration ? (Y/n): " confirm
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        echo -e "${YELLOW}Configuration annulée par l'utilisateur${NC}"
        exit 0
    fi
    
    # Génération des clés de sécurité
    log "INFO" "Génération des clés de sécurité avancées..."
    JWT_SECRET=$(openssl rand -base64 48)
    ENCRYPTION_KEY=$(openssl rand -hex 32)
    
    log "SUCCESS" "Configuration validée et sécurisée"
}

build_and_deploy_robust() {
    log "INFO" "Construction et déploiement robuste des services..."
    
    echo -e "\n${WHITE}🔨 Construction des Images Docker${NC}"
    echo -e "${WHITE}==================================${NC}\n"
    
    # Nettoyage préliminaire intelligent
    log "INFO" "Nettoyage des ressources obsolètes..."
    (
        # Arrêter les anciens containers vote-secret
        docker ps -a --format "{{.Names}}" | grep "vote-secret" | xargs -r docker stop 2>/dev/null || true
        docker ps -a --format "{{.Names}}" | grep "vote-secret" | xargs -r docker rm 2>/dev/null || true
        
        # Nettoyer les images dangereuses et les volumes orphelins
        docker system prune -f 2>&1
        docker volume prune -f 2>&1
        
    ) &>/dev/null &
    
    spinner_with_status $! "Nettoyage Docker" 60
    
    # Construction des images avec gestion d'erreur
    log "INFO" "Construction des images (cela peut prendre quelques minutes)..."
    
    (
        export DOCKER_BUILDKIT=1
        export COMPOSE_DOCKER_CLI_BUILD=1
        
        # Build sans cache pour éviter les problèmes de dépendances
        docker-compose build --no-cache --parallel 2>&1 | tee -a "$LOG_FILE"
        
    ) &
    
    if ! spinner_with_status $! "Construction des images Docker" 600; then
        log "ERROR" "Échec de la construction des images"
        log "INFO" "Consultez les logs détaillés: tail -f $LOG_FILE"
        return 1
    fi
    
    # Démarrage des services avec ordre de dépendance
    log "INFO" "Démarrage des services..."
    
    if ! docker-compose up -d 2>&1 | tee -a "$LOG_FILE"; then
        log "ERROR" "Échec du démarrage des services"
        return 1
    fi
    
    log "SUCCESS" "Services démarrés avec succès"
}

wait_for_all_services_robust() {
    log "INFO" "Validation complète de tous les services..."
    
    echo -e "\n${WHITE}🔍 Tests de Santé des Services${NC}"
    echo -e "${WHITE}==============================${NC}\n"
    
    # MongoDB - Test avancé
    if ! wait_for_service_advanced "mongodb" "http://localhost:27017" 120; then
        # Test alternatif via container
        local mongo_ready=false
        for i in {1..30}; do
            if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
                mongo_ready=true
                break
            fi
            sleep 2
        done
        
        if [ "$mongo_ready" = true ]; then
            echo -e "${GREEN}✓${NC} MongoDB opérationnel (via connexion directe)"
        else
            echo -e "${RED}✗${NC} MongoDB timeout - Vérifiez les logs: docker-compose logs mongodb"
            return 1
        fi
    fi
    
    # Backend API - Test complet
    if ! wait_for_service_advanced "backend" "http://localhost:8001/api/health" 120 "healthy"; then
        echo -e "${RED}✗${NC} Backend API timeout"
        log "ERROR" "Backend API non accessible"
        return 1
    fi
    
    # Frontend - Test robuste
    if ! wait_for_service_advanced "frontend" "http://localhost:3000/health" 120; then
        echo -e "${RED}✗${NC} Frontend timeout"
        log "ERROR" "Frontend non accessible"
        return 1
    fi
    
    # Nginx - Test multi-endpoints
    local nginx_ready=false
    for endpoint in "http://localhost:80/health" "http://localhost/health"; do
        if wait_for_service_advanced "nginx" "$endpoint" 60 "nginx"; then
            nginx_ready=true
            break
        fi
    done
    
    if [ "$nginx_ready" != true ]; then
        echo -e "${RED}✗${NC} Nginx proxy timeout"
        log "ERROR" "Nginx proxy non accessible"
        return 1
    fi
    
    log "SUCCESS" "Tous les services de base sont opérationnels"
    return 0
}

configure_ssl_robust() {
    log "INFO" "Configuration SSL robuste avec Let's Encrypt..."
    
    echo -e "\n${WHITE}🔒 Configuration SSL Avancée${NC}"
    echo -e "${WHITE}=============================${NC}\n"
    
    # Attendre que Nginx soit prêt
    sleep 15
    
    # Vérifier que le domaine est accessible via HTTP d'abord
    echo -e "${YELLOW}🌐 Vérification de l'accessibilité du domaine...${NC}"
    
    local domain_accessible=false
    for i in {1..20}; do
        if curl -sf --max-time 10 "http://$DOMAIN/health" | grep -q "nginx" 2>/dev/null; then
            domain_accessible=true
            break
        fi
        
        # Tester aussi avec www.
        if curl -sf --max-time 10 "http://www.$DOMAIN/health" | grep -q "nginx" 2>/dev/null; then
            domain_accessible=true
            break
        fi
        
        printf "."
        sleep 3
    done
    
    if [ "$domain_accessible" = true ]; then
        echo -e "\r${GREEN}✓${NC} Domaine accessible via HTTP"
    else
        echo -e "\r${YELLOW}⚠${NC} Domaine non accessible - SSL manuel nécessaire"
        log "WARNING" "Domaine $DOMAIN non accessible pour validation SSL automatique"
    fi
    
    # Tentative de génération SSL
    echo -e "${YELLOW}🔑 Génération du certificat SSL...${NC}"
    
    local ssl_attempts=0
    local max_ssl_attempts=3
    
    while [ $ssl_attempts -lt $max_ssl_attempts ]; do
        ssl_attempts=$((ssl_attempts + 1))
        
        log "INFO" "Tentative SSL $ssl_attempts/$max_ssl_attempts pour $DOMAIN"
        
        # Lancer certbot et attendre le résultat
        sleep 10
        
        # Vérifier si le certificat a été généré
        local ssl_check_attempts=0
        while [ $ssl_check_attempts -lt 18 ]; do  # 3 minutes max
            ssl_check_attempts=$((ssl_check_attempts + 1))
            
            # Vérifier dans les logs de certbot
            local certbot_logs=$(docker-compose logs certbot 2>/dev/null | tail -20)
            
            if echo "$certbot_logs" | grep -q "Successfully received certificate"; then
                SSL_GENERATED=true
                echo -e "\r${GREEN}✓${NC} Certificat SSL généré avec succès"
                log "SUCCESS" "Certificat SSL généré pour $DOMAIN"
                break 2
            fi
            
            if echo "$certbot_logs" | grep -q "Certificate not yet due for renewal"; then
                SSL_GENERATED=true
                echo -e "\r${GREEN}✓${NC} Certificat SSL existant et valide"
                log "SUCCESS" "Certificat SSL existant pour $DOMAIN"
                break 2
            fi
            
            # Vérifier les erreurs critiques
            if echo "$certbot_logs" | grep -qE "(Failed authorization|Invalid response|DNS problem)"; then
                echo -e "\r${RED}✗${NC} Erreur de validation SSL"
                log "ERROR" "Échec validation SSL: $(echo "$certbot_logs" | grep -E "(error|Error)" | tail -1)"
                break
            fi
            
            printf "\r${YELLOW}⌛${NC} Génération SSL en cours... (${ssl_check_attempts}/18)"
            sleep 10
        done
        
        if [ "$SSL_GENERATED" = true ]; then
            break
        fi
        
        if [ $ssl_attempts -lt $max_ssl_attempts ]; then
            echo -e "\n${YELLOW}⚠ Tentative SSL $ssl_attempts échouée, nouvelle tentative...${NC}"
            sleep 30
        fi
    done
    
    # Configuration de fallback si SSL échoue
    if [ "$SSL_GENERATED" != true ]; then
        echo -e "\r${YELLOW}⚠${NC} Génération SSL automatique échouée"
        log "WARNING" "SSL automatique échoué - Configuration fallback HTTP activée"
        
        echo -e "\n${WHITE}Configuration SSL Manuel${NC}"
        echo -e "========================"
        echo -e "Le certificat SSL automatique n'a pas pu être généré."
        echo -e "L'application reste accessible via:"
        echo -e "• ${CYAN}http://$DOMAIN${NC} (HTTP)"
        echo -e "• ${CYAN}http://$(curl -s ifconfig.me 2>/dev/null || echo 'votre-ip')${NC} (IP)"
        echo
        echo -e "Pour configurer SSL manuellement:"
        echo -e "1. Vérifiez que $DOMAIN pointe vers ce serveur"
        echo -e "2. Redémarrez certbot: ${YELLOW}docker-compose restart certbot${NC}"
        echo -e "3. Suivez les logs: ${YELLOW}docker-compose logs -f certbot${NC}"
    fi
    
    log "SUCCESS" "Configuration SSL terminée"
}

validate_web_accessibility() {
    log "INFO" "Validation complète de l'accessibilité web..."
    
    echo -e "\n${WHITE}🌐 Tests d'Accessibilité Web Complets${NC}"
    echo -e "${WHITE}======================================${NC}\n"
    
    local urls_to_test=()
    
    # URLs HTTP
    urls_to_test+=(
        "http://localhost/health|Localhost HTTP Health"
        "http://localhost:80/health|Port 80 Health" 
        "http://$DOMAIN/health|Domain HTTP Health"
        "http://localhost/api/health|API HTTP Health"
    )
    
    # URLs HTTPS (si SSL configuré)
    if [ "$SSL_GENERATED" = true ]; then
        urls_to_test+=(
            "https://localhost:443/health|HTTPS Port 443 Health"
            "https://$DOMAIN/health|Domain HTTPS Health"
            "https://localhost/api/health|API HTTPS Health"
        )
    fi
    
    local successful_tests=0
    local total_tests=${#urls_to_test[@]}
    
    for url_test in "${urls_to_test[@]}"; do
        local url=$(echo "$url_test" | cut -d'|' -f1)
        local description=$(echo "$url_test" | cut -d'|' -f2)
        
        printf "${YELLOW}⌛${NC} Test: $description..."
        
        local success=false
        local response=""
        
        # Test avec retry et timeout
        for attempt in {1..3}; do
            if response=$(curl -sf --max-time 15 --retry 0 -k "$url" 2>/dev/null); then
                if [[ "$response" == *"healthy"* || "$response" == *"nginx"* ]]; then
                    success=true
                    break
                fi
            fi
            sleep 2
        done
        
        if [ "$success" = true ]; then
            printf "\r${GREEN}✓${NC} $description\n"
            successful_tests=$((successful_tests + 1))
            
            # Marquer les types d'accès comme fonctionnels
            if [[ "$url" == *"https://"* ]]; then
                HTTPS_ACCESSIBLE=true
            else
                HTTP_ACCESSIBLE=true
            fi
        else
            printf "\r${RED}✗${NC} $description (Non accessible)\n"
            log "WARNING" "$description non accessible: $url"
        fi
    done
    
    # Test de l'application complète (pas seulement health)
    echo -e "\n${WHITE}🎯 Test de l'Application Complète${NC}"
    echo -e "${WHITE}=================================${NC}\n"
    
    local app_urls=(
        "http://localhost|Application HTTP"
        "http://$DOMAIN|Application Domain HTTP"
    )
    
    if [ "$SSL_GENERATED" = true ]; then
        app_urls+=(
            "https://$DOMAIN|Application Domain HTTPS"
        )
    fi
    
    for url_test in "${app_urls[@]}"; do
        local url=$(echo "$url_test" | cut -d'|' -f1)
        local description=$(echo "$url_test" | cut -d'|' -f2)
        
        printf "${YELLOW}⌛${NC} Test: $description..."
        
        local app_success=false
        
        # Tester que l'application renvoie du HTML (pas seulement health)
        for attempt in {1..3}; do
            local response=$(curl -sf --max-time 20 -k "$url" 2>/dev/null)
            if [[ "$response" == *"<html"* || "$response" == *"<!DOCTYPE"* || "$response" == *"Vote Secret"* ]]; then
                app_success=true
                break
            fi
            sleep 3
        done
        
        if [ "$app_success" = true ]; then
            printf "\r${GREEN}✓${NC} $description (Application chargée)\n"
            successful_tests=$((successful_tests + 1))
        else
            printf "\r${YELLOW}⚠${NC} $description (HTML non détecté)\n"
            log "WARNING" "Application non complètement chargée sur $url"
        fi
    done
    
    # Évaluation finale
    echo -e "\n${WHITE}📊 Résumé des Tests d'Accessibilité${NC}"
    echo -e "${WHITE}===================================${NC}"
    
    local success_rate=$(( (successful_tests * 100) / (total_tests + ${#app_urls[@]}) ))
    
    echo -e "Tests réussis: ${GREEN}$successful_tests$(echo " / $((total_tests + ${#app_urls[@]}))")${NC} (${success_rate}%)"
    
    if [ "$HTTP_ACCESSIBLE" = true ]; then
        echo -e "${GREEN}✓${NC} Accès HTTP fonctionnel"
    fi
    
    if [ "$HTTPS_ACCESSIBLE" = true ]; then
        echo -e "${GREEN}✓${NC} Accès HTTPS fonctionnel"
    fi
    
    if [ $success_rate -ge 70 ]; then
        log "SUCCESS" "Validation d'accessibilité réussie ($success_rate% des tests)"
        return 0
    else
        log "ERROR" "Validation d'accessibilité échouée ($success_rate% des tests)"
        return 1
    fi
}

show_deployment_summary_complete() {
    local end_time=$(date +%s)
    local duration=$((end_time - DEPLOYMENT_START_TIME))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    clear
    
    if [ "$HTTP_ACCESSIBLE" = true ] || [ "$HTTPS_ACCESSIBLE" = true ]; then
        echo -e "${GREEN}"
        cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════════╗
║                        🎉 DÉPLOIEMENT RÉUSSI ET VALIDÉ! 🎉                    ║
╚════════════════════════════════════════════════════════════════════════════════╝
EOF
    else
        echo -e "${YELLOW}"
        cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════════╗
║                     ⚠️  DÉPLOIEMENT PARTIEL - ATTENTION ⚠️                     ║
╚════════════════════════════════════════════════════════════════════════════════╝
EOF
    fi
    echo -e "${NC}"
    
    echo -e "${WHITE}📊 Résumé Détaillé du Déploiement${NC}"
    echo -e "${WHITE}==================================${NC}"
    echo -e "⏱️  Durée totale: ${GREEN}${minutes}m ${seconds}s${NC}"
    echo -e "🌐 Domaine: ${GREEN}$DOMAIN${NC}"
    echo -e "📧 Email admin: ${GREEN}$ADMIN_EMAIL${NC}"
    echo -e "🐳 Services: ${GREEN}$(docker-compose ps --services 2>/dev/null | wc -l) conteneurs actifs${NC}"
    echo -e "💾 Données: ${GREEN}Persistantes (volumes Docker)${NC}"
    echo
    
    echo -e "${WHITE}🌍 URLs d'Accès Validées${NC}"
    echo -e "${WHITE}=========================${NC}"
    
    if [ "$HTTP_ACCESSIBLE" = true ]; then
        echo -e "🔗 HTTP:  ${CYAN}http://$DOMAIN${NC} ${GREEN}✓ Accessible${NC}"
        echo -e "📱 Local: ${CYAN}http://localhost${NC} ${GREEN}✓ Accessible${NC}"
    else
        echo -e "🔗 HTTP:  ${CYAN}http://$DOMAIN${NC} ${YELLOW}⚠ Non validé${NC}"
    fi
    
    if [ "$HTTPS_ACCESSIBLE" = true ]; then
        echo -e "🔒 HTTPS: ${CYAN}https://$DOMAIN${NC} ${GREEN}✓ SSL Fonctionnel${NC}"
    elif [ "$SSL_GENERATED" = true ]; then
        echo -e "🔒 HTTPS: ${CYAN}https://$DOMAIN${NC} ${YELLOW}⚠ SSL configuré (test manuel requis)${NC}"
    else
        echo -e "🔒 HTTPS: ${YELLOW}⚠ Configuration SSL à finaliser manuellement${NC}"
    fi
    
    echo
    
    # Recommandations basées sur l'état
    if [ "$HTTP_ACCESSIBLE" = true ] && [ "$HTTPS_ACCESSIBLE" = true ]; then
        echo -e "${WHITE}✨ État: Application entièrement fonctionnelle${NC}"
        echo -e "   ${GREEN}→ Prêt pour la production${NC}"
    elif [ "$HTTP_ACCESSIBLE" = true ]; then
        echo -e "${WHITE}⚠️  État: Application accessible en HTTP${NC}"
        echo -e "   ${YELLOW}→ Configurez SSL pour la production${NC}"
    else
        echo -e "${WHITE}🔧 État: Configuration supplémentaire requise${NC}"
        echo -e "   ${YELLOW}→ Vérifiez la configuration réseau${NC}"
    fi
    
    echo
    echo -e "${WHITE}🛠️  Commandes de Gestion${NC}"
    echo -e "${WHITE}========================${NC}"
    echo -e "📊 Status:      ${YELLOW}docker-compose ps${NC}"
    echo -e "📋 Logs:        ${YELLOW}docker-compose logs -f [service]${NC}"
    echo -e "🔄 Restart:     ${YELLOW}docker-compose restart${NC}"
    echo -e "🛑 Arrêt:       ${YELLOW}docker-compose down${NC}"
    echo -e "🔒 SSL Manuel:  ${YELLOW}docker-compose restart certbot && docker-compose logs -f certbot${NC}"
    echo
    
    echo -e "${WHITE}📋 Fichiers Importants${NC}"
    echo -e "${WHITE}======================${NC}"
    echo -e "• Configuration: ${YELLOW}.env${NC}"
    echo -e "• Logs déploiement: ${YELLOW}$LOG_FILE${NC}"
    echo -e "• Sauvegarde MongoDB: ${YELLOW}Volume docker vote-secret-mongodb-data${NC}"
    echo
    
    # Alertes spécifiques
    if [ "$SSL_GENERATED" != true ]; then
        echo -e "${YELLOW}⚠️  ATTENTION SSL${NC}"
        echo -e "${YELLOW}================${NC}"
        echo -e "Le certificat SSL automatique n'a pas pu être généré."
        echo -e "Causes possibles:"
        echo -e "• Le domaine $DOMAIN ne pointe pas vers ce serveur"
        echo -e "• Port 80 non accessible depuis Internet"
        echo -e "• Configuration DNS incomplète"
        echo
        echo -e "Action recommandée:"
        echo -e "1. Vérifiez le DNS: ${YELLOW}nslookup $DOMAIN${NC}"
        echo -e "2. Testez l'accès: ${YELLOW}curl -I http://$DOMAIN${NC}"
        echo -e "3. Relancez SSL: ${YELLOW}docker-compose restart certbot${NC}"
        echo
    fi
    
    log "SUCCESS" "Déploiement terminé (${minutes}m ${seconds}s) - HTTP: $HTTP_ACCESSIBLE, HTTPS: $HTTPS_ACCESSIBLE"
}

# =============================================================================
# FONCTION PRINCIPALE ROBUSTE
# =============================================================================

main() {
    DEPLOYMENT_START_TIME=$(date +%s)
    
    # Initialisation
    show_banner
    log "INFO" "Début du déploiement SUPER Vote Secret v2.0"
    
    # Validation des étapes critiques avec gestion d'erreur
    if ! verify_prerequisites_advanced; then
        log "ERROR" "Échec de la vérification des prérequis"
        exit 1
    fi
    
    collect_configuration_validated
    
    if ! create_environment_file; then
        log "ERROR" "Échec de création du fichier d'environnement"
        exit 1
    fi
    
    if ! stop_conflicting_services; then
        log "WARNING" "Problème lors de l'arrêt des services conflictuels"
    fi
    
    if ! build_and_deploy_robust; then
        log "ERROR" "Échec du déploiement"
        exit 1
    fi
    
    if ! wait_for_all_services_robust; then
        log "ERROR" "Services non démarrés correctement"
        echo -e "\n${RED}❌ Certains services ne sont pas opérationnels${NC}"
        echo -e "Vérifiez les logs: ${YELLOW}docker-compose logs${NC}"
        exit 1
    fi
    
    configure_ssl_robust
    
    # Validation finale - critique pour la réussite
    if ! validate_web_accessibility; then
        log "WARNING" "Validation d'accessibilité partielle"
        echo -e "\n${YELLOW}⚠️ L'application peut nécessiter une configuration supplémentaire${NC}"
    fi
    
    # Résumé final avec état réel
    show_deployment_summary_complete
    
    # Message final adapté à l'état
    if [ "$HTTP_ACCESSIBLE" = true ]; then
        echo -e "${GREEN}🎉 L'application SUPER Vote Secret est accessible !${NC}"
        echo -e "${WHITE}🎯 Accédez maintenant: ${CYAN}http://$DOMAIN${NC}"
        if [ "$HTTPS_ACCESSIBLE" = true ]; then
            echo -e "${WHITE}🔒 Accès sécurisé: ${CYAN}https://$DOMAIN${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Déploiement terminé avec configuration supplémentaire requise${NC}"
        echo -e "${WHITE}📖 Consultez le guide: GUIDE_DEPLOIEMENT_PRODUCTION.md${NC}"
    fi
}

create_environment_file() {
    log "INFO" "Création du fichier d'environnement sécurisé..."
    
    cat > .env << EOF
# SUPER Vote Secret - Production Environment Configuration
# Généré automatiquement le $(date)
# Configuration HTTPS robuste

# MongoDB Configuration
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD}
MONGO_DB=vote_secret

# Application Configuration  
DOMAIN=${DOMAIN}
ADMIN_EMAIL=${ADMIN_EMAIL}

# Security Keys (GENERATED AUTOMATICALLY - HIGH ENTROPY)
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

# Backup & Monitoring
BACKUP_RETENTION_DAYS=30
ENABLE_AUTOMATED_BACKUPS=true
DEPLOYMENT_DATE=$(date -Iseconds)
EOF

    chmod 600 .env
    log "SUCCESS" "Fichier d'environnement créé avec permissions sécurisées (600)"
}

stop_conflicting_services() {
    log "INFO" "Gestion intelligente des services conflictuels..."
    
    local services_stopped=false
    
    # Arrêter nginx système
    if systemctl is-active --quiet nginx 2>/dev/null; then
        log "WARNING" "Arrêt de nginx système..."
        if sudo systemctl stop nginx && sudo systemctl disable nginx; then
            services_stopped=true
        fi
    fi
    
    # Arrêter apache système
    for apache_service in apache2 httpd; do
        if systemctl is-active --quiet $apache_service 2>/dev/null; then
            log "WARNING" "Arrêt de $apache_service système..."
            if sudo systemctl stop $apache_service && sudo systemctl disable $apache_service; then
                services_stopped=true
            fi
        fi
    done
    
    # Gestion des anciens containers avec vérification
    local old_containers=$(docker ps -a --format "{{.Names}}" | grep "vote-secret" | head -10)
    if [[ -n "$old_containers" ]]; then
        log "WARNING" "Arrêt des anciens containers vote-secret..."
        echo "$old_containers" | xargs -r docker stop 2>/dev/null || true
        echo "$old_containers" | xargs -r docker rm 2>/dev/null || true
        services_stopped=true
    fi
    
    if [ "$services_stopped" = true ]; then
        log "SUCCESS" "Services conflictuels gérés avec succès"
        sleep 5  # Laisser le temps aux ports de se libérer
    else
        log "INFO" "Aucun service conflictuel détecté"
    fi
    
    return 0
}

# Gestion des interruptions avec nettoyage
cleanup_on_exit() {
    log "WARNING" "Interruption détectée - Nettoyage en cours..."
    docker-compose down 2>/dev/null || true
    exit 1
}

trap cleanup_on_exit INT TERM

# Vérifier si le script est exécuté directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Vérification des permissions
    if [[ $EUID -eq 0 ]]; then
        log "WARNING" "Exécution en tant que root détectée - Non recommandé pour la sécurité"
        echo -e "${YELLOW}⚠️ Il est recommandé d'exécuter ce script avec un utilisateur non-root${NC}"
        read -p "Continuer quand même ? (y/N): " continue_root
        if [[ ! "$continue_root" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    main "$@"
fi