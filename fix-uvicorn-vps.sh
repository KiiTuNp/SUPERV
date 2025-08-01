#!/bin/bash

echo "=== CORRECTION UVICORN - VPS UBUNTU ==="
echo "Date: $(date)"
echo ""

# Couleurs
GREEN='33[0;32m'
RED='33[0;31m'
BLUE='33[0;34m'
NC='33[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

print_info "Configuration SystemD pour Uvicorn direct"

# 1. Vérifier Uvicorn
print_info "Étape 1: Vérification d'Uvicorn"

if [ ! -f "/home/ubuntu/vote-secret/venv/bin/uvicorn" ]; then
    print_info "Installation d'Uvicorn..."
    sudo -u ubuntu /home/ubuntu/vote-secret/venv/bin/pip install "uvicorn[standard]"
    
    if [ $? -eq 0 ]; then
        print_success "Uvicorn installé"
    else
        print_error "Échec installation Uvicorn"
        exit 1
    fi
else
    print_success "Uvicorn disponible"
fi

# 2. Test de l'application avec Uvicorn
print_info "Étape 2: Test de l'application avec Uvicorn"

cd /home/ubuntu/vote-secret/backend

# Test d'import
sudo -u ubuntu bash -c '
export PYTHONPATH=/home/ubuntu/vote-secret/backend
cd /home/ubuntu/vote-secret/backend
/home/ubuntu/vote-secret/venv/bin/python -c "
try:
    from server import app
    print(\"✅ Import server:app réussi\")
    print(\"Type app:\", type(app))
except Exception as e:
    print(\"❌ Erreur import:\", str(e))
    import traceback
    traceback.print_exc()
    exit(1)
"'

if [ $? -ne 0 ]; then
    print_error "L'application ne peut pas être importée"
    exit 1
fi

print_success "Application importée avec succès"

# 3. Test manuel d'Uvicorn
print_info "Étape 3: Test manuel d'Uvicorn (5 secondes)"

sudo -u ubuntu bash -c '
cd /home/ubuntu/vote-secret/backend
export PATH=/home/ubuntu/vote-secret/venv/bin:$PATH
export PYTHONPATH=/home/ubuntu/vote-secret/backend
echo "Test Uvicorn..."
timeout 5 uvicorn server:app --host 127.0.0.1 --port 8001 --log-level info
echo "Test terminé"
' 2>&1

print_success "Test Uvicorn terminé"

# 4. Créer le service SystemD pour Uvicorn
print_info "Étape 4: Configuration SystemD pour Uvicorn"

sudo tee /etc/systemd/system/vote-secret.service > /dev/null << 'EOF'
[Unit]
Description=Vote Secret v2.0 Backend Service (Uvicorn)
After=network.target mongod.service
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/vote-secret/backend
Environment=PATH=/home/ubuntu/vote-secret/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/home/ubuntu/vote-secret/backend
ExecStart=/home/ubuntu/vote-secret/venv/bin/uvicorn server:app --host 127.0.0.1 --port 8001 --log-level info
Restart=always
RestartSec=3

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vote-secret

[Install]
WantedBy=multi-user.target
EOF

print_success "Service SystemD configuré pour Uvicorn"

# 5. Recharger et démarrer
print_info "Étape 5: Démarrage du service"

sudo systemctl daemon-reload
sudo systemctl enable vote-secret
sudo systemctl stop vote-secret 2>/dev/null || true

# Démarrer le service
sudo systemctl start vote-secret

# Attendre et vérifier
sleep 5

if sudo systemctl is-active --quiet vote-secret; then
    print_success "Service Vote Secret (Uvicorn) démarré avec succès !"
    
    # Test de connectivité
    sleep 2
    if curl -s http://127.0.0.1:8001/api/health >/dev/null 2>&1; then
        print_success "Backend répond sur /api/health"
    else
        print_info "Test de connectivité..."
        sleep 3
        if curl -s http://127.0.0.1:8001/api/health >/dev/null 2>&1; then
            print_success "Backend répond maintenant sur /api/health"
        else
            print_error "Backend ne répond pas"
        fi
    fi
    
    print_info "Statut du service:"
    sudo systemctl status vote-secret --no-pager -l
    
else
    print_error "Service ne démarre pas"
    print_info "Logs d'erreur:"
    sudo journalctl -u vote-secret --no-pager -n 20
    exit 1
fi

print_success "Configuration Uvicorn terminée !"
echo ""
print_info "Commandes utiles:"
echo "  - Status: sudo systemctl status vote-secret"
echo "  - Logs: sudo journalctl -u vote-secret -f"
echo "  - Restart: sudo systemctl restart vote-secret"
echo "  - Test: curl http://127.0.0.1:8001/api/health"