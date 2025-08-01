# 🔧 CORRECTION URGENTE - DOUBLE PRÉFIXE /api/api/

## ❌ Problème identifié :
```
"POST /api/api/meetings HTTP/1.1" 404 Not Found
```

## ✅ Cause :
L'URL backend est configurée avec `/api` à la fin, mais le frontend ajoute automatiquement `/api` devant chaque route.

**Frontend (App.js ligne 15) :**
```javascript
const API = `${BACKEND_URL}/api`;  // Ajoute /api automatiquement
```

## 🚀 SOLUTION IMMÉDIATE

### Option 1 : Script automatique (RECOMMANDÉ)
```bash
# Exécuter le script de correction
sudo bash /app/fix-backend-url.sh
```

### Option 2 : Correction manuelle

#### 1. Trouver votre fichier .env frontend :
```bash
# Chercher le fichier
find /home/ubuntu/vote-secret -name ".env" -type f
# OU
find /var/www -name ".env" -type f
```

#### 2. Vérifier la configuration actuelle :
```bash
# Voir la configuration
cat /home/ubuntu/vote-secret/frontend/.env
# OU
cat /var/www/vote-secret/.env
```

#### 3. Corriger l'URL :

**❌ Configuration incorrecte :**
```env
REACT_APP_BACKEND_URL=http://votre-domaine.com/api
```

**✅ Configuration correcte :**
```env
REACT_APP_BACKEND_URL=http://votre-domaine.com
```

#### 4. Appliquer la correction :
```bash
# Sauvegarder
cp /home/ubuntu/vote-secret/frontend/.env /home/ubuntu/vote-secret/frontend/.env.backup

# Corriger (remplacez votre-domaine.com par votre vrai domaine)
echo "REACT_APP_BACKEND_URL=http://votre-domaine.com" > /home/ubuntu/vote-secret/frontend/.env
```

#### 5. Rebuilder le frontend :
```bash
cd /home/ubuntu/vote-secret/frontend
npm run build
```

#### 6. Déployer vers le serveur web :
```bash
# Si vous utilisez /var/www/
sudo cp -r build/* /var/www/vote-secret/
sudo chown -R www-data:www-data /var/www/vote-secret/
```

#### 7. Redémarrer les services :
```bash
sudo systemctl restart nginx
sudo systemctl restart vote-secret
```

## 🧪 TEST DE VALIDATION

### 1. Vérifier l'URL backend :
```bash
# Doit répondre avec 200 OK
curl -I http://votre-domaine.com/api/health
```

### 2. Vérifier le frontend :
```bash
# Ouvrir la console développeur du navigateur
# Vérifier que les requêtes vont vers /api/meetings (et non /api/api/meetings)
```

### 3. Test de création de réunion :
- Ouvrir l'interface web
- Essayer de créer une réunion
- Vérifier dans la console réseau qu'il n'y a plus d'erreur 404

## 📋 CONFIGURATIONS TYPES

### Configuration locale (test direct) :
```env
REACT_APP_BACKEND_URL=http://127.0.0.1:8001
```
**Résultat :** Requêtes vers `http://127.0.0.1:8001/api/meetings` ✅

### Configuration avec domaine :
```env
REACT_APP_BACKEND_URL=https://vote.votre-domaine.com
```
**Résultat :** Requêtes vers `https://vote.votre-domaine.com/api/meetings` ✅

### Configuration avec sous-chemin :
```env
REACT_APP_BACKEND_URL=https://votre-domaine.com
```
**Résultat :** Requêtes vers `https://votre-domaine.com/api/meetings` ✅

## ⚠️ ATTENTION

**NE JAMAIS mettre `/api` à la fin de `REACT_APP_BACKEND_URL` !**

Le frontend l'ajoute automatiquement dans `App.js` :
```javascript
const API = `${BACKEND_URL}/api`;  // /api ajouté ici
```

## 🎯 RÉSUMÉ DE LA CORRECTION

1. ✅ **Supprimer `/api`** de `REACT_APP_BACKEND_URL`
2. ✅ **Rebuilder** le frontend
3. ✅ **Redéployer** vers le serveur web
4. ✅ **Redémarrer** Nginx et le backend
5. ✅ **Tester** la création d'une réunion

Cette correction devrait résoudre immédiatement l'erreur 404 !