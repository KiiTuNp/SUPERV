# CORRECTION SERVICE SYSTEMD VOTE SECRET

## Problèmes identifiés dans votre configuration :

### ❌ Configuration actuelle (défaillante) :
```ini
[Service]
ExecStart=/opt/vote-secret/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

### ✅ Configuration corrigée :
```ini
[Service]
Type=exec
ExecStart=/opt/vote-secret/venv/bin/gunicorn --config /opt/vote-secret/config/gunicorn.conf.py server:app
```

## Corrections apportées :

1. **Port correct** : `127.0.0.1:8001` (pas 8000)
2. **Module correct** : `server:app` (pas app:app)  
3. **Configuration Gunicorn** : Utilise le fichier de config complet
4. **Type de service** : `Type=exec` ajouté
5. **Permissions de logs** : Ajout de `/var/log/vote-secret` aux ReadWritePaths
6. **Variables d'environnement** : PATH et PYTHONPATH correctement configurés

## Instructions de réparation :

### Option 1 : Script automatique (recommandé)
```bash
# Exécuter le script de réparation
sudo /app/fix-systemd.sh
```

### Option 2 : Réparation manuelle

1. **Arrêter le service défaillant :**
```bash
sudo systemctl stop vote-secret
sudo systemctl disable vote-secret
```

2. **Remplacer le fichier service :**
```bash
sudo cp /app/vote-secret-systemd-fixed.service /etc/systemd/system/vote-secret.service
```

3. **Recharger et redémarrer :**
```bash
sudo systemctl daemon-reload
sudo systemctl enable vote-secret
sudo systemctl start vote-secret
```

4. **Vérifier le statut :**
```bash
sudo systemctl status vote-secret
```

5. **Tester la connectivité :**
```bash
curl http://127.0.0.1:8001/api/health
```

## Diagnostic en cas de problème :

### Exécuter le diagnostic complet :
```bash 
sudo /app/diagnose-systemd.sh
```

### Vérifications manuelles :

1. **Logs du service :**
```bash
sudo journalctl -u vote-secret -f
```

2. **Test de l'application :**
```bash
cd /opt/vote-secret/backend
sudo -u vote-secret /opt/vote-secret/venv/bin/python -c "from server import app; print('OK')"
```

3. **Test de Gunicorn :**
```bash
sudo -u vote-secret /opt/vote-secret/venv/bin/gunicorn --config /opt/vote-secret/config/gunicorn.conf.py --check-config server:app
```

4. **Vérifier les permissions :**
```bash
ls -la /opt/vote-secret/
ls -la /var/log/vote-secret/
```

## Fichiers importants :

- **Service SystemD** : `/etc/systemd/system/vote-secret.service`
- **Config Gunicorn** : `/opt/vote-secret/config/gunicorn.conf.py`  
- **Application** : `/opt/vote-secret/backend/server.py`
- **Variables d'env** : `/opt/vote-secret/backend/.env`
- **Logs** : `/var/log/vote-secret/` et `journalctl -u vote-secret`

## Points critiques :

1. ✅ **Port 8001** (pas 8000) - Nginx est configuré pour proxifier vers 8001
2. ✅ **Module server:app** - Le fichier s'appelle server.py
3. ✅ **Config Gunicorn** - Utilise les bonnes options (workers, timeout, etc.)
4. ✅ **Permissions** - L'utilisateur vote-secret doit être propriétaire
5. ✅ **Logs** - Répertoire /var/log/vote-secret doit exister avec bonnes permissions