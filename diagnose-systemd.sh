#!/bin/bash

echo "=== DIAGNOSTIC SYSTEMD VOTE SECRET ==="
echo "Date: $(date)"
echo ""

echo "1. Vérification des fichiers requis:"
echo "-----------------------------------"

# Vérifier les fichiers
FILES=(
    "/opt/vote-secret/backend/server.py"
    "/opt/vote-secret/venv/bin/gunicorn"
    "/opt/vote-secret/config/gunicorn.conf.py"
    "/opt/vote-secret/backend/.env"
    "/var/log/vote-secret"
)

for file in "${FILES[@]}"; do
    if [ -e "$file" ]; then
        echo "✅ $file existe"
    else
        echo "❌ $file MANQUANT"
    fi
done

echo ""
echo "2. Vérification des permissions:"
echo "-------------------------------"

# Vérifier les permissions
echo "Propriétaire de /opt/vote-secret:"
ls -la /opt/ | grep vote-secret

echo ""
echo "Contenu de /opt/vote-secret:"
ls -la /opt/vote-secret/

echo ""
echo "3. Test de l'application FastAPI:"
echo "--------------------------------"

# Test de l'application
cd /opt/vote-secret/backend
if [ -f "server.py" ]; then
    echo "Fichier server.py trouvé, test de l'import..."
    sudo -u vote-secret /opt/vote-secret/venv/bin/python -c "
import sys
sys.path.append('/opt/vote-secret/backend')
try:
    from server import app
    print('✅ Import de l\'application réussi')
    print(f'Type de l\'application: {type(app)}')
except Exception as e:
    print(f'❌ Erreur d\'import: {e}')
"
else
    echo "❌ server.py non trouvé"
fi

echo ""
echo "4. Test de Gunicorn:"
echo "-------------------"

# Test Gunicorn
if [ -f "/opt/vote-secret/config/gunicorn.conf.py" ]; then
    echo "Configuration Gunicorn trouvée, test..."
    sudo -u vote-secret /opt/vote-secret/venv/bin/gunicorn --config /opt/vote-secret/config/gunicorn.conf.py --check-config server:app
    if [ $? -eq 0 ]; then
        echo "✅ Configuration Gunicorn valide"
    else
        echo "❌ Configuration Gunicorn invalide"
    fi
else
    echo "❌ Configuration Gunicorn manquante"
fi

echo ""
echo "5. Variables d'environnement:"
echo "----------------------------"

# Vérifier les variables d'environnement
if [ -f "/opt/vote-secret/backend/.env" ]; then
    echo "Contenu du fichier .env:"
    cat /opt/vote-secret/backend/.env
else
    echo "❌ Fichier .env manquant"
fi

echo ""
echo "6. Logs du service:"
echo "------------------"

echo "Dernières 10 lignes des logs systemd:"
journalctl -u vote-secret --no-pager -n 10

echo ""
echo "7. Port et processus:"
echo "--------------------"

echo "Processus écoutant sur le port 8001:"
sudo netstat -tlnp | grep 8001 || echo "Aucun processus sur le port 8001"

echo ""
echo "8. Test de connectivité MongoDB:"
echo "-------------------------------"

# Test MongoDB
if command -v mongosh >/dev/null 2>&1; then
    echo "Test de connexion MongoDB avec mongosh..."
    mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ MongoDB accessible"
    else
        echo "❌ MongoDB non accessible"
    fi
elif command -v mongo >/dev/null 2>&1; then
    echo "Test de connexion MongoDB avec mongo..."  
    mongo --eval "db.adminCommand('ping')" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ MongoDB accessible"
    else
        echo "❌ MongoDB non accessible"
    fi
else
    echo "⚠️ Client MongoDB non trouvé"
fi

echo ""
echo "=== FIN DU DIAGNOSTIC ==="