# 🚀 Guide d'Installation VPS - SUPER Vote Secret

## Prérequis

✅ **VPS Requirements:**
- Ubuntu 20.04+ ou Debian 11+
- 2 GB RAM minimum (4 GB recommandé)
- 20 GB espace disque
- Connexion Internet

✅ **Domaine Requirements:**
- Nom de domaine (ex: vote.example.com)
- DNS configuré vers l'IP de votre VPS

## Installation en 3 Commandes

### 1. Cloner le Repository
```bash
git clone https://github.com/votre-username/super-vote-secret.git
cd super-vote-secret
```

### 2. Lancer le Script d'Installation
```bash
sudo ./deploy-vps.sh
```

### 3. Suivre les Instructions
Le script vous demandera :
- **Votre domaine** (ex: vote.example.com)
- **Votre email** (pour les certificats SSL)
- **Confirmation des étapes**

## Ce que fait le Script Automatiquement

### 🔧 Installation des Dépendances
- ✅ Docker Engine (dernière version)
- ✅ Docker Compose V2
- ✅ Certificats SSL (Let's Encrypt)
- ✅ Configuration firewall

### 🛠️ Configuration de l'Application
- ✅ Variables d'environnement sécurisées
- ✅ Base de données MongoDB
- ✅ Proxy Nginx avec SSL
- ✅ Services en arrière-plan

### 🔒 Sécurisation
- ✅ Mots de passe forts générés
- ✅ Chiffrement SSL/TLS
- ✅ Headers de sécurité
- ✅ Rate limiting

## Après l'Installation

### ✅ Vérifications
```bash
# Vérifier les services
docker compose ps

# Voir les logs
docker compose logs -f

# Tester l'application
curl https://votre-domaine.com/health
```

### 🎯 Accès à l'Application
Votre application sera disponible sur :
**https://votre-domaine.com**

## Gestion de l'Application

### Commandes Utiles
```bash
# Redémarrer l'application
docker compose restart

# Arrêter l'application  
docker compose down

# Mettre à jour
git pull && docker compose up -d --build

# Sauvegarder la base de données
docker exec vote-secret-mongodb mongodump --out /backup

# Voir l'utilisation des ressources
docker stats
```

### Logs et Débogage
```bash
# Logs de tous les services
docker compose logs -f

# Logs d'un service spécifique
docker compose logs -f nginx
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f certbot

# Logs système
journalctl -u docker -f
```

## Résolution de Problèmes

### 🔥 Problème : SSL ne fonctionne pas
```bash
# Vérifier que le domaine pointe vers le serveur
dig +short votre-domaine.com

# Relancer la génération SSL
docker compose restart certbot
docker compose logs certbot
```

### 🔥 Problème : Application inaccessible
```bash
# Vérifier les ports
sudo netstat -tulpn | grep -E ':80|:443'

# Vérifier le firewall
sudo ufw status

# Ouvrir les ports si nécessaire
sudo ufw allow 80
sudo ufw allow 443
```

### 🔥 Problème : Services ne démarrent pas
```bash
# Vérifier l'espace disque
df -h

# Vérifier la mémoire
free -h

# Nettoyer Docker
docker system prune -a
```

## Mise à Jour de l'Application

```bash
# 1. Sauvegarder les données
docker exec vote-secret-mongodb mongodump --out /backup/$(date +%Y%m%d)

# 2. Mettre à jour le code
git pull

# 3. Reconstruire et redémarrer
docker compose up -d --build

# 4. Vérifier que tout fonctionne
docker compose ps
```

## Support

### 📧 Logs Importants
En cas de problème, partagez ces logs :
```bash
# Logs d'installation
cat /var/log/vote-secret-install.log

# Status des services
docker compose ps

# Logs des services
docker compose logs --tail=50 nginx backend frontend
```

### 🆘 Réinstallation Complète
Si tout va mal :
```bash
# Arrêter et nettoyer
docker compose down -v
docker system prune -a

# Relancer l'installation
sudo ./deploy-vps.sh
```

---

**🎉 Votre SUPER Vote Secret est prêt !**

Une fois l'installation terminée, votre plateforme de vote sera accessible sur **https://votre-domaine.com** avec tous les certificats SSL configurés automatiquement.