#!/bin/bash

# SUPER Vote Secret - Script de Déploiement VPS Interactif
# Version 2.2.0 - Pour déploiement production sur VPS

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Fonctions d'affichage
print_header() {
    echo ""
    echo -e "${PURPLE}🗳️  SUPER Vote Secret - Déploiement VPS${NC}"
    echo -e "${PURPLE}======================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_step() {
    echo ""
    echo -e "${BLUE}📍 ÉTAPE $1/$2: $3${NC}"
    echo "----------------------------------------"
}

# Variables
DOMAIN=""
ADMIN_EMAIL=""
MONGO_PASSWORD=""
JWT_SECRET=""
ENCRYPTION_KEY=""
TOTAL_STEPS=8

# Fonction pour générer un mot de passe sécurisé
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Fonction pour valider un domaine
validate_domain() {
    local domain=$1
    if [[ $domain =~ ^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$ ]]; then
        return 0
    else
        return 1
    fi
}

# Fonction pour valider un email
validate_email() {
    local email=$1
    if [[ $email =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Fonction pour vérifier les prérequis système
check_system_requirements() {
    print_step 1 $TOTAL_STEPS "Vérification des prérequis système"
    
    # Vérifier l'OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        print_info "OS détecté: $NAME $VERSION"
    else
        print_error "Impossible de détecter l'OS"
        exit 1
    fi
    
    # Vérifier les privilèges root
    if [ "$EUID" -ne 0 ]; then
        print_error "Ce script doit être exécuté avec sudo"
        print_info "Utilisez: sudo ./deploy-vps.sh"
        exit 1
    fi
    
    # Vérifier la connectivité internet
    if ! ping -c 1 google.com > /dev/null 2>&1; then
        print_error "Pas de connexion Internet"
        exit 1
    fi
    
    print_success "Prérequis système vérifiés"
}

# Fonction pour installer Docker
install_docker() {
    print_step 2 $TOTAL_STEPS "Installation de Docker et Docker Compose"
    
    if command -v docker &> /dev/null && command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_info "Docker déjà installé: $DOCKER_VERSION"
        
        if docker compose version &> /dev/null; then
            COMPOSE_VERSION=$(docker compose version | cut -d' ' -f4)
            print_info "Docker Compose déjà installé: $COMPOSE_VERSION"
        else
            print_warning "Docker Compose V2 non trouvé, utilisation de docker-compose legacy"
        fi
    else
        print_info "Installation de Docker..."
        
        # Mise à jour du système
        apt-get update
        apt-get install -y ca-certificates curl gnupg lsb-release
        
        # Ajouter la clé GPG Docker
        mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # Ajouter le repository Docker
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Installer Docker
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # Démarrer Docker
        systemctl start docker
        systemctl enable docker
        
        print_success "Docker installé avec succès"
    fi
    
    # Vérifier que Docker fonctionne
    if ! docker run --rm hello-world > /dev/null 2>&1; then
        print_error "Docker ne fonctionne pas correctement"
        exit 1
    fi
    
    print_success "Docker opérationnel"
}

# Fonction pour configurer les variables d'environnement
configure_environment() {
    print_step 3 $TOTAL_STEPS "Configuration des variables d'environnement"
    
    # Demander le domaine
    while true; do
        echo ""
        echo -e "${BLUE}🌐 Configuration du domaine${NC}"
        echo "Entrez votre domaine (ex: vote.example.com):"
        read -p "Domaine: " DOMAIN
        
        if validate_domain "$DOMAIN"; then
            print_success "Domaine valide: $DOMAIN"
            break
        else
            print_error "Domaine invalide. Format attendu: vote.example.com"
        fi
    done
    
    # Demander l'email
    while true; do
        echo ""
        echo -e "${BLUE}📧 Configuration de l'email SSL${NC}"
        echo "Entrez votre email pour les certificats SSL:"
        read -p "Email: " ADMIN_EMAIL
        
        if validate_email "$ADMIN_EMAIL"; then
            print_success "Email valide: $ADMIN_EMAIL"
            break
        else
            print_error "Email invalide. Format attendu: admin@example.com"
        fi
    done
    
    # Générer les mots de passe sécurisés
    echo ""
    echo -e "${BLUE}🔐 Génération des clés de sécurité${NC}"
    MONGO_PASSWORD=$(generate_password)
    JWT_SECRET=$(generate_password)
    ENCRYPTION_KEY=$(generate_password)
    
    print_info "Mot de passe MongoDB: ${MONGO_PASSWORD:0:8}..."
    print_info "Clé JWT: ${JWT_SECRET:0:8}..."
    print_info "Clé de chiffrement: ${ENCRYPTION_KEY:0:8}..."
    
    # Créer le fichier .env
    cat > .env << EOL
# SUPER Vote Secret - Configuration VPS Production
# Généré automatiquement le $(date)

# MongoDB Configuration
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=$MONGO_PASSWORD
MONGO_DB=vote_secret

# Application Configuration  
DOMAIN=$DOMAIN
ADMIN_EMAIL=$ADMIN_EMAIL

# Security Keys
JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY

# Application Settings
APP_NAME=SUPER Vote Secret
APP_VERSION=2.2.0
NODE_ENV=production
PYTHON_ENV=production

# SSL Configuration
SSL_ENABLED=true
SSL_EMAIL=$ADMIN_EMAIL

# Backup Configuration
BACKUP_RETENTION_DAYS=30
ENABLE_AUTOMATED_BACKUPS=true
EOL
    
    print_success "Fichier .env créé avec succès"
}

# Fonction pour vérifier le DNS
check_dns() {
    print_step 4 $TOTAL_STEPS "Vérification de la configuration DNS"
    
    print_info "Vérification que $DOMAIN pointe vers ce serveur..."
    
    SERVER_IP=$(curl -s https://ipinfo.io/ip)
    DOMAIN_IP=$(dig +short $DOMAIN)
    
    print_info "IP du serveur: $SERVER_IP"
    print_info "IP du domaine: $DOMAIN_IP"
    
    if [ "$SERVER_IP" = "$DOMAIN_IP" ]; then
        print_success "DNS configuré correctement"
    else
        print_warning "Le domaine ne pointe pas vers ce serveur"
        echo ""
        echo "Veuillez configurer votre DNS avec les paramètres suivants:"
        echo "Type: A"
        echo "Nom: @ (ou votre sous-domaine)"
        echo "Valeur: $SERVER_IP"
        echo ""
        read -p "Continuer quand même ? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Déploiement annulé"
            exit 1
        fi
    fi
}

# Fonction pour préparer les fichiers
prepare_files() {
    print_step 5 $TOTAL_STEPS "Préparation des fichiers de configuration"
    
    # Créer les répertoires nécessaires
    mkdir -p nginx/ssl
    mkdir -p data/mongodb
    mkdir -p data/certbot
    mkdir -p data/letsencrypt
    
    # Donner les permissions appropriées
    chmod 755 nginx/ssl
    chmod 755 data
    
    print_success "Répertoires créés"
    
    # Vérifier que tous les fichiers Docker sont présents
    if [ ! -f "docker-compose.yml" ]; then
        print_error "Fichier docker-compose.yml manquant"
        exit 1
    fi
    
    if [ ! -f "frontend/Dockerfile" ] || [ ! -f "backend/Dockerfile" ]; then
        print_error "Dockerfiles manquants"
        exit 1
    fi
    
    print_success "Tous les fichiers nécessaires sont présents"
}

# Fonction pour construire et démarrer les services
deploy_application() {
    print_step 6 $TOTAL_STEPS "Construction et démarrage de l'application"
    
    # Détecter la version de Docker Compose
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    print_info "Utilisation de: $COMPOSE_CMD"
    
    # Arrêter les services existants
    print_info "Arrêt des services existants..."
    $COMPOSE_CMD down --remove-orphans
    
    # Construire les images
    print_info "Construction des images Docker..."
    $COMPOSE_CMD build --no-cache
    
    # Démarrer les services
    print_info "Démarrage des services..."
    $COMPOSE_CMD up -d
    
    # Attendre que les services démarrent
    print_info "Attente du démarrage des services..."
    sleep 30
    
    print_success "Services démarrés"
}

# Fonction pour vérifier le déploiement
verify_deployment() {
    print_step 7 $TOTAL_STEPS "Vérification du déploiement"
    
    # Vérifier que les services sont en cours d'exécution
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    print_info "Vérification des services Docker..."
    $COMPOSE_CMD ps
    
    # Vérifier les ports
    print_info "Vérification des ports..."
    if netstat -tuln | grep -q ":80\|:443"; then
        print_success "Ports 80 et 443 en écoute"
    else
        print_warning "Problème avec les ports 80/443"
    fi
    
    # Test de santé HTTP
    print_info "Test de santé HTTP..."
    sleep 10
    
    if curl -s -f http://localhost/health > /dev/null; then
        print_success "Application accessible localement"
    else
        print_warning "Application pas encore accessible (normal si SSL en cours)"
    fi
    
    print_success "Vérification terminée"
}

# Fonction pour afficher les informations finales
show_final_info() {
    print_step 8 $TOTAL_STEPS "Informations de déploiement"
    
    echo ""
    echo -e "${GREEN}🎉 DÉPLOIEMENT RÉUSSI ! 🎉${NC}"
    echo ""
    echo -e "${BLUE}📋 Informations de votre installation:${NC}"
    echo "----------------------------------------"
    echo -e "🌐 URL de l'application: ${GREEN}https://$DOMAIN${NC}"
    echo -e "📧 Email SSL: ${GREEN}$ADMIN_EMAIL${NC}"
    echo -e "🔐 Base de données: ${GREEN}MongoDB avec mot de passe sécurisé${NC}"
    echo ""
    echo -e "${BLUE}📋 Commandes utiles:${NC}"
    echo "----------------------------------------"
    echo "• Voir les logs: docker compose logs -f"
    echo "• Redémarrer: docker compose restart"
    echo "• Arrêter: docker compose down"
    echo "• Sauvegarder BD: docker exec vote-secret-mongodb mongodump --out /backup"
    echo ""
    echo -e "${YELLOW}⏰ Le certificat SSL peut prendre quelques minutes à être généré${NC}"
    echo -e "${YELLOW}📧 Vérifiez les logs avec: docker compose logs certbot${NC}"
    echo ""
    echo -e "${GREEN}🗳️ SUPER Vote Secret est prêt à l'utilisation !${NC}"
    echo ""
}

# Fonction principale
main() {
    clear
    print_header
    
    echo "Ce script va déployer SUPER Vote Secret sur votre VPS."
    echo "Durée estimée: 5-10 minutes"
    echo ""
    read -p "Continuer ? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Déploiement annulé"
        exit 1
    fi
    
    # Exécution des étapes
    check_system_requirements
    install_docker
    configure_environment
    check_dns
    prepare_files
    deploy_application
    verify_deployment
    show_final_info
    
    echo -e "${GREEN}✨ Script terminé avec succès ! ✨${NC}"
}

# Gestion des erreurs
trap 'echo ""; print_error "Erreur durant le déploiement. Vérifiez les logs ci-dessus."; exit 1' ERR

# Lancer le script principal
main "$@"