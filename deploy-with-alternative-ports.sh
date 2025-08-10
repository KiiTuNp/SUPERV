#!/bin/bash

echo "=== DEPLOIEMENT AVEC PORTS ALTERNATIFS ==="
echo

# Backup original docker-compose.yml
if [ ! -f "docker-compose.yml.backup" ]; then
    cp docker-compose.yml docker-compose.yml.backup
    echo "✅ Sauvegarde de docker-compose.yml créée"
fi

# Create alternative port configuration
cat > docker-compose.override.yml << 'EOF'
services:
  nginx:
    ports:
      - "8080:80"
      - "8443:443"
EOF

echo "✅ Configuration avec ports alternatifs créée (8080:80, 8443:443)"

# Update environment file to reflect new ports
if [ -f ".env" ]; then
    # Update DOMAIN to include port if not already present
    if ! grep -q ":8080\|:8443" .env; then
        sed -i 's/^DOMAIN=\(.*\)$/DOMAIN=\1:8080/' .env
        echo "✅ Domaine mis à jour pour utiliser le port 8080"
    fi
fi

echo
echo "=== DEPLOIEMENT EN COURS ==="
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

echo
echo "=== VERIFICATION DES SERVICES ==="
sleep 10
docker-compose ps

echo
echo "✅ Application déployée avec succès !"
echo "🌐 Accès via : http://votre-domaine:8080"
echo "🔒 HTTPS via : https://votre-domaine:8443"
echo
echo "Pour revenir aux ports standards (80/443), utilisez :"
echo "1. Résolvez le conflit de port avec fix-port-conflict.sh"
echo "2. Supprimez docker-compose.override.yml"
echo "3. Relancez : docker-compose up -d"