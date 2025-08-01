#!/bin/bash

echo "=== RÉPARATION VPS UBUNTU - VOTE SECRET ==="
echo "Date: $(date)"
echo ""

set -e

# Couleurs
RED='33[0;31m'
GREEN='33[0;32m'
YELLOW='33[1;33m'
BLUE='33[0;34m'
NC='33[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Vérifier qu'on est bien sur Ubuntu
if [ ! -f /etc/os-release ] || ! grep -q "Ubuntu" /etc/os-release; then
    print_error "Ce script est conçu pour Ubuntu"
    exit 1
fi

print_info "Réparation du service Vote Secret sur VPS Ubuntu"

# 1. Vérifier la structure des fichiers
print_info "Étape 1: Vérification de la structure des fichiers"

if [ ! -d "/home/ubuntu/vote-secret" ]; then
    print_error "Répertoire /home/ubuntu/vote-secret manquant"
    print_info "Vous devez d'abord déployer l'application dans ce répertoire"
    exit 1
fi

if [ ! -f "/home/ubuntu/vote-secret/backend/server.py" ]; then
    print_error "Fichier server.py manquant dans /home/ubuntu/vote-secret/backend/"
    exit 1
fi

if [ ! -f "/home/ubuntu/vote-secret/venv/bin/gunicorn" ]; then
    print_error "Gunicorn manquant dans l'environnement virtuel"
    print_info "Tentative d'installation de Gunicorn..."
    
    # Installer Gunicorn si manquant
    sudo -u ubuntu /home/ubuntu/vote-secret/venv/bin/pip install gunicorn uvicorn[standard]
    
    if [ $? -eq 0 ]; then
        print_success "Gunicorn installé"
    else
        print_error "Échec installation Gunicorn"
        exit 1
    fi
fi

print_success "Structure des fichiers OK"

# 2. Vérifier et corriger les permissions
print_info "Étape 2: Correction des permissions"

sudo chown -R ubuntu:ubuntu /home/ubuntu/vote-secret/
sudo chmod +x /home/ubuntu/vote-secret/venv/bin/*

print_success "Permissions corrigées"

# 3. Test de l'application
print_info "Étape 3: Test de l'application FastAPI"

cd /home/ubuntu/vote-secret/backend

# Test d'import
sudo -u ubuntu bash -c '
export PYTHONPATH=/home/ubuntu/vote-secret/backend
cd /home/ubuntu/vote-secret/backend
/home/ubuntu/vote-secret/venv/bin/python -c "
try:
    from server import app
    print(\"✅ Import réussi\")
    print(\"Type:\", type(app))
except Exception as e:
    print(\"❌ Erreur import:\", str(e))
    exit(1)
"'

if [ $? -ne 0 ]; then
    print_error "L'application FastAPI ne peut pas être importée"
    exit 1
fi

print_success "Application FastAPI importée avec succès"

# 4. Créer un fichier .env si manquant
print_info "Étape 4: Vérification du fichier .env"

if [ ! -f "/home/ubuntu/vote-secret/backend/.env" ]; then
    print_warning "Fichier .env manquant, création d'un fichier de base"
    
    sudo -u ubuntu tee /home/ubuntu/vote-secret/backend/.env > /dev/null << EOF
# Vote Secret Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=vote_secret
CORS_ORIGINS=*
LOG_LEVEL=info
EOF
    
    print_success "Fichier .env créé"
fi

# 5. Créer une configuration Gunicorn optimisée
print_info "Étape 5: Création de la configuration Gunicorn"

sudo -u ubuntu tee /home/ubuntu/vote-secret/gunicorn.conf.py > /dev/null << EOF
# Configuration Gunicorn pour Vote Secret
import multiprocessing

# Serveur
bind = "127.0.0.1:8001"
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Timeouts
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logs
accesslog = "/var/log/vote-secret-access.log"
errorlog = "/var/log/vote-secret-error.log"
loglevel = "info"

# Process
preload_app = True
proc_name = "vote-secret"

def when_ready(server):
    server.log.info("Vote Secret ready on %s", server.address)
EOF

print_success "Configuration Gunicorn créée"

# 6. Créer le service SystemD corrigé
print_info "Étape 6: Installation du service SystemD corrigé"

sudo tee /etc/systemd/system/vote-secret.service > /dev/null << EOF
[Unit]
Description=Vote Secret v2.0 Backend Service
After=network.target mongod.service
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/vote-secret/backend
Environment=PATH=/home/ubuntu/vote-secret/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/home/ubuntu/vote-secret/backend
ExecStart=/home/ubuntu/vote-secret/venv/bin/gunicorn --config /home/ubuntu/vote-secret/gunicorn.conf.py server:app
Restart=always
RestartSec=3

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vote-secret

[Install]
WantedBy=multi-user.target
EOF

print_success "Service SystemD installé"

# 7. Recharger et démarrer le service
print_info "Étape 7: Démarrage du service"

sudo systemctl daemon-reload
sudo systemctl enable vote-secret
sudo systemctl stop vote-secret 2>/dev/null || true

# Test préliminaire
print_info "Test préliminaire de la commande..."
sudo -u ubuntu bash -c '
cd /home/ubuntu/vote-secret/backend
export PATH=/home/ubuntu/vote-secret/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH=/home/ubuntu/vote-secret/backend
timeout 10 /home/ubuntu/vote-secret/venv/bin/gunicorn --config /home/ubuntu/vote-secret/gunicorn.conf.py --check-config server:app
'

if [ $? -eq 0 ]; then
    print_success "Configuration Gunicorn valide"
else
    print_error "Configuration Gunicorn invalide"
    exit 1
fi

# Démarrer le service
sudo systemctl start vote-secret

# Attendre et vérifier
sleep 5

if sudo systemctl is-active --quiet vote-secret; then
    print_success "Service Vote Secret démarré avec succès !"
    
    # Test de connectivité
    sleep 2
    if curl -s http://127.0.0.1:8001/api/health >/dev/null 2>&1; then
        print_success "Backend répond sur /api/health"
    else
        print_warning "Backend ne répond pas encore (peut prendre quelques secondes)"
    fi
    
    print_info "Statut du service:"
    sudo systemctl status vote-secret --no-pager -l
    
else
    print_error "Service ne démarre pas"
    print_info "Logs d'erreur:"
    sudo journalctl -u vote-secret --no-pager -n 20
    exit 1
fi

print_success "Réparation terminée ! Vote Secret opérationnel."
echo ""
print_info "Commandes utiles:"
echo "  - Status: sudo systemctl status vote-secret"
echo "  - Logs: sudo journalctl -u vote-secret -f"
echo "  - Restart: sudo systemctl restart vote-secret"
echo "  - Test: curl http://127.0.0.1:8001/api/health"