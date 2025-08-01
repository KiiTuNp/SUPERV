# CORRECTION SERVICE SYSTEMD - VPS UBUNTU

## 🔍 Diagnostic de votre problème

L'erreur `status=203/EXEC` indique que SystemD ne peut pas exécuter la commande. Voici les causes possibles :

### ❌ Problèmes potentiels :

1. **Fichiers manquants** :
   - `/home/ubuntu/vote-secret/backend/server.py` n'existe pas
   - `/home/ubuntu/vote-secret/venv/bin/gunicorn` n'est pas installé
   - Environnement virtuel incomplet

2. **Permissions incorrectes** :
   - L'utilisateur `ubuntu` ne peut pas accéder aux fichiers
   - Permissions d'exécution manquantes sur l'environnement virtuel

3. **Dépendances manquantes** :
   - Gunicorn pas installé dans l'environnement virtuel
   - Module `uvicorn` manquant pour les workers
   - Variables d'environnement incorrectes

4. **Configuration Python** :
   - Le module `server` ne peut pas être importé
   - PYTHONPATH mal configuré
   - Dépendances Python manquantes

## 🛠️ Solutions automatiques

### 1. Diagnostic complet (RECOMMANDÉ)
```bash
# Télécharger et exécuter le diagnostic
curl -sSL https://raw.githubusercontent.com/user/repo/main/diagnostic-vps.sh | bash

# OU si vous avez les fichiers localement :
sudo bash /app/diagnostic-vps.sh
```

### 2. Réparation automatique complète
```bash
# Exécuter le script de réparation
sudo bash /app/fix-vps-ubuntu.sh
```

## 🔧 Solutions manuelles

### Étape 1 : Vérifier la structure des fichiers
```bash
# Vérifier que les fichiers existent
ls -la /home/ubuntu/vote-secret/
ls -la /home/ubuntu/vote-secret/backend/
ls -la /home/ubuntu/vote-secret/venv/bin/

# Vérifier server.py
cat /home/ubuntu/vote-secret/backend/server.py | head -10
```

### Étape 2 : Installer les dépendances manquantes
```bash
# Aller dans le répertoire
cd /home/ubuntu/vote-secret

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install gunicorn uvicorn[standard]
pip install -r backend/requirements.txt

# Vérifier l'installation
which gunicorn
gunicorn --version
```

### Étape 3 : Tester l'application manuellement
```bash
# Aller dans le backend
cd /home/ubuntu/vote-secret/backend

# Tester l'import Python
export PYTHONPATH=/home/ubuntu/vote-secret/backend
python -c "from server import app; print('OK')"

# Tester Gunicorn
/home/ubuntu/vote-secret/venv/bin/gunicorn --check-config server:app
```

### Étape 4 : Corriger les permissions
```bash
# S'assurer que ubuntu est propriétaire
sudo chown -R ubuntu:ubuntu /home/ubuntu/vote-secret/

# Permissions d'exécution
chmod +x /home/ubuntu/vote-secret/venv/bin/*
```

### Étape 5 : Configuration Gunicorn améliorée
```bash
# Créer une configuration Gunicorn
cat > /home/ubuntu/vote-secret/gunicorn.conf.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:8001"
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
max_requests = 1000
preload_app = True
EOF
```

### Étape 6 : Service SystemD amélioré
```bash
# Créer le service avec configuration Gunicorn
sudo tee /etc/systemd/system/vote-secret.service << 'EOF'
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
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vote-secret

[Install]
WantedBy=multi-user.target
EOF

# Recharger et démarrer
sudo systemctl daemon-reload
sudo systemctl enable vote-secret
sudo systemctl restart vote-secret
```

### Étape 7 : Vérification finale
```bash
# Vérifier le statut
sudo systemctl status vote-secret

# Voir les logs
sudo journalctl -u vote-secret -f

# Tester la connectivité
curl http://127.0.0.1:8001/api/health
```

## 🚨 Commandes de débogage

### Si le service ne démarre toujours pas :

```bash
# Test manuel complet
sudo -u ubuntu bash -c '
cd /home/ubuntu/vote-secret/backend
export PATH=/home/ubuntu/vote-secret/venv/bin:$PATH
export PYTHONPATH=/home/ubuntu/vote-secret/backend
echo "Testing import..."
python -c "from server import app; print(\"Import OK\")"
echo "Testing gunicorn..."
gunicorn --bind 127.0.0.1:8001 --timeout 30 server:app --preload --workers 1
'
```

### Logs détaillés :
```bash
# Logs SystemD complets
sudo journalctl -u vote-secret --no-pager -l

# Logs en temps réel
sudo journalctl -u vote-secret -f

# Debug SystemD
sudo systemd-analyze verify vote-secret.service
```

## 📞 Support

Si le problème persiste, envoyez-moi :

1. **Résultat du diagnostic** :
   ```bash
   sudo bash /app/diagnostic-vps.sh > diagnostic.txt 2>&1
   ```

2. **Logs complets** :
   ```bash
   sudo journalctl -u vote-secret --no-pager -l > logs.txt
   ```

3. **Structure des fichiers** :
   ```bash
   find /home/ubuntu/vote-secret -type f -name "*.py" -o -name "gunicorn*" -o -name "*.txt" | head -20
   ```