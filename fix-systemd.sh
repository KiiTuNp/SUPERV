#!/bin/bash

echo "=== RÉPARATION SERVICE SYSTEMD VOTE SECRET ==="
echo "Date: $(date)"
echo ""

set -e

# Couleurs pour les messages
RED='33[0;31m'
GREEN='33[0;32m'
YELLOW='33[1;33m'
BLUE='33[0;34m'
NC='33[0m' # No Color

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Arrêter le service actuel s'il existe
print_info "Arrêt du service actuel..."
sudo systemctl stop vote-secret 2>/dev/null || true
sudo systemctl disable vote-secret 2>/dev/null || true

# Créer les répertoires nécessaires
print_info "Création des répertoires nécessaires..."
sudo mkdir -p /var/log/vote-secret
sudo chown vote-secret:vote-secret /var/log/vote-secret 2>/dev/null || print_warning "Utilisateur vote-secret non trouvé"

# S'assurer que l'utilisateur vote-secret existe
if ! id "vote-secret" &>/dev/null; then
    print_info "Création de l'utilisateur vote-secret..."
    sudo useradd -r -s /bin/false -d /opt/vote-secret -c 'Vote Secret Application' vote-secret
    print_success "Utilisateur vote-secret créé"
else
    print_success "Utilisateur vote-secret existe"
fi

# Vérifier et corriger les permissions
print_info "Correction des permissions..."
sudo chown -R vote-secret:vote-secret /opt/vote-secret 2>/dev/null || print_warning "Répertoire /opt/vote-secret non trouvé"
sudo chown vote-secret:vote-secret /var/log/vote-secret

# Copier le fichier service corrigé
print_info "Installation du fichier service SystemD corrigé..."
if [ -f "/app/vote-secret-systemd-fixed.service" ]; then
    sudo cp /app/vote-secret-systemd-fixed.service /etc/systemd/system/vote-secret.service
    print_success "Fichier service copié"
else
    print_error "Fichier service corrigé non trouvé"
    exit 1
fi

# Recharger systemd
print_info "Rechargement de systemd..."
sudo systemctl daemon-reload

# Activer le service
print_info "Activation du service..."
sudo systemctl enable vote-secret

# Vérifier la configuration avant de démarrer
print_info "Vérification de la configuration..."

# Vérifier que les fichiers existent
REQUIRED_FILES=(
    "/opt/vote-secret/backend/server.py"
    "/opt/vote-secret/venv/bin/gunicorn"
    "/opt/vote-secret/config/gunicorn.conf.py"
)

ALL_FILES_OK=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Fichier trouvé: $file"
    else
        print_error "Fichier manquant: $file"
        ALL_FILES_OK=false
    fi
done

if [ "$ALL_FILES_OK" = false ]; then
    print_error "Fichiers requis manquants. Déploiement incomplet."
    exit 1
fi

# Test de la configuration Gunicorn
print_info "Test de la configuration Gunicorn..."
cd /opt/vote-secret/backend
if sudo -u vote-secret /opt/vote-secret/venv/bin/gunicorn --config /opt/vote-secret/config/gunicorn.conf.py --check-config server:app; then
    print_success "Configuration Gunicorn valide"
else
    print_error "Configuration Gunicorn invalide"
    exit 1
fi

# Démarrer le service
print_info "Démarrage du service Vote Secret..."
sudo systemctl start vote-secret

# Attendre un moment pour que le service démarre
sleep 3

# Vérifier le statut
print_info "Vérification du statut du service..."
if sudo systemctl is-active --quiet vote-secret; then
    print_success "Service Vote Secret actif !"
    
    # Test de connectivité
    print_info "Test de connectivité sur le port 8001..."
    sleep 2
    if curl -s http://127.0.0.1:8001/api/health >/dev/null 2>&1; then
        print_success "Backend répond correctement sur /api/health"
    else
        print_warning "Backend ne répond pas encore (peut prendre quelques secondes)"
    fi
    
    # Afficher les logs récents
    print_info "Dernières lignes des logs:"
    sudo journalctl -u vote-secret --no-pager -n 5
    
else
    print_error "Service Vote Secret non actif"
    print_info "Logs d'erreur:"
    sudo journalctl -u vote-secret --no-pager -n 10
    exit 1
fi

print_success "Réparation terminée ! Service Vote Secret opérationnel."
echo ""
print_info "Commandes utiles:"
echo "  - Status: sudo systemctl status vote-secret"
echo "  - Logs: sudo journalctl -u vote-secret -f"
echo "  - Restart: sudo systemctl restart vote-secret"
echo "  - Test: curl http://127.0.0.1:8001/api/health"