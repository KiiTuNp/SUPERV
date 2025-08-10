#!/bin/bash

# SUPER Vote Secret - Configuration Post-Installation
# Configure Nginx avec le domaine spécifique après déploiement

set -e

DOMAIN=${1:-}
NGINX_CONFIG="/root/nginx/nginx.conf"
TEMP_CONFIG="/tmp/nginx.conf.temp"

if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain>"
    echo "Example: $0 vote.example.com"
    exit 1
fi

echo "🔧 Configuration Nginx pour le domaine: $DOMAIN"

# Remplacer les placeholders dans la configuration Nginx
sed "s/server_name _;/server_name $DOMAIN;/g" "$NGINX_CONFIG" > "$TEMP_CONFIG"
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" "$TEMP_CONFIG"

# Copier la configuration modifiée
cp "$TEMP_CONFIG" "$NGINX_CONFIG"

echo "✅ Configuration Nginx mise à jour pour $DOMAIN"

# Redémarrer Nginx si Docker Compose est disponible
if command -v docker &> /dev/null; then
    if docker compose version &> /dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    fi
    
    if [ ! -z "$COMPOSE_CMD" ]; then
        echo "🔄 Redémarrage de Nginx..."
        $COMPOSE_CMD restart nginx
        echo "✅ Nginx redémarré"
    fi
fi

echo "🎉 Configuration terminée pour $DOMAIN"