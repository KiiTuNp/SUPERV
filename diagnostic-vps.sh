#!/bin/bash

echo "=== DIAGNOSTIC VPS UBUNTU - VOTE SECRET ==="
echo "Date: $(date)"
echo ""

# Couleurs
RED='33[0;31m'
GREEN='33[0;32m'
YELLOW='33[1;33m'
NC='33[0m'

print_check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
    fi
}

echo "1. Vérification de l'utilisateur ubuntu:"
echo "---------------------------------------"
id ubuntu 2>/dev/null && print_check "Utilisateur ubuntu existe" || echo -e "${RED}❌ Utilisateur ubuntu n'existe pas${NC}"

echo ""
echo "2. Vérification des fichiers dans /home/ubuntu/vote-secret/:"
echo "----------------------------------------------------------"

if [ -d "/home/ubuntu/vote-secret" ]; then
    echo "✅ Répertoire /home/ubuntu/vote-secret existe"
    echo "Contenu:"
    ls -la /home/ubuntu/vote-secret/
    
    echo ""
    echo "Contenu backend:"
    if [ -d "/home/ubuntu/vote-secret/backend" ]; then
        ls -la /home/ubuntu/vote-secret/backend/
    else
        echo "❌ Répertoire backend manquant"
    fi
    
    echo ""
    echo "Vérification du fichier server.py:"
    if [ -f "/home/ubuntu/vote-secret/backend/server.py" ]; then
        echo "✅ server.py existe"
        echo "Taille: $(stat -c%s /home/ubuntu/vote-secret/backend/server.py) bytes"
    else
        echo "❌ server.py manquant"
    fi
    
    echo ""
    echo "Vérification de l'environnement virtuel:"
    if [ -f "/home/ubuntu/vote-secret/venv/bin/gunicorn" ]; then
        echo "✅ Gunicorn existe dans venv"
        echo "Version Gunicorn:"
        /home/ubuntu/vote-secret/venv/bin/gunicorn --version
    else
        echo "❌ Gunicorn manquant dans venv"
        if [ -d "/home/ubuntu/vote-secret/venv" ]; then
            echo "Contenu de venv/bin:"
            ls -la /home/ubuntu/vote-secret/venv/bin/ | head -10
        fi
    fi
    
else
    echo "❌ Répertoire /home/ubuntu/vote-secret n'existe pas"
    echo "Répertoires dans /home/ubuntu:"
    ls -la /home/ubuntu/ 2>/dev/null || echo "Répertoire /home/ubuntu inaccessible"
fi

echo ""
echo "3. Test d'exécution manuelle:"
echo "----------------------------"

echo "Test de l'import Python:"
cd /home/ubuntu/vote-secret/backend 2>/dev/null
if [ $? -eq 0 ]; then
    export PYTHONPATH=/home/ubuntu/vote-secret/backend
    /home/ubuntu/vote-secret/venv/bin/python -c "
import sys
print('Python path:', sys.path)
try:
    from server import app
    print('✅ Import de server.app réussi')
    print('Type app:', type(app))
except Exception as e:
    print('❌ Erreur import:', str(e))
    import traceback
    traceback.print_exc()
" 2>&1
else
    echo "❌ Impossible d'accéder au répertoire backend"
fi

echo ""
echo "4. Vérification des permissions:"
echo "-------------------------------"
echo "Propriétaire des fichiers:"
ls -la /home/ubuntu/vote-secret/ 2>/dev/null | head -5

echo ""
echo "5. Test de la commande SystemD:"
echo "------------------------------"
echo "Commande exacte du service:"
echo '/home/ubuntu/vote-secret/venv/bin/gunicorn -w 4 -b 127.0.0.1:8001 --timeout 120 --keepalive 5 --max-requests 1000 server:app'

echo ""
echo "Test d'exécution manuelle (en tant qu'ubuntu):"
sudo -u ubuntu bash -c '
cd /home/ubuntu/vote-secret/backend
export PATH=/home/ubuntu/vote-secret/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH=/home/ubuntu/vote-secret/backend
echo "PATH: $PATH"
echo "PYTHONPATH: $PYTHONPATH"
echo "Working directory: $(pwd)"
timeout 5 /home/ubuntu/vote-secret/venv/bin/gunicorn -w 1 -b 127.0.0.1:8001 --timeout 30 server:app --preload
'

echo ""
echo "6. Logs SystemD récents:"
echo "----------------------"
journalctl -u vote-secret --no-pager -n 20

echo ""
echo "=== FIN DU DIAGNOSTIC ==="