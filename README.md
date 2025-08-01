# Vote Secret v2.0 🗳️

**Système de vote anonyme moderne pour assemblées avec fonctionnalités avancées**

## 🚀 Fonctionnalités

### ✨ Fonctionnalités Principales
- **Vote anonyme sécurisé** avec suppression automatique des données
- **Interface moderne** avec design glassmorphique et responsive
- **Système de scrutateurs** avec approbation majoritaire pour les rapports
- **Rapports PDF** complets avec protection de fermeture
- **Temps réel** via WebSockets pour toutes les interactions

### 🔐 Fonctionnalités Avancées v2.0
- **🔄 Récupération de réunions** : URLs sécurisées pour revenir à sa réunion
- **🛡️ Protection de fermeture** : Impossible de fermer sans télécharger le rapport
- **👥 Gestion d'absence organisateur** : Transfert automatique aux scrutateurs
- **⚡ Système de heartbeat** : Détection de présence en temps réel
- **🗂️ Rapports partiels** : Disponibles en cas d'absence organisateur
- **⏰ Suppression intelligente** : Auto-nettoyage après 12h ou déconnexion

## 🏗️ Architecture

- **Frontend:** React 19 + Tailwind CSS + Shadcn/UI
- **Backend:** FastAPI (Python) + WebSockets
- **Base de données:** MongoDB avec Motor (async)
- **PDF:** ReportLab pour génération de rapports
- **Sécurité:** JWT, UUID, chiffrement des données

## ⚡ Installation Rapide

### 1. Configuration automatique
```bash
python3 setup_environment.py
```
Le script interactif configure automatiquement :
- Variables d'environnement (.env)
- URLs et base de données
- Clés de sécurité
- Guide d'installation personnalisé

### 2. Installation des dépendances
```bash
npm run install:all
```

### 3. Démarrage
```bash
# Développement
npm run dev

# Production
npm run build
npm run start
```

## 🎯 Utilisation

### Pour les Organisateurs
1. **Créer une réunion** avec titre et nom organisateur
2. **Générer une URL de récupération** (optionnel, pour sécurité)
3. **Ajouter des scrutateurs** avec codes sécurisés (optionnel)
4. **Créer des sondages** avec options multiples
5. **Gérer les participants** (approbation/rejet)
6. **Lancer les votes** et voir résultats en temps réel
7. **Générer le rapport PDF** (avec approbation scrutateurs si configuré)

### Pour les Participants
1. **Rejoindre** avec nom et code de réunion
2. **Attendre l'approbation** de l'organisateur
3. **Voter anonymement** sur les sondages actifs
4. **Voir les résultats** après fermeture des sondages

### Pour les Scrutateurs
1. **Rejoindre** avec nom et code scrutateur (SCxxxxxx)
2. **Être approuvé** par l'organisateur
3. **Accéder à l'interface organisateur** en lecture
4. **Voter pour l'approbation** des rapports PDF
5. **Prendre le leadership** si organisateur absent

## 📁 Structure du Projet

```
vote-secret/
├── setup_environment.py      # 🔧 Configuration interactive
├── package.json              # Scripts npm principaux
├── INSTALLATION.md           # Guide détaillé (auto-généré)
├── backend/
│   ├── server.py            # API FastAPI + WebSockets
│   ├── requirements.txt     # Dépendances Python optimisées
│   └── .env                 # Config backend (auto-généré)
├── frontend/
│   ├── src/
│   │   ├── App.js          # Application React principale
│   │   ├── App.css         # Styles avec glassmorphisme
│   │   └── components/ui/   # Composants Shadcn/UI
│   ├── package.json        # Dépendances React optimisées
│   └── .env                # Config frontend (auto-généré)
└── tests/                  # Tests automatisés
```

## 🛠️ Scripts Disponibles

### Développement
```bash
npm run dev                 # Démarrage complet (frontend + backend)
npm run dev:backend         # Backend seul (port 8001)
npm run dev:frontend        # Frontend seul (port 3000)
```

### Production
```bash
npm run build              # Build optimisé
npm run start              # Démarrage production
```

### Maintenance
```bash
npm run test               # Tests automatisés
npm run lint               # Vérification code
npm run format             # Formatage automatique
npm run clean              # Nettoyage caches
```

## 🔒 Sécurité et Confidentialité

### Anonymat Garanti
- **Dissociation cryptographique** : Impossible de lier vote et votant
- **UUID anonymes** : Aucune traçabilité des votes
- **Suppression automatique** : Données effacées après rapport PDF

### Protection des Données
- **Chiffrement** en transit et au repos
- **Clés secrètes** générées automatiquement
- **Expiration** des sessions de récupération
- **Audit trail** pour actions critiques

### Contrôles d'Intégrité
- **Validation serveur** de toutes les données
- **Protection CORS** contre attaques externes
- **Scrutateurs** pour validation indépendante
- **Immutabilité** des sondages après création

## 🚀 Déploiement

### Développement Local
```bash
# Configuration automatique
python3 setup_environment.py
# Choisir "Développement local"
```

### Production
```bash
# Configuration avec domaine personnalisé
python3 setup_environment.py
# Choisir "Production" et configurer HTTPS
```

### Variables d'Environnement Clés
- `MONGO_URL` : Connexion MongoDB
- `SECRET_KEY` : Clé de chiffrement principale
- `REACT_APP_BACKEND_URL` : URL backend pour React
- `ALLOWED_ORIGINS` : Origins CORS autorisées

## 📊 Cas d'Usage

### Parfait pour :
- ✅ **Assemblées générales** d'associations
- ✅ **Conseils d'administration** et comités
- ✅ **Élections** de représentants
- ✅ **Consultations internes** d'entreprise
- ✅ **Réunions syndicales** et professionnelles
- ✅ **Votes sensibles** nécessitant l'anonymat
- ✅ **Assemblées citoyennes** participatives

### Garanties Techniques
- 🔐 **Anonymat cryptographique inviolable**
- ⚡ **Temps réel** avec WebSockets
- 📱 **Responsive** sur tous appareils
- 🛡️ **Sécurité** de niveau entreprise
- 📈 **Scalabilité** testée (450+ participants)
- 🔄 **Récupération** en cas de problème

## 🆘 Support

Pour utiliser Vote Secret :

1. **Configuration** : Lancez `python3 setup_environment.py`
2. **Installation** : Suivez le guide généré `INSTALLATION.md`
3. **Démarrage** : Utilisez `npm run dev` pour tester
4. **Documentation** : Consultez les commentaires dans le code

## 📝 Licence

MIT License - Libre d'utilisation pour tous projets.

---

**Vote Secret v2.0** - *Votre vote, votre secret* 🤐
