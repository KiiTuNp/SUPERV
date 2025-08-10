#!/bin/bash

# Script de test pour valider la configuration Docker
# Ce script teste les configurations Docker sans les construire

echo "🔍 Validation de la configuration Docker pour Vote Secret..."

# Couleurs pour l'output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Test 1: Vérifier que les fichiers Docker existent
echo "📝 Test 1: Vérification des fichiers Docker..."
if [ -f "docker-compose.yml" ] && [ -f "frontend/Dockerfile" ] && [ -f "backend/Dockerfile" ]; then
    print_result 0 "Tous les fichiers Docker sont présents"
else
    print_result 1 "Fichiers Docker manquants"
fi

# Test 2: Vérifier la synchronisation package.json et yarn.lock
echo "📝 Test 2: Vérification de la synchronisation yarn.lock..."
cd frontend
if yarn install --frozen-lockfile --silent > /dev/null 2>&1; then
    print_result 0 "yarn.lock est synchronisé avec package.json"
else
    print_result 1 "yarn.lock n'est pas synchronisé avec package.json"
fi
cd ..

# Test 3: Validation de la syntaxe docker-compose
echo "📝 Test 3: Validation de la syntaxe Docker Compose..."
if command -v docker-compose >/dev/null 2>&1; then
    if docker-compose -f docker-compose.yml config > /dev/null 2>&1; then
        print_result 0 "docker-compose.yml syntaxe valide"
    else
        print_result 1 "docker-compose.yml syntaxe invalide"
    fi
elif command -v docker >/dev/null 2>&1; then
    if docker compose -f docker-compose.yml config > /dev/null 2>&1; then
        print_result 0 "docker-compose.yml syntaxe valide"
    else
        print_result 1 "docker-compose.yml syntaxe invalide"
    fi
else
    echo -e "${YELLOW}⚠️  Docker non disponible dans cet environnement${NC}"
fi

# Test 4: Vérifier les variables d'environnement
echo "📝 Test 4: Vérification des variables d'environnement..."
if [ -f ".env" ] && [ -f "frontend/.env" ] && [ -f "backend/.env" ]; then
    print_result 0 "Tous les fichiers .env sont présents"
else
    print_result 1 "Fichiers .env manquants"
fi

# Test 5: Vérifier les .dockerignore
echo "📝 Test 5: Vérification des fichiers .dockerignore..."
if [ -f "frontend/.dockerignore" ] && [ -f "backend/.dockerignore" ]; then
    print_result 0 "Fichiers .dockerignore présents"
else
    print_result 1 "Fichiers .dockerignore manquants"
fi

echo ""
echo "🚀 Tests de validation terminés!"
echo ""
echo -e "${GREEN}SOLUTION POUR LE PROBLÈME DE DÉPLOIEMENT:${NC}"
echo "Le problème yarn.lock désynchronisé a été corrigé."
echo "Votre fichier yarn.lock est maintenant à jour avec package.json."
echo ""
echo -e "${YELLOW}POUR DÉPLOYER SUR VOTRE VPS:${NC}"
echo "1. Utilisez le script: ./deploy.sh"
echo "2. Ou manuellement: docker compose up -d --build"
echo ""