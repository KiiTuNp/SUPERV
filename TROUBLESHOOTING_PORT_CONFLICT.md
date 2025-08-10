# Guide de Résolution - Conflit de Port 80

## Problème Identifié
```
Error response from daemon: failed to bind host port for 0.0.0.0:80:172.18.0.5:80/tcp: address already in use
```

## Causes Communes

1. **Serveur web existant** (nginx, apache) en cours d'exécution
2. **Anciens containers Docker** utilisant les ports 80/443
3. **Services système** bindés sur ces ports

## Solutions Rapides

### 1. Diagnostic Automatique
```bash
./diagnose-port-conflict.sh
```

### 2. Correction Automatique
```bash
./fix-port-conflict.sh
```

### 3. Déploiement avec Ports Alternatifs
```bash
./deploy-with-alternative-ports.sh
```

### 4. Guide Complet de Dépannage
```bash
./troubleshoot-deployment.sh
```

## Solutions Manuelles

### Arrêter Services Conflictuels
```bash
# Arrêt nginx système
sudo systemctl stop nginx
sudo systemctl disable nginx

# Arrêt apache système  
sudo systemctl stop apache2
sudo systemctl disable apache2
```

### Nettoyer Containers Docker
```bash
# Arrêter containers vote-secret
docker ps -a | grep vote-secret | awk '{print $1}' | xargs docker stop
docker ps -a | grep vote-secret | awk '{print $1}' | xargs docker rm

# Nettoyer système Docker
docker system prune -af
```

### Vérifier Ports Libres
```bash
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

## Options de Déploiement

### Option A : Ports Standards (80/443)
```bash
# Après résolution du conflit
docker-compose up -d
```

### Option B : Ports Alternatifs (8080/8443)
```bash
# Utilise docker-compose.override.yml
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

## Vérification Post-Déploiement

```bash
# Statut des containers
docker-compose ps

# Logs des services
docker-compose logs nginx
docker-compose logs backend

# Test de connectivité
curl -I http://localhost:80      # ou :8080
curl -I https://localhost:443    # ou :8443
```

## Commandes d'Urgence

```bash
# Arrêt d'urgence
docker-compose down --remove-orphans

# Nettoyage complet
docker system prune -af && docker volume prune -f

# Redémarrage propre
docker-compose up -d --force-recreate
```