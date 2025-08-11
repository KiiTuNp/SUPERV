# SUPER Vote Secret 🗳️

Une plateforme de vote anonyme moderne et sécurisée pour assemblées, avec gestion automatique des fuseaux horaires et suppression cryptographique des données.

## 🌟 Fonctionnalités Principales

### 🕒 **Nouveau : Gestion Automatique des Fuseaux Horaires**
- **Détection automatique** du fuseau horaire de l'organisateur
- **Affichage uniforme** : tous les participants voient l'heure de l'organisateur
- **Rapports PDF** générés avec les bonnes heures
- **Compatibilité ascendante** avec les réunions existantes

### 🔐 **Sécurité et Anonymat**
- Vote anonyme avec UUIDs
- Pas de traçabilité des votes individuels
- Suppression cryptographique définitive des données après génération du rapport
- Protection contre la fermeture prématurée des réunions

### 👥 **Gestion des Participants**
- **Organisateur** : Créé et contrôle la réunion
- **Scrutateurs** : Accès automatique sans approbation manuelle
- **Participants** : Rejoignent avec approbation de l'organisateur
- Codes séparés pour participants et scrutateurs

### 📊 **Système de Vote Avancé**
- Création de sondages avec options multiples
- Minuteur optionnel pour chaque sondage
- Résultats en temps réel pour l'organisateur
- Masquage des résultats partiels pour les participants

### 📄 **Génération de Rapports**
- **Génération directe** par l'organisateur (plus d'approbation des scrutateurs)
- Rapport PDF complet avec timestamps dans le fuseau horaire correct
- Suppression automatique des données après téléchargement
- Export sécurisé avec nom de fichier automatique

## 🚀 Installation Rapide

### Prérequis
- Docker et Docker Compose
- Ports 3000 (frontend) et 8001 (backend) disponibles
- Certificats SSL (pour la production)

### Installation Automatique

```bash
# Cloner le projet
git clone <repository-url>
cd vote-secret

# Installation interactive avec choix du mode
make install

# Ou installation directe en production
make prod
```

### Installation Manuelle

```bash
# 1. Configuration des variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# 2. Démarrage des services
docker-compose up -d

# 3. Vérification
make status
```

## 🎯 Utilisation

### Créer une Réunion
1. Accéder à l'interface organisateur
2. Cliquer sur **"Créer une nouvelle réunion"**
3. Remplir le titre et votre nom (le fuseau horaire est détecté automatiquement)
4. Partager le **code de réunion** avec les participants

### Ajouter des Scrutateurs
1. Dans l'interface organisateur, cliquer sur **"Ajouter des scrutateurs"**
2. Entrer les noms des scrutateurs autorisés
3. Partager le **code de scrutateur** généré
4. Les scrutateurs ont un accès immédiat sans approbation

### Créer et Gérer les Sondages
1. Cliquer sur **"Créer un sondage"**
2. Entrer la question et les options (2 minimum, 20 maximum)
3. Optionnel : Définir un minuteur
4. Lancer le sondage quand prêt
5. Fermer le sondage pour révéler les résultats

### Générer le Rapport Final
1. S'assurer que tous les sondages sont fermés
2. Cliquer sur **"Voir le résumé du rapport"**
3. Vérifier les informations affichées
4. Télécharger le rapport PDF
5. ⚠️ **Les données sont supprimées définitivement après téléchargement**

## 🔧 Configuration Avancée

### Variables d'Environnement

```bash
# Base de données
MONGO_URL=mongodb://localhost:27017
DB_NAME=vote_secret

# URLs de service
REACT_APP_BACKEND_URL=http://localhost:8001

# Sécurité (Production)
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

### Commandes Make Disponibles

```bash
make install    # Installation interactive
make dev        # Mode développement
make prod       # Mode production
make status     # Vérifier les services
make logs       # Voir les logs
make clean      # Nettoyer les conteneurs
make backup     # Sauvegarder les données
```

## 🌍 Support des Fuseaux Horaires

L'application détecte automatiquement le fuseau horaire de l'organisateur et affiche toutes les heures de manière cohérente :

- **Détection automatique** via `Intl.DateTimeFormat().resolvedOptions().timeZone`
- **Affichage uniforme** pour tous les participants
- **Rapports PDF** avec les bonnes heures locales
- **Fallback** vers l'heure du serveur si nécessaire

### Fuseaux Horaires Testés
- ✅ Europe/Paris
- ✅ America/New_York
- ✅ Compatibilité sans timezone

## 🏗️ Architecture Technique

### Stack Technologique
- **Frontend** : React 18 + Tailwind CSS + Shadcn/UI
- **Backend** : FastAPI + Python 3.11
- **Base de données** : MongoDB
- **Temps réel** : WebSockets
- **Containerisation** : Docker + Docker Compose
- **Proxy** : Nginx avec SSL automatique

### Structure du Projet

```
vote-secret/
├── frontend/          # Application React
├── backend/           # API FastAPI
├── nginx/             # Configuration proxy
├── docker-compose.yml # Orchestration services
├── Makefile          # Commandes d'automatisation
└── README.md         # Cette documentation
```

### Sécurité

- **Anonymat** : Utilisation d'UUIDs, pas d'ID participants
- **Chiffrement** : HTTPS obligatoire en production
- **Suppression** : Données supprimées après export PDF
- **Validation** : Contrôles d'entrée stricts
- **Isolation** : Services containerisés

## 📱 Interface Utilisateur

### Interface Organisateur
- Tableau de bord complet
- Gestion des participants et scrutateurs
- Création et contrôle des sondages
- Génération des rapports
- Récupération d'accès avec URL sécurisée

### Interface Participant
- Participation anonyme
- Vote simple et intuitif
- Résultats en temps réel après fermeture
- Protection contre les votes multiples

### Interface Scrutateur
- Accès automatique aux fonctionnalités organisateur
- Supervision des votes
- Pas de génération de rapport (réservée à l'organisateur)

## 🔍 Monitoring et Logs

### Vérifier les Services

```bash
# Status général
make status

# Logs en temps réel
make logs

# Logs spécifiques
docker-compose logs frontend
docker-compose logs backend
```

### Résolution de Problèmes

**Service ne démarre pas :**
```bash
# Vérifier les ports
netstat -tlnp | grep -E ":(3000|8001|27017)"

# Redémarrer les services
make restart
```

**Problème de base de données :**
```bash
# Vérifier MongoDB
docker-compose exec mongodb mongosh --eval "db.stats()"

# Réinitialiser la DB
make clean && make prod
```

## 🚀 Déploiement Production

### Prérequis Production
- Serveur avec Docker
- Certificats SSL valides
- Nom de domaine configuré
- Ports 80 et 443 ouverts

### Script de Déploiement Automatique

```bash
# Utiliser le script de déploiement interactif
./deploy-optimized.sh

# Ou directement
make prod
```

### Configuration SSL Automatique

Le système gère automatiquement :
- Configuration Nginx
- Certificats Let's Encrypt
- Renouvellement automatique
- Redirection HTTPS

## 🧪 Tests

### Tests Backend
```bash
# Tests complets de l'API
cd backend && python -m pytest

# Tests de charge
make load-test
```

### Tests de Compatibilité
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile (responsive)

## 📈 Performances

### Optimisations Intégrées
- Compression Gzip
- Cache navigateur
- Images optimisées
- Code minifié
- Lazy loading

### Capacité Recommandée
- **Participants** : Jusqu'à 500 simultanés
- **Sondages** : Jusqu'à 50 par réunion
- **Options** : Jusqu'à 20 par sondage
- **Stockage** : Nettoyage automatique

## 🤝 Contribution

### Développement Local

```bash
# Mode développement
make dev

# Installation des dépendances
cd frontend && yarn install
cd backend && pip install -r requirements.txt

# Tests en développement
make test
```

### Standards de Code
- **Frontend** : ESLint + Prettier
- **Backend** : Black + Flake8
- **Git** : Conventional Commits
- **Documentation** : Mise à jour du README obligatoire

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

### Issues Communes

**ESLint erreurs** : Configuration automatique, ignorer les warnings temporaires
**WebSocket timeout** : Limitations infrastructure, fonctionnalité dégradée acceptable
**Timezone incorrect** : Vérifier la détection automatique du navigateur

### Contact

Pour tout problème ou suggestion :
- 📧 Créer une issue GitHub
- 📖 Consulter la documentation technique
- 🔧 Utiliser les commandes de diagnostic

## 🎉 Fonctionnalités à Venir

- [ ] API export des données
- [ ] Interface d'administration avancée
- [ ] Support multi-langues
- [ ] Intégration calendrier
- [ ] Notifications email
- [ ] Mode sombre

---

**SUPER Vote Secret v2.0** - Plateforme de vote anonyme avec support des fuseaux horaires 🌍

*Développé avec ❤️ pour la transparence démocratique*