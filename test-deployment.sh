#!/bin/bash

# =============================================================================
# Script de Test du Déploiement SUPER Vote Secret
# =============================================================================

set -euo pipefail

# Couleurs
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log() {
    echo -e "${GREEN}[TEST]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

test_docker_setup() {
    log "Test de l'environnement Docker..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        error "Docker n'est pas installé"
        return 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose n'est pas installé"
        return 1
    fi
    
    # Tester les permissions Docker
    if ! docker ps &> /dev/null; then
        error "Permissions Docker insuffisantes"
        return 1
    fi
    
    log "✅ Environnement Docker OK"
    return 0
}

test_deployment_files() {
    log "Vérification des fichiers de déploiement..."
    
    local required_files=(
        "docker-compose.yml"
        "nginx/nginx.conf"
        "nginx/ssl/nginx-selfsigned.crt"
        "nginx/ssl/nginx-selfsigned.key"
        "deploy-production.sh"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            error "Fichier manquant: $file"
            return 1
        fi
    done
    
    # Vérifier les permissions d'exécution
    if [ ! -x "deploy-production.sh" ]; then
        error "deploy-production.sh n'est pas exécutable"
        return 1
    fi
    
    log "✅ Fichiers de déploiement OK"
    return 0
}

test_port_availability() {
    log "Vérification de la disponibilité des ports..."
    
    local ports=(80 443)
    local ports_in_use=()
    
    for port in "${ports[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            ports_in_use+=($port)
        fi
    done
    
    if [ ${#ports_in_use[@]} -gt 0 ]; then
        warn "Ports en cours d'utilisation: ${ports_in_use[*]}"
        warn "Le script de déploiement les libérera automatiquement"
    else
        log "✅ Ports 80/443 disponibles"
    fi
    
    return 0
}

simulate_deployment_config() {
    log "Test de la configuration de déploiement..."
    
    # Créer un fichier .env de test
    cat > .env.test << EOF
DOMAIN=test.example.com
ADMIN_EMAIL=admin@test.com
MONGO_ROOT_PASSWORD=TestPassword123!
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 16)
EOF
    
    # Vérifier que les variables sont bien formées
    source .env.test
    
    if [[ ! "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9\.-]*[a-zA-Z0-9]$ ]]; then
        error "Format de domaine invalide"
        return 1
    fi
    
    if [[ ! "$ADMIN_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        error "Format d'email invalide"
        return 1
    fi
    
    if [[ ${#MONGO_ROOT_PASSWORD} -lt 12 ]]; then
        error "Mot de passe MongoDB trop court"
        return 1
    fi
    
    # Nettoyer
    rm .env.test
    
    log "✅ Configuration de test valide"
    return 0
}

test_nginx_config() {
    log "Test de la configuration Nginx..."
    
    # Utiliser docker pour tester la configuration nginx
    if docker run --rm -v "$(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro" nginx nginx -t; then
        log "✅ Configuration Nginx valide"
        return 0
    else
        error "Configuration Nginx invalide"
        return 1
    fi
}

show_deployment_readiness() {
    echo
    echo "================================================="
    echo "🚀 ÉTAT DE PRÉPARATION DU DÉPLOIEMENT"
    echo "================================================="
    echo
    echo "✅ Environnement Docker configuré"
    echo "✅ Fichiers de déploiement présents"
    echo "✅ Configuration Nginx valide"
    echo "✅ Scripts de déploiement prêts"
    echo "✅ Certificats SSL initialisés"
    echo
    echo "🎯 Pour déployer l'application:"
    echo "   ./deploy-production.sh"
    echo
    echo "📋 Le script vous demandera:"
    echo "   • Nom de domaine"
    echo "   • Email administrateur"
    echo "   • Mot de passe MongoDB"
    echo
    echo "⏱️  Durée estimée du déploiement: 3-5 minutes"
    echo "================================================="
}

main() {
    echo "🧪 Tests de Préparation au Déploiement SUPER Vote Secret"
    echo "======================================================="
    echo
    
    local tests_passed=0
    local total_tests=5
    
    if test_docker_setup; then ((tests_passed++)); fi
    if test_deployment_files; then ((tests_passed++)); fi
    if test_port_availability; then ((tests_passed++)); fi
    if simulate_deployment_config; then ((tests_passed++)); fi
    if test_nginx_config; then ((tests_passed++)); fi
    
    echo
    echo "Résultats: $tests_passed/$total_tests tests passés"
    
    if [ $tests_passed -eq $total_tests ]; then
        echo -e "${GREEN}✅ Système prêt pour le déploiement !${NC}"
        show_deployment_readiness
        return 0
    else
        echo -e "${RED}❌ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.${NC}"
        return 1
    fi
}

main "$@"