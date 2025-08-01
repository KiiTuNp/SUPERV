# 🚀 Vote Secret v2.0 - Guide de Déploiement Production

## Vue d'ensemble

Ce guide vous accompagne dans le déploiement automatisé de Vote Secret v2.0 sur un serveur de production Linux. Le système utilise des scripts Python interactifs pour une installation complète et sécurisée.

## 📋 Prérequis Serveur

### Système d'exploitation supporté
- **Ubuntu 20.04+ / Debian 11+** (recommandé)
- **CentOS 8+ / RHEL 8+ / Rocky Linux / AlmaLinux**
- **Fedora 35+**

### Spécifications minimales
- **CPU**: 2 cœurs
- **RAM**: 4 GB
- **Disque**: 20 GB libres
- **Réseau**: Connexion Internet stable

### Accès requis
- **Utilisateur avec droits sudo** (pas root direct)
- **Ports ouverts**: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- **Domaine configuré** pointant vers le serveur (pour production)

## 🎯 Déploiement Automatisé Complet

### Option 1: Déploiement Maître (Recommandé)

Le script maître orchestre automatiquement toutes les étapes :

```bash
# Télécharger Vote Secret v2.0
git clone <repository-url>
cd vote-secret

# Lancer le déploiement complet
python3 deploy_master.py
```

**Le script maître exécute automatiquement :**
1. Installation des prérequis système
2. Configuration de l'environnement
3. Installation et configuration Nginx + SSL
4. Déploiement final et services systemd

**Durée estimée :** 30-60 minutes selon la connexion

### Option 2: Déploiement Étape par Étape

Pour plus de contrôle, exécutez chaque script individuellement :

```bash
# Étape 1: Prérequis système
python3 deploy.py

# Étape 2: Configuration environnement
python3 deploy_environment.py

# Étape 3: Serveur web et SSL
python3 deploy_nginx.py

# Étape 4: Déploiement final
python3 deploy_final.py
```

## 📊 Scripts de Déploiement

### 1. `deploy.py` - Prérequis Système
**Fonctionnalités :**
- Vérification compatibilité système
- Installation Python 3.11+, Node.js 20+, MongoDB 8.0+
- Configuration des outils de base
- Validation des prérequis

**Distributions supportées :**
- Ubuntu/Debian → apt
- CentOS/RHEL/Rocky/Alma → yum/dnf
- Fedora → dnf

### 2. `deploy_environment.py` - Configuration
**Fonctionnalités :**
- Configuration interactive complète
- Génération automatique des clés de sécurité
- Support multi-environnement (dev/staging/prod)
- Configuration SSL (Let's Encrypt/Certificats/Auto-signé)
- Paramètres performance et monitoring
- Génération fichiers .env et documentation

**Configurations supportées :**
- **Base de données :** MongoDB local/Atlas/distant
- **SSL :** Let's Encrypt automatique, certificats existants, auto-signé
- **Performance :** Workers, cache Redis, logs
- **Sécurité :** Rate limiting, CORS, authentification

### 3. `deploy_nginx.py` - Serveur Web
**Fonctionnalités :**
- Installation et configuration Nginx optimisée
- Configuration SSL automatique avec Let's Encrypt
- Support certificats existants
- Durcissement sécurité (headers, rate limiting)
- Configuration firewall (UFW)
- Tests de connectivité

**Optimisations incluses :**
- Compression gzip
- Cache des assets statiques
- Headers de sécurité
- Protection contre DDoS basique
- Support WebSocket pour temps réel

### 4. `deploy_final.py` - Mise en Production
**Fonctionnalités :**
- Création utilisateur système vote-secret
- Déploiement application dans /opt/vote-secret
- Installation dépendances et build frontend
- Configuration services systemd
- Scripts de gestion (/usr/local/bin/)
- Tests de validation complets

**Services créés :**
- **vote-secret.service** → Backend avec Gunicorn
- **Scripts de gestion** → manage.sh, backup.sh, monitor.sh
- **Rotation des logs** → logrotate automatique

## 🔧 Configuration Interactive

### Informations Requises

Préparez les informations suivantes avant le déploiement :

#### Serveur
- **Nom du serveur** (pour identification)
- **Domaine principal** (ex: vote.entreprise.com)
- **Email administrateur** (pour SSL et alertes)

#### Base de Données
- **Type :** Local sécurisé / MongoDB Atlas / Serveur distant
- **Authentification :** Utilisateur/mot de passe MongoDB
- **Nom de la base** (défaut: vote_secret_prod)

#### SSL/Sécurité
- **Certificats SSL :** Let's Encrypt auto / Existants / Auto-signés
- **Limites :** Participants max, sondages max, requêtes/minute
- **Monitoring :** Activation, port métriques, alertes email

### Exemple de Configuration Typique

```
🌐 Serveur
Nom: vote-prod-01
Domaine: vote.monentreprise.com
SSL: Let's Encrypt automatique
Email: admin@monentreprise.com

🗄️ Base de Données  
Type: MongoDB local sécurisé
Utilisateur: vote_secret_user
Base: vote_secret_prod

⚡ Performance
Workers: 4
Cache Redis: Activé
Logs: INFO level

🔒 Sécurité
Max participants: 500
Rate limiting: 100 req/min
Monitoring: Activé sur port 9090
```

## 📁 Structure Post-Déploiement

```
/opt/vote-secret/              # Application principale
├── backend/                   # API FastAPI
├── frontend/                  # Interface React (build)
├── config/                    # Configurations
├── scripts/                   # Scripts de gestion
├── venv/                      # Environnement Python
├── .env                       # Configuration globale
└── logs/                      # Logs applicatifs

/etc/systemd/system/
└── vote-secret.service        # Service systemd

/etc/nginx/sites-available/
└── vote-secret                # Configuration Nginx

/usr/local/bin/
├── manage.sh                  # Gestion application
├── backup.sh                  # Sauvegarde automatique
└── monitor.sh                 # Monitoring système

/var/log/vote-secret/          # Logs de production
├── access.log                 # Logs d'accès
├── error.log                  # Logs d'erreurs
└── application.log            # Logs applicatifs
```

## 🛠️ Gestion Post-Déploiement

### Commandes de Gestion

```bash
# Gestion du service
sudo systemctl start/stop/restart vote-secret
sudo systemctl status vote-secret

# Scripts de gestion simplifiés
/usr/local/bin/manage.sh start      # Démarrer
/usr/local/bin/manage.sh stop       # Arrêter  
/usr/local/bin/manage.sh restart    # Redémarrer
/usr/local/bin/manage.sh status     # Statut
/usr/local/bin/manage.sh logs       # Logs temps réel
/usr/local/bin/manage.sh update     # Mise à jour

# Monitoring et maintenance
/usr/local/bin/monitor.sh           # État complet du système
/usr/local/bin/backup.sh            # Sauvegarde manuelle
```

### Surveillance des Logs

```bash
# Logs applicatifs
tail -f /var/log/vote-secret/error.log
tail -f /var/log/vote-secret/access.log

# Logs système
journalctl -u vote-secret -f
journalctl -u nginx -f

# Monitoring complet
/usr/local/bin/monitor.sh
```

## 🔒 Sécurité et Maintenance

### Sécurité Intégrée

✅ **Chiffrement complet** avec SSL/TLS moderne
✅ **Isolation utilisateur** avec compte système dédié  
✅ **Durcissement Nginx** avec headers de sécurité
✅ **Rate limiting** contre les attaques DDoS
✅ **Firewall configuré** (UFW) avec ports essentiels
✅ **Clés secrètes** générées cryptographiquement
✅ **Permissions strictes** sur fichiers sensibles

### Maintenance Automatique

✅ **Rotation des logs** avec logrotate
✅ **Renouvellement SSL** automatique (Let's Encrypt)
✅ **Monitoring système** intégré
✅ **Scripts de sauvegarde** configurables
✅ **Health checks** automatiques

### Sauvegarde Automatique

```bash
# Configuration crontab pour sauvegarde quotidienne
sudo crontab -e

# Ajouter cette ligne pour sauvegarde à 2h00
0 2 * * * /usr/local/bin/backup.sh >> /var/log/vote-secret-backup.log 2>&1
```

## 🔍 Dépannage

### Problèmes Courants

#### Service ne démarre pas
```bash
# Vérifier les logs
journalctl -u vote-secret --no-pager -n 50

# Vérifier la configuration
sudo nginx -t
python3 -c "import sys; print(sys.version)"
```

#### Problème SSL/Certificats
```bash
# Vérifier les certificats Let's Encrypt
sudo certbot certificates

# Renouveler manuellement
sudo certbot renew --dry-run
```

#### Performance dégradée
```bash
# Monitoring complet
/usr/local/bin/monitor.sh

# Vérifier les ressources
htop
iotop
```

### Logs de Diagnostic

| Composant | Localisation | Description |
|-----------|--------------|-------------|
| Application | `/var/log/vote-secret/` | Logs Vote Secret |
| Système | `journalctl -u vote-secret` | Logs systemd |
| Nginx | `/var/log/nginx/` | Logs serveur web |
| MongoDB | `journalctl -u mongod` | Logs base de données |

## 📞 Support et Ressources

### Documentation Générée
- **DEPLOYMENT_GUIDE.md** → Guide personnalisé post-configuration
- **PROJECT_STATUS.md** → État détaillé du projet
- **README.md** → Documentation utilisateur

### Commandes Utiles
```bash
# État complet du déploiement
/usr/local/bin/monitor.sh

# Test de connectivité
curl -I https://votre-domaine.com
curl -I https://votre-domaine.com/api/health

# Vérification des services
systemctl status vote-secret nginx mongod
```

### En Cas de Problème
1. **Consultez** `/usr/local/bin/monitor.sh` pour un diagnostic
2. **Vérifiez** les logs dans `/var/log/vote-secret/`
3. **Testez** la configuration avec `sudo nginx -t`
4. **Redémarrez** les services si nécessaire

---

## 🎉 Félicitations !

Une fois le déploiement terminé, **Vote Secret v2.0** sera opérationnel avec :

✅ **Interface moderne** accessible via votre domaine  
✅ **API sécurisée** avec authentification et chiffrement  
✅ **Base de données** optimisée et sauvegardée  
✅ **Monitoring** en temps réel  
✅ **SSL/TLS** configuré automatiquement  
✅ **Maintenance** automatisée  

**Vote Secret v2.0 est maintenant prêt pour un usage professionnel intensif !** 🚀