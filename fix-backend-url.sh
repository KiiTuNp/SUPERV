#!/bin/bash

echo "=== CORRECTION URL BACKEND - VPS UBUNTU ==="
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

print_info "Correction du problème d'URL backend (/api/api/)"

# 1. Diagnostiquer le problème
print_info "Étape 1: Diagnostic du problème d'URL"

echo "Problème détecté: Double préfixe /api/api/ au lieu de /api/"
echo "Cause: REACT_APP_BACKEND_URL contient déjà /api mais le frontend ajoute /api"

# 2. Trouver le fichier .env du frontend
FRONTEND_ENV=""
if [ -f "/home/ubuntu/vote-secret/frontend/.env" ]; then
    FRONTEND_ENV="/home/ubuntu/vote-secret/frontend/.env"
elif [ -f "/var/www/vote-secret/.env" ]; then
    FRONTEND_ENV="/var/www/vote-secret/.env"
elif [ -f "/home/ubuntu/vote-secret/.env" ]; then
    FRONTEND_ENV="/home/ubuntu/vote-secret/.env"
else
    print_error "Fichier .env du frontend non trouvé"
    print_info "Emplacements vérifiés:"
    echo "  - /home/ubuntu/vote-secret/frontend/.env"
    echo "  - /var/www/vote-secret/.env"
    echo "  - /home/ubuntu/vote-secret/.env"
    
    read -p "Chemin vers le fichier .env du frontend: " FRONTEND_ENV
    if [ ! -f "$FRONTEND_ENV" ]; then
        print_error "Fichier spécifié non trouvé: $FRONTEND_ENV"
        exit 1
    fi
fi

print_success "Fichier .env trouvé: $FRONTEND_ENV"

# 3. Afficher la configuration actuelle
print_info "Configuration actuelle:"
if grep -q "REACT_APP_BACKEND_URL" "$FRONTEND_ENV"; then
    CURRENT_URL=$(grep "REACT_APP_BACKEND_URL" "$FRONTEND_ENV" | cut -d'=' -f2)
    echo "  REACT_APP_BACKEND_URL=$CURRENT_URL"
else
    print_warning "REACT_APP_BACKEND_URL non trouvé dans le fichier .env"
    CURRENT_URL=""
fi

# 4. Demander la configuration correcte
print_info "Correction nécessaire:"
echo ""
echo "Le frontend ajoute automatiquement '/api' aux requêtes."
echo "Donc REACT_APP_BACKEND_URL ne doit PAS contenir '/api'"
echo ""
echo "Exemples de configuration correcte:"
echo "  - http://votre-domaine.com (sans /api)"
echo "  - https://votre-domaine.com (sans /api)"
echo "  - http://127.0.0.1:8001 (pour test local direct)"
echo ""

# Suggérer une correction automatique
if [[ "$CURRENT_URL" == *"/api"* ]]; then
    SUGGESTED_URL=$(echo "$CURRENT_URL" | sed 's|/api$||')
    print_info "Correction suggérée:"
    echo "  Actuel: $CURRENT_URL"
    echo "  Corrigé: $SUGGESTED_URL"
    echo ""
    
    read -p "Utiliser cette correction automatique? (o/N): " AUTO_FIX
    if [[ "$AUTO_FIX" =~ ^[oO] ]]; then
        NEW_URL="$SUGGESTED_URL"
    else
        read -p "Nouvelle URL backend (sans /api): " NEW_URL
    fi
else
    read -p "Quelle est votre URL backend (sans /api)? " NEW_URL
fi

# 5. Valider l'URL
if [[ ! "$NEW_URL" =~ ^https?:// ]]; then
    print_error "URL invalide. Elle doit commencer par http:// ou https://"
    exit 1
fi

if [[ "$NEW_URL" == *"/api"* ]]; then
    print_error "L'URL ne doit PAS contenir '/api' !"
    print_info "Le frontend l'ajoute automatiquement"
    exit 1
fi

print_success "URL validée: $NEW_URL"

# 6. Sauvegarder l'ancien fichier
cp "$FRONTEND_ENV" "$FRONTEND_ENV.backup.$(date +%Y%m%d_%H%M%S)"
print_success "Sauvegarde créée: $FRONTEND_ENV.backup.*"

# 7. Appliquer la correction
if grep -q "REACT_APP_BACKEND_URL" "$FRONTEND_ENV"; then
    # Remplacer la ligne existante
    sed -i "s|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=$NEW_URL|" "$FRONTEND_ENV"
else
    # Ajouter la ligne
    echo "REACT_APP_BACKEND_URL=$NEW_URL" >> "$FRONTEND_ENV"
fi

print_success "Configuration mise à jour"

# 8. Afficher la nouvelle configuration
print_info "Nouvelle configuration:"
grep "REACT_APP_BACKEND_URL" "$FRONTEND_ENV"

# 9. Instructions pour appliquer les changements
print_info "Étapes pour appliquer les changements:"

echo ""
echo "1. Rebuild du frontend:"
echo "   cd /home/ubuntu/vote-secret/frontend"
echo "   npm run build"
echo ""
echo "2. Copier vers le serveur web (si utilisé):"
echo "   sudo cp -r build/* /var/www/vote-secret/"
echo "   sudo chown -R www-data:www-data /var/www/vote-secret/"
echo ""
echo "3. Redémarrer les services:"
echo "   sudo systemctl restart nginx"
echo "   sudo systemctl restart vote-secret"
echo ""

# 10. Test automatique si possible
if command -v curl >/dev/null 2>&1; then
    print_info "Test de l'URL backend:"
    
    HEALTH_URL="$NEW_URL/api/health"
    echo "Test: $HEALTH_URL"
    
    if curl -s --connect-timeout 5 "$HEALTH_URL" >/dev/null 2>&1; then
        print_success "Backend accessible sur $HEALTH_URL"
    else
        print_warning "Backend non accessible sur $HEALTH_URL"
        print_info "Vérifiez que le service backend fonctionne"
    fi
fi

print_success "Correction de l'URL terminée !"
echo ""
print_warning "N'oubliez pas de rebuilder et redéployer le frontend !"

# 11. Proposer le rebuild automatique
read -p "Rebuilder le frontend maintenant? (o/N): " DO_REBUILD
if [[ "$DO_REBUILD" =~ ^[oO] ]]; then
    print_info "Rebuild du frontend..."
    
    cd /home/ubuntu/vote-secret/frontend
    if npm run build; then
        print_success "Rebuild terminé"
        
        # Copier vers www si le répertoire existe
        if [ -d "/var/www/vote-secret" ]; then
            print_info "Copie vers /var/www/vote-secret..."
            sudo cp -r build/* /var/www/vote-secret/
            sudo chown -R www-data:www-data /var/www/vote-secret/
            print_success "Frontend déployé"
        fi
    else
        print_error "Échec du rebuild"
    fi
fi