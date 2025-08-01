#!/usr/bin/env python3
"""
Vote Secret - Configuration d'Environnement Interactive
=======================================================

Script de configuration automatique pour déployer Vote Secret.
Génère les fichiers .env nécessaires pour le frontend, backend et la racine.

Auteur: Assistant AI
Version: 2.0.0
Date: 2025-08-01
"""

import os
import sys
import getpass
import secrets
import string
import re
from typing import Dict, Optional, Any
from pathlib import Path

class Colors:
    """Codes couleur pour l'affichage terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Affiche un en-tête stylisé"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

def print_success(text: str):
    """Affiche un message de succès"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Affiche un avertissement"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    """Affiche une erreur"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """Affiche une information"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.ENDC}")

def generate_secret_key(length: int = 32) -> str:
    """Génère une clé secrète sécurisée"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_url(url: str) -> bool:
    """Valide une URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def validate_email(email: str) -> bool:
    """Valide une adresse email"""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return email_pattern.match(email) is not None

def prompt_input(prompt: str, default: Optional[str] = None, required: bool = True, 
                 validator: Optional[callable] = None, secret: bool = False) -> str:
    """Demande une saisie utilisateur avec validation"""
    while True:
        if default:
            display_prompt = f"{Colors.BLUE}{prompt} [{default}]{Colors.ENDC}: "
        else:
            display_prompt = f"{Colors.BLUE}{prompt}{Colors.ENDC}: "
        
        if secret:
            value = getpass.getpass(display_prompt)
        else:
            value = input(display_prompt).strip()
        
        if not value and default:
            value = default
        
        if not value and required:
            print_error("Cette valeur est requise. Veuillez saisir une valeur.")
            continue
        
        if validator and value and not validator(value):
            print_error("Format invalide. Veuillez réessayer.")
            continue
        
        return value

def prompt_choice(prompt: str, choices: Dict[str, str], default: Optional[str] = None) -> str:
    """Demande un choix parmi plusieurs options"""
    print(f"\n{Colors.CYAN}{prompt}{Colors.ENDC}")
    for key, description in choices.items():
        marker = f" [{Colors.GREEN}défaut{Colors.ENDC}]" if key == default else ""
        print(f"  {Colors.BOLD}{key}{Colors.ENDC}: {description}{marker}")
    
    while True:
        choice = input(f"\n{Colors.BLUE}Votre choix{Colors.ENDC}: ").strip().lower()
        
        if not choice and default:
            return default
        
        if choice in choices:
            return choice
        
        print_error(f"Choix invalide. Options disponibles: {', '.join(choices.keys())}")

def prompt_yes_no(prompt: str, default: bool = True) -> bool:
    """Demande une confirmation oui/non"""
    default_text = "O/n" if default else "o/N"
    response = input(f"{Colors.BLUE}{prompt} [{default_text}]{Colors.ENDC}: ").strip().lower()
    
    if not response:
        return default
    
    return response in ['o', 'oui', 'y', 'yes', '1', 'true']

class EnvironmentSetup:
    """Classe principale pour la configuration d'environnement"""
    
    def __init__(self):
        self.config = {}
        self.project_root = Path(__file__).parent
        
    def welcome(self):
        """Affiche le message de bienvenue"""
        print_header("VOTE SECRET - CONFIGURATION D'ENVIRONNEMENT")
        print(f"{Colors.CYAN}Bienvenue dans l'assistant de configuration de Vote Secret !{Colors.ENDC}")
        print(f"{Colors.CYAN}Ce script va vous guider pour configurer votre environnement de déploiement.{Colors.ENDC}\n")
        
        print_info("Fonctionnalités de Vote Secret v2.0:")
        print("  • Vote anonyme sécurisé avec suppression automatique des données")
        print("  • Système de scrutateurs avec approbation majoritaire")
        print("  • Interface moderne avec récupération de réunions")
        print("  • Rapports PDF avec protection de fermeture")
        print("  • Gestion d'absence organisateur avec transfert de leadership")
        print("  • Architecture FastAPI + React + MongoDB\n")

    def collect_deployment_info(self):
        """Collecte les informations de déploiement"""
        print_header("CONFIGURATION DU DÉPLOIEMENT")
        
        # Type de déploiement
        deployment_types = {
            "dev": "Développement local (localhost)",
            "staging": "Environnement de test/staging",
            "prod": "Production (domaine personnalisé)"
        }
        
        self.config['DEPLOYMENT_TYPE'] = prompt_choice(
            "Type de déploiement", 
            deployment_types, 
            default="dev"
        )
        
        # Configuration des URLs selon le type de déploiement
        if self.config['DEPLOYMENT_TYPE'] == 'dev':
            self.config['FRONTEND_URL'] = 'http://localhost:3000'
            self.config['BACKEND_URL'] = 'http://localhost:8001'
            self.config['ALLOWED_ORIGINS'] = 'http://localhost:3000,http://127.0.0.1:3000'
        else:
            self.config['FRONTEND_URL'] = prompt_input(
                "URL du frontend (avec https://)", 
                required=True, 
                validator=validate_url
            )
            self.config['BACKEND_URL'] = prompt_input(
                "URL du backend (avec https://)", 
                required=True, 
                validator=validate_url
            )
            self.config['ALLOWED_ORIGINS'] = self.config['FRONTEND_URL']

    def collect_database_info(self):
        """Collecte les informations de base de données"""
        print_header("CONFIGURATION DE LA BASE DE DONNÉES")
        
        db_types = {
            "local": "MongoDB local (recommandé pour dev)",
            "atlas": "MongoDB Atlas (cloud)",
            "custom": "URL personnalisée"
        }
        
        db_type = prompt_choice("Type de base de données", db_types, default="local")
        
        if db_type == "local":
            self.config['MONGO_URL'] = 'mongodb://localhost:27017'
            self.config['DB_NAME'] = prompt_input("Nom de la base de données", default="vote_secret")
        elif db_type == "atlas":
            print_info("Pour MongoDB Atlas, récupérez votre chaîne de connexion depuis le dashboard Atlas")
            self.config['MONGO_URL'] = prompt_input(
                "URL de connexion MongoDB Atlas (mongodb+srv://...)", 
                required=True
            )
            self.config['DB_NAME'] = prompt_input("Nom de la base de données", default="vote_secret")
        else:
            self.config['MONGO_URL'] = prompt_input("URL MongoDB personnalisée", required=True)
            self.config['DB_NAME'] = prompt_input("Nom de la base de données", default="vote_secret")

    def collect_security_info(self):
        """Collecte les informations de sécurité"""
        print_header("CONFIGURATION DE SÉCURITÉ")
        
        # Génération automatique des clés secrètes
        if prompt_yes_no("Générer automatiquement les clés secrètes ?", default=True):
            self.config['SECRET_KEY'] = generate_secret_key(64)
            self.config['JWT_SECRET'] = generate_secret_key(64)
            print_success("Clés secrètes générées automatiquement")
        else:
            self.config['SECRET_KEY'] = prompt_input("Clé secrète principale", secret=True, required=True)
            self.config['JWT_SECRET'] = prompt_input("Clé secrète JWT", secret=True, required=True)
        
        # Configuration CORS
        if self.config['DEPLOYMENT_TYPE'] != 'dev':
            if prompt_yes_no("Configurer des origines CORS supplémentaires ?", default=False):
                additional_origins = prompt_input("Origines supplémentaires (séparées par des virgules)")
                if additional_origins:
                    self.config['ALLOWED_ORIGINS'] += f",{additional_origins}"

    def collect_optional_features(self):
        """Collecte la configuration des fonctionnalités optionnelles"""
        print_header("FONCTIONNALITÉS OPTIONNELLES")
        
        # Configuration des logs
        log_levels = {
            "debug": "Debug (très détaillé)",
            "info": "Info (recommandé)",
            "warning": "Warning (erreurs seulement)",
            "error": "Error (erreurs critiques)"
        }
        
        self.config['LOG_LEVEL'] = prompt_choice(
            "Niveau de logs", 
            log_levels, 
            default="info"
        ).upper()
        
        # Configuration du heartbeat
        self.config['HEARTBEAT_INTERVAL'] = prompt_input(
            "Intervalle de heartbeat organisateur (secondes)", 
            default="60"
        )
        
        # Configuration de suppression automatique
        self.config['AUTO_DELETE_HOURS'] = prompt_input(
            "Délai de suppression automatique après absence organisateur (heures)", 
            default="12"
        )
        
        # Configuration des rapports
        if prompt_yes_no("Activer la compression PDF ?", default=True):
            self.config['PDF_COMPRESSION'] = "true"
        else:
            self.config['PDF_COMPRESSION'] = "false"

    def collect_contact_info(self):
        """Collecte les informations de contact (optionnel)"""
        print_header("INFORMATIONS DE CONTACT (OPTIONNEL)")
        
        if prompt_yes_no("Ajouter des informations de contact dans l'application ?", default=False):
            self.config['ADMIN_EMAIL'] = prompt_input(
                "Email administrateur", 
                validator=validate_email,
                required=False
            ) or ""
            self.config['SUPPORT_URL'] = prompt_input(
                "URL de support/documentation", 
                validator=validate_url,
                required=False
            ) or ""
            self.config['ORGANIZATION_NAME'] = prompt_input(
                "Nom de l'organisation",
                required=False
            ) or ""

    def generate_env_files(self):
        """Génère les fichiers .env"""
        print_header("GÉNÉRATION DES FICHIERS .ENV")
        
        # .env racine
        root_env = f"""# Vote Secret - Configuration Racine
# Généré automatiquement le {self._get_timestamp()}

# Type de déploiement
DEPLOYMENT_TYPE={self.config['DEPLOYMENT_TYPE']}

# URLs principales
FRONTEND_URL={self.config['FRONTEND_URL']}
BACKEND_URL={self.config['BACKEND_URL']}

# Base de données
MONGO_URL={self.config['MONGO_URL']}
DB_NAME={self.config['DB_NAME']}

# Sécurité
SECRET_KEY={self.config['SECRET_KEY']}
JWT_SECRET={self.config['JWT_SECRET']}
ALLOWED_ORIGINS={self.config['ALLOWED_ORIGINS']}

# Configuration
LOG_LEVEL={self.config['LOG_LEVEL']}
HEARTBEAT_INTERVAL={self.config['HEARTBEAT_INTERVAL']}
AUTO_DELETE_HOURS={self.config['AUTO_DELETE_HOURS']}
PDF_COMPRESSION={self.config['PDF_COMPRESSION']}

# Optionnel
ADMIN_EMAIL={self.config.get('ADMIN_EMAIL', '')}
SUPPORT_URL={self.config.get('SUPPORT_URL', '')}
ORGANIZATION_NAME={self.config.get('ORGANIZATION_NAME', '')}
"""
        
        # .env backend
        backend_env = f"""# Vote Secret - Configuration Backend
# Généré automatiquement le {self._get_timestamp()}

# Base de données
MONGO_URL={self.config['MONGO_URL']}
DB_NAME={self.config['DB_NAME']}

# Sécurité
SECRET_KEY={self.config['SECRET_KEY']}
JWT_SECRET={self.config['JWT_SECRET']}
ALLOWED_ORIGINS={self.config['ALLOWED_ORIGINS']}

# Configuration serveur
HOST=0.0.0.0
PORT=8001
LOG_LEVEL={self.config['LOG_LEVEL']}

# Fonctionnalités
HEARTBEAT_INTERVAL={self.config['HEARTBEAT_INTERVAL']}
AUTO_DELETE_HOURS={self.config['AUTO_DELETE_HOURS']}
PDF_COMPRESSION={self.config['PDF_COMPRESSION']}

# Optionnel
ADMIN_EMAIL={self.config.get('ADMIN_EMAIL', '')}
SUPPORT_URL={self.config.get('SUPPORT_URL', '')}
ORGANIZATION_NAME={self.config.get('ORGANIZATION_NAME', '')}
"""
        
        # .env frontend
        frontend_env = f"""# Vote Secret - Configuration Frontend
# Généré automatiquement le {self._get_timestamp()}

# URL du backend (utilisée par React)
REACT_APP_BACKEND_URL={self.config['BACKEND_URL']}

# Configuration optionnelle
REACT_APP_APP_NAME=Vote Secret
REACT_APP_VERSION=2.0.0
REACT_APP_ADMIN_EMAIL={self.config.get('ADMIN_EMAIL', '')}
REACT_APP_SUPPORT_URL={self.config.get('SUPPORT_URL', '')}
REACT_APP_ORGANIZATION_NAME={self.config.get('ORGANIZATION_NAME', '')}

# Build configuration
GENERATE_SOURCEMAP=false
"""
        
        # Écriture des fichiers
        self._write_env_file('.env', root_env)
        self._write_env_file('backend/.env', backend_env)
        self._write_env_file('frontend/.env', frontend_env)
        
        print_success("Fichiers .env générés avec succès !")

    def _write_env_file(self, path: str, content: str):
        """Écrit un fichier .env"""
        full_path = self.project_root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success(f"Fichier {path} créé")

    def _get_timestamp(self) -> str:
        """Retourne un timestamp formaté"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_installation_guide(self):
        """Génère un guide d'installation"""
        print_header("GÉNÉRATION DU GUIDE D'INSTALLATION")
        
        guide_content = f"""# Vote Secret - Guide d'Installation
Généré automatiquement le {self._get_timestamp()}

## Configuration détectée
- **Type de déploiement:** {self.config['DEPLOYMENT_TYPE']}
- **Frontend:** {self.config['FRONTEND_URL']}
- **Backend:** {self.config['BACKEND_URL']}
- **Base de données:** {self.config['DB_NAME']}

## Installation rapide

### 1. Installation des dépendances
```bash
# Installation de toutes les dépendances
npm run install:all

# Ou installation séparée
npm run install:backend  # Backend Python
npm run install:frontend # Frontend React
```

### 2. Démarrage en développement
```bash
# Démarrage complet (frontend + backend)
npm run dev

# Ou démarrage séparé
npm run dev:backend   # Backend sur port 8001
npm run dev:frontend  # Frontend sur port 3000
```

### 3. Build pour production
```bash
# Build complet
npm run build

# Démarrage en production
npm run start
```

## Scripts disponibles

### Développement
- `npm run dev` - Démarrage complet en mode développement
- `npm run dev:backend` - Backend seulement
- `npm run dev:frontend` - Frontend seulement

### Production
- `npm run build` - Build optimisé pour production
- `npm run start` - Démarrage en mode production

### Maintenance
- `npm run test` - Tests automatisés
- `npm run lint` - Vérification du code
- `npm run format` - Formatage automatique
- `npm run clean` - Nettoyage des caches

## Configuration personnalisée

Les fichiers .env ont été générés avec vos paramètres.
Vous pouvez les modifier manuellement si nécessaire :

- `/.env` - Configuration globale
- `/backend/.env` - Configuration backend
- `/frontend/.env` - Configuration frontend

## Dépannage

### Problèmes courants

1. **Erreur de connexion MongoDB**
   - Vérifiez que MongoDB est démarré
   - Vérifiez l'URL dans MONGO_URL

2. **Erreur CORS**
   - Vérifiez ALLOWED_ORIGINS dans backend/.env
   - Assurez-vous que les URLs correspondent

3. **Port déjà utilisé**
   - Backend: modifiez PORT dans backend/.env
   - Frontend: modifiez le port dans package.json

### Logs
- Backend: Les logs s'affichent dans le terminal
- Niveau configuré: {self.config['LOG_LEVEL']}

## Support

- Version: Vote Secret v2.0.0"""
        
        if self.config.get('ADMIN_EMAIL'):
            guide_content += f"\n- Contact: {self.config['ADMIN_EMAIL']}"
        if self.config.get('SUPPORT_URL'):
            guide_content += f"\n- Support: {self.config['SUPPORT_URL']}"
        
        guide_content += """

## Fonctionnalités avancées

### Récupération de réunions
Les organisateurs peuvent générer des URLs de récupération sécurisées pour revenir à leur réunion en cas de fermeture de navigateur.

### Protection de fermeture
Les réunions ne peuvent être fermées qu'après téléchargement du rapport PDF, garantissant la conservation des données importantes.

### Gestion d'absence
En cas d'absence de l'organisateur, le système :
- Transfère automatiquement le leadership au scrutateur senior
- Propose des rapports partiels aux participants
- Supprime automatiquement les données après le délai configuré

Bon déploiement ! 🚀
"""
        
        guide_path = self.project_root / 'INSTALLATION.md'
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print_success("Guide d'installation généré: INSTALLATION.md")

    def run_post_setup_checks(self):
        """Effectue des vérifications après configuration"""
        print_header("VÉRIFICATIONS POST-CONFIGURATION")
        
        # Vérification des dépendances Python
        try:
            import fastapi
            print_success("FastAPI disponible")
        except ImportError:
            print_warning("FastAPI non installé - exécutez: pip install -r backend/requirements.txt")
        
        # Vérification de Node.js
        node_check = os.system("node --version > /dev/null 2>&1")
        if node_check == 0:
            print_success("Node.js disponible")
        else:
            print_warning("Node.js non trouvé - installez Node.js 20+")
        
        # Vérification de Yarn
        yarn_check = os.system("yarn --version > /dev/null 2>&1")
        if yarn_check == 0:
            print_success("Yarn disponible")
        else:
            print_warning("Yarn non trouvé - installez Yarn ou utilisez npm")
        
        # Vérification MongoDB si local
        if 'localhost' in self.config['MONGO_URL']:
            mongo_check = os.system("mongosh --version > /dev/null 2>&1")
            if mongo_check == 0:
                print_success("MongoDB Shell disponible")
            else:
                print_warning("MongoDB non détecté - assurez-vous qu'il soit installé et démarré")

    def display_next_steps(self):
        """Affiche les prochaines étapes"""
        print_header("PROCHAINES ÉTAPES")
        
        print(f"{Colors.GREEN}Configuration terminée avec succès ! 🎉{Colors.ENDC}\n")
        
        print("Commandes recommandées :")
        print(f"{Colors.CYAN}1. Installer les dépendances:{Colors.ENDC}")
        print("   npm run install:all")
        print()
        print(f"{Colors.CYAN}2. Démarrer en développement:{Colors.ENDC}")
        print("   npm run dev")
        print()
        print(f"{Colors.CYAN}3. Accéder à l'application:{Colors.ENDC}")
        print(f"   Frontend: {self.config['FRONTEND_URL']}")
        print(f"   Backend:  {self.config['BACKEND_URL']}")
        print()
        
        if self.config['DEPLOYMENT_TYPE'] != 'dev':
            print(f"{Colors.CYAN}4. Pour la production:{Colors.ENDC}")
            print("   npm run build")
            print("   npm run start")
            print()
        
        print(f"{Colors.BLUE}📖 Consultez INSTALLATION.md pour plus de détails{Colors.ENDC}")
        print(f"{Colors.BLUE}🔧 Modifiez les fichiers .env si nécessaire{Colors.ENDC}")

    def run(self):
        """Exécute le processus complet de configuration"""
        try:
            self.welcome()
            self.collect_deployment_info()
            self.collect_database_info()
            self.collect_security_info()
            self.collect_optional_features()
            self.collect_contact_info()
            self.generate_env_files()
            self.generate_installation_guide()
            self.run_post_setup_checks()
            self.display_next_steps()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Configuration interrompue par l'utilisateur.{Colors.ENDC}")
            sys.exit(1)
        except Exception as e:
            print_error(f"Erreur durant la configuration: {str(e)}")
            sys.exit(1)

def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Vote Secret - Assistant de Configuration")
        print("Usage: python3 setup_environment.py")
        print("\nCe script configure automatiquement votre environnement Vote Secret.")
        print("Il génère les fichiers .env nécessaires et un guide d'installation.")
        return
    
    setup = EnvironmentSetup()
    setup.run()

if __name__ == "__main__":
    main()