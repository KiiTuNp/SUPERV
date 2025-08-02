#!/bin/bash

echo "=== MISE À JOUR DÉPLOIEMENT EXISTANT - UVICORN + URL BACKEND ==="
echo "Date: $(date)"
echo ""

# Couleurs
GREEN='33[0;32m'
RED='33[0;31m'
BLUE='33[0;34m'
YELLOW='33[1;33m'
NC='33[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

print_info "Mise à jour automatique pour utiliser Uvicorn"
echo ""

# 1. Détecter l'installation existante
INSTALL_PATHS=(
    "/opt/vote-secret"
    "/home/ubuntu/vote-secret" 
    "/home/vote-secret/vote-secret"
)

INSTALL_PATH=""
for path in "${INSTALL_PATHS[@]}"; do
    if [ -d "$path" ]; then
        INSTALL_PATH="$path"
        print_success "Installation détectée: $INSTALL_PATH"
        break
    fi
done

if [ -z "$INSTALL_PATH" ]; then
    print_error "Aucune installation Vote Secret détectée"
    print_info "Emplacements vérifiés: ${INSTALL_PATHS[*]}"
    exit 1
fi

# 2. Détecter l'utilisateur
USER="ubuntu"
if [ -d "/opt/vote-secret" ]; then
    USER="vote-secret"
fi

print_info "Utilisateur détecté: $USER"

# 3. Arrêter les services
print_info "Arrêt du service existant..."
sudo systemctl stop vote-secret 2>/dev/null || print_warning "Service non trouvé"

# 4. Installer Uvicorn si manquant
print_info "Installation/Mise à jour d'Uvicorn..."

VENV_PATH="$INSTALL_PATH/venv"
if [ -d "$VENV_PATH" ]; then
    sudo -u $USER $VENV_PATH/bin/pip install 'uvicorn[standard]'
    if [ $? -eq 0 ]; then
        print_success "Uvicorn installé"
    else
        print_error "Échec installation Uvicorn"
        exit 1
    fi
else
    print_error "Environnement virtuel non trouvé dans $VENV_PATH"
    exit 1
fi

# 5. Corriger l'URL backend dans le frontend
print_info "Correction de l'URL backend..."

FRONTEND_ENV_PATHS=(
    "$INSTALL_PATH/frontend/.env"
    "/var/www/vote-secret/.env"
    "$INSTALL_PATH/.env"
)

FRONTEND_ENV=""
for env_path in "${FRONTEND_ENV_PATHS[@]}"; do
    if [ -f "$env_path" ]; then
        FRONTEND_ENV="$env_path"
        break
    fi
done

if [ -n "$FRONTEND_ENV" ]; then
    print_info "Fichier .env frontend trouvé: $FRONTEND_ENV"
    
    # Sauvegarder
    cp "$FRONTEND_ENV" "$FRONTEND_ENV.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Corriger l'URL (supprimer /api s'il existe)
    if grep -q "REACT_APP_BACKEND_URL.*/api" "$FRONTEND_ENV"; then
        print_warning "URL backend contient /api, correction..."
        sed -i 's|REACT_APP_BACKEND_URL=\(.*\)/api|REACT_APP_BACKEND_URL=\1|' "$FRONTEND_ENV"
        print_success "URL backend corrigée"
    else
        print_info "URL backend déjà correcte"
    fi
    
    print_info "Configuration frontend actuelle:"
    grep "REACT_APP_BACKEND_URL" "$FRONTEND_ENV"
    
else
    print_error "Fichier .env frontend non trouvé"
    print_info "Emplacements vérifiés: ${FRONTEND_ENV_PATHS[*]}"
fi

# 6. Corriger le service SystemD
print_info "Mise à jour du service SystemD pour Uvicorn..."

sudo tee /etc/systemd/system/vote-secret.service > /dev/null << EOF
[Unit]
Description=Vote Secret v2.0 Backend Service (Uvicorn)
After=network.target mongod.service
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_PATH/backend
Environment=PATH=$INSTALL_PATH/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=$INSTALL_PATH/backend
ExecStart=$INSTALL_PATH/venv/bin/uvicorn server:app --host 127.0.0.1 --port 8001 --log-level info
Restart=always
RestartSec=3

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vote-secret

[Install]
WantedBy=multi-user.target
EOF

print_success "Service SystemD mis à jour avec Uvicorn"

# 7. Recharger et démarrer
print_info "Redémarrage des services..."

sudo systemctl daemon-reload
sudo systemctl enable vote-secret
sudo systemctl start vote-secret

# Attendre le démarrage
sleep 5

# 8. Vérification
if sudo systemctl is-active --quiet vote-secret; then
    print_success "Service Vote Secret (Uvicorn) démarré avec succès !"
    
    # Test de connectivité
    sleep 2
    if curl -s http://127.0.0.1:8001/api/health >/dev/null 2>&1; then
        print_success "Backend répond sur /api/health"
    else
        print_warning "Backend ne répond pas encore (peut prendre quelques secondes)"
    fi
    
else
    print_error "Service ne démarre pas"
    print_info "Logs d'erreur:"
    sudo journalctl -u vote-secret --no-pager -n 20
    exit 1
fi

# 9. Rebuild du frontend si nécessaire
if [ -n "$FRONTEND_ENV" ] && [ -d "$INSTALL_PATH/frontend" ]; then
    read -p "Rebuilder le frontend maintenant? (o/N): " DO_REBUILD
    if [[ "$DO_REBUILD" =~ ^[oO] ]]; then
        print_info "Rebuild du frontend..."
        
        cd "$INSTALL_PATH/frontend"
        if sudo -u $USER npm run build; then
            print_success "Rebuild terminé"
            
            # Copier vers www si le répertoire existe
            if [ -d "/var/www/vote-secret" ]; then
                print_info "Déploiement vers /var/www/vote-secret..."
                sudo cp -r build/* /var/www/vote-secret/
                sudo chown -R www-data:www-data /var/www/vote-secret/
                print_success "Frontend redéployé"
                
                # Redémarrer Nginx
                sudo systemctl restart nginx
                print_success "Nginx redémarré"
            fi
        else
            print_error "Échec du rebuild"
        fi
    fi
fi

print_success "Mise à jour terminée !"
echo ""
print_info "Changements appliqués:"
echo "  ✅ Service SystemD utilise maintenant Uvicorn"
echo "  ✅ URL backend corrigée (sans /api)"
echo "  ✅ Service redémarré et opérationnel"
echo ""
print_info "Commandes utiles:"
echo "  - Status: sudo systemctl status vote-secret"
echo "  - Logs: sudo journalctl -u vote-secret -f"
echo "  - Test: curl http://127.0.0.1:8001/api/health"