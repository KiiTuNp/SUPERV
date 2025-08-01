#!/usr/bin/env python3
"""
Vote Secret v2.0 - Configuration Environnement de Production
===========================================================

Script de configuration de l'environnement pour déploiement production.
Intègre les fonctionnalités de setup_environment.py avec optimisations serveur.

Auteur: Assistant AI
Version: 2.0.0
Date: 2025-08-01
"""

import os
import sys
import subprocess
import json
import secrets
import string
import re
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

# Réutilisation des classes de couleurs du script principal
sys.path.append(str(Path(__file__).parent))

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_step(step_num: int, total_steps: int, description: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}[ÉTAPE {step_num}/{total_steps}] {description}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.ENDC}")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

def prompt_continue(message: str = "Continuer ?") -> bool:
    while True:
        response = input(f"\n{Colors.BLUE}{message} [O/n]{Colors.ENDC}: ").strip().lower()
        if response in ['', 'o', 'oui', 'y', 'yes']:
            return True
        elif response in ['n', 'non', 'no']:
            return False
        print_warning("Réponse invalide. Utilisez 'o' pour oui ou 'n' pour non.")

def prompt_input(prompt: str, default: Optional[str] = None, required: bool = True, 
                 validator: Optional[callable] = None, secret: bool = False) -> str:
    while True:
        if default:
            display_prompt = f"{Colors.BLUE}{prompt} [{default}]{Colors.ENDC}: "
        else:
            display_prompt = f"{Colors.BLUE}{prompt}{Colors.ENDC}: "
        
        if secret:
            import getpass
            value = getpass.getpass(display_prompt)
        else:
            value = input(display_prompt).strip()
        
        if not value and default:
            value = default
        
        if not value and required:
            print_error("Cette valeur est requise.")
            continue
        
        if validator and value and not validator(value):
            print_error("Format invalide.")
            continue
        
        return value

def generate_secret_key(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_url(url: str) -> bool:
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def validate_email(email: str) -> bool:
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return email_pattern.match(email) is not None

def validate_domain(domain: str) -> bool:
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    return domain_pattern.match(domain) is not None

class ProductionEnvironmentSetup:
    """Configuration d'environnement pour production"""
    
    def __init__(self):
        self.config = {}
        self.project_root = Path(__file__).parent
        self.total_steps = 7
        
    def welcome(self):
        print_header("CONFIGURATION ENVIRONNEMENT PRODUCTION")
        print(f"{Colors.CYAN}Configuration automatique de l'environnement Vote Secret pour production{Colors.ENDC}")
        print(f"{Colors.CYAN}Ce script configure tous les paramètres nécessaires au déploiement.{Colors.ENDC}\n")
        
        print_warning("Configuration pour serveur de production !")
        print_info("Cette configuration inclut HTTPS, domaines personnalisés et optimisations serveur.")

    def step_1_server_info(self) -> bool:
        """Collecte les informations serveur"""
        print_step(1, self.total_steps, "Informations Serveur")
        
        # Mode de déploiement
        print_info("Choisissez le mode de déploiement:")
        print("  [1] Simple VPS Ubuntu (recommandé pour la plupart des cas)")
        print("  [2] Production avancée (utilisateur dédié, sécurité renforcée)")
        
        deploy_mode_choice = prompt_input(
            "Mode de déploiement", 
            default="1"
        )
        
        if deploy_mode_choice == "2":
            self.config['DEPLOY_MODE'] = 'advanced'
            self.config['DEPLOY_USER'] = 'vote-secret'
            self.config['APP_DIR'] = '/opt/vote-secret'
            print_info("Mode avancé sélectionné : utilisateur dédié vote-secret, répertoire /opt/vote-secret")
        else:
            self.config['DEPLOY_MODE'] = 'simple'
            ubuntu_user = prompt_input("Nom d'utilisateur Ubuntu", default="ubuntu")
            self.config['DEPLOY_USER'] = ubuntu_user
            self.config['APP_DIR'] = f'/home/{ubuntu_user}/vote-secret'
            print_info(f"Mode simple sélectionné : utilisateur {ubuntu_user}, répertoire {self.config['APP_DIR']}")
        
        # Informations serveur
        self.config['SERVER_NAME'] = prompt_input(
            "Nom du serveur (pour logs)", 
            default="vote-secret-prod"
        )
        
        # Domaine principal
        self.config['DOMAIN'] = prompt_input(
            "Domaine principal (ex: vote.monentreprise.com)",
            required=True,
            validator=validate_domain
        )
        
        # SSL/TLS
        ssl_choice = prompt_input(
            "Configuration SSL/TLS ? [1] Let's Encrypt auto [2] Certificats existants [3] Auto-signé",
            default="1"
        )
        
        if ssl_choice == "1":
            self.config['SSL_MODE'] = 'letsencrypt'
            self.config['SSL_EMAIL'] = prompt_input(
                "Email pour Let's Encrypt",
                required=True,
                validator=validate_email
            )
        elif ssl_choice == "2":
            self.config['SSL_MODE'] = 'existing'
            self.config['SSL_CERT_PATH'] = prompt_input(
                "Chemin certificat SSL (.crt)",
                required=True
            )
            self.config['SSL_KEY_PATH'] = prompt_input(
                "Chemin clé privée SSL (.key)",
                required=True
            )
        else:
            self.config['SSL_MODE'] = 'selfsigned'
            print_warning("Les certificats auto-signés ne sont pas recommandés en production")
        
        # URLs finales
        protocol = "https" if self.config.get('SSL_MODE') != 'none' else "http"
        self.config['FRONTEND_URL'] = f"{protocol}://{self.config['DOMAIN']}"
        self.config['BACKEND_URL'] = f"{protocol}://{self.config['DOMAIN']}/api"
        
        print_success(f"Frontend: {self.config['FRONTEND_URL']}")
        print_success(f"Backend: {self.config['BACKEND_URL']}")
        
        return prompt_continue()

    def step_2_database_production(self) -> bool:
        """Configuration base de données production"""
        print_step(2, self.total_steps, "Configuration Base de Données")
        
        db_types = {
            "1": "MongoDB local sécurisé (recommandé)",
            "2": "MongoDB Atlas (cloud)",
            "3": "MongoDB distant (serveur dédié)"
        }
        
        print("Types de base de données disponibles :")
        for key, desc in db_types.items():
            print(f"  {key}. {desc}")
        
        db_choice = prompt_input("Votre choix", default="1")
        
        if db_choice == "1":
            self.config['DB_TYPE'] = 'local'
            self.config['MONGO_URL'] = 'mongodb://127.0.0.1:27017'
            self.config['DB_NAME'] = prompt_input("Nom de la base de données", default="vote_secret_prod")
            
            # Configuration sécurité MongoDB locale
            if prompt_input("Activer l'authentification MongoDB ? [O/n]", default="O").lower().startswith('o'):
                self.config['MONGO_AUTH'] = True
                self.config['MONGO_USER'] = prompt_input("Utilisateur MongoDB", default="vote_secret_user")
                self.config['MONGO_PASSWORD'] = prompt_input("Mot de passe MongoDB", secret=True, required=True)
                self.config['MONGO_URL'] = f"mongodb://{self.config['MONGO_USER']}:{self.config['MONGO_PASSWORD']}@127.0.0.1:27017/{self.config['DB_NAME']}"
            else:
                self.config['MONGO_AUTH'] = False
                
        elif db_choice == "2":
            self.config['DB_TYPE'] = 'atlas'
            print_info("Récupérez votre chaîne de connexion depuis MongoDB Atlas")
            self.config['MONGO_URL'] = prompt_input("URL MongoDB Atlas (mongodb+srv://...)", required=True)
            self.config['DB_NAME'] = prompt_input("Nom de la base de données", default="vote_secret_prod")
            
        else:
            self.config['DB_TYPE'] = 'remote'
            self.config['MONGO_HOST'] = prompt_input("Adresse serveur MongoDB", required=True)
            self.config['MONGO_PORT'] = prompt_input("Port MongoDB", default="27017")
            self.config['MONGO_USER'] = prompt_input("Utilisateur MongoDB", required=True)
            self.config['MONGO_PASSWORD'] = prompt_input("Mot de passe MongoDB", secret=True, required=True)
            self.config['DB_NAME'] = prompt_input("Nom de la base de données", default="vote_secret_prod")
            self.config['MONGO_URL'] = f"mongodb://{self.config['MONGO_USER']}:{self.config['MONGO_PASSWORD']}@{self.config['MONGO_HOST']}:{self.config['MONGO_PORT']}/{self.config['DB_NAME']}"
        
        return prompt_continue()

    def step_3_security_production(self) -> bool:
        """Configuration sécurité production"""
        print_step(3, self.total_steps, "Configuration Sécurité")
        
        # Génération automatique des clés
        print_info("Génération des clés de sécurité...")
        self.config['SECRET_KEY'] = generate_secret_key(64)
        self.config['JWT_SECRET'] = generate_secret_key(64)
        self.config['SESSION_SECRET'] = generate_secret_key(32)
        print_success("Clés secrètes générées")
        
        # Configuration CORS
        cors_origins = [self.config['FRONTEND_URL']]
        
        if prompt_input("Ajouter des origines CORS supplémentaires ? [o/N]", default="N").lower().startswith('o'):
            additional = prompt_input("Origines supplémentaires (séparées par virgules)")
            if additional:
                cors_origins.extend([origin.strip() for origin in additional.split(',')])
        
        self.config['ALLOWED_ORIGINS'] = ','.join(cors_origins)
        
        # Configuration des limites de sécurité
        self.config['MAX_PARTICIPANTS'] = prompt_input("Limite max participants par réunion", default="500")
        self.config['MAX_POLLS'] = prompt_input("Limite max sondages par réunion", default="50")
        self.config['MAX_MEETINGS'] = prompt_input("Limite max réunions simultanées", default="100")
        
        # Rate limiting
        self.config['RATE_LIMIT_REQUESTS'] = prompt_input("Limite requêtes par minute par IP", default="100")
        self.config['RATE_LIMIT_BURST'] = prompt_input("Limite burst requêtes", default="20")
        
        return prompt_continue()

    def step_4_performance_config(self) -> bool:
        """Configuration performance"""
        print_step(4, self.total_steps, "Configuration Performance")
        
        # Configuration serveur
        self.config['WORKERS'] = prompt_input("Nombre de workers backend", default="4")
        self.config['WORKER_CONNECTIONS'] = prompt_input("Connexions par worker", default="1000")
        
        # Configuration cache
        if prompt_input("Activer Redis pour le cache ? [O/n]", default="O").lower().startswith('o'):
            self.config['REDIS_ENABLED'] = True
            self.config['REDIS_URL'] = prompt_input("URL Redis", default="redis://localhost:6379")
        else:
            self.config['REDIS_ENABLED'] = False
        
        # Configuration logs
        log_levels = {"1": "ERROR", "2": "WARNING", "3": "INFO", "4": "DEBUG"}
        print("Niveaux de logs :")
        for key, level in log_levels.items():
            print(f"  {key}. {level}")
        
        log_choice = prompt_input("Niveau de logs", default="3")
        self.config['LOG_LEVEL'] = log_levels.get(log_choice, "INFO")
        
        # Rotation des logs
        self.config['LOG_MAX_SIZE'] = prompt_input("Taille max des logs (MB)", default="100")
        self.config['LOG_BACKUP_COUNT'] = prompt_input("Nombre de fichiers de sauvegarde", default="5")
        
        return prompt_continue()

    def step_5_monitoring_config(self) -> bool:
        """Configuration monitoring"""
        print_step(5, self.total_steps, "Configuration Monitoring")
        
        # Monitoring basique
        self.config['MONITORING_ENABLED'] = prompt_input("Activer le monitoring ? [O/n]", default="O").lower().startswith('o')
        
        if self.config['MONITORING_ENABLED']:
            self.config['METRICS_PORT'] = prompt_input("Port pour métriques", default="9090")
            
            # Alertes
            if prompt_input("Configurer les alertes email ? [o/N]", default="N").lower().startswith('o'):
                self.config['ALERT_EMAIL'] = prompt_input("Email pour alertes", validator=validate_email)
                self.config['SMTP_SERVER'] = prompt_input("Serveur SMTP", default="localhost")
                self.config['SMTP_PORT'] = prompt_input("Port SMTP", default="587")
        
        # Health checks
        self.config['HEALTH_CHECK_INTERVAL'] = prompt_input("Intervalle health check (secondes)", default="30")
        
        return prompt_continue()

    def step_6_backup_config(self) -> bool:
        """Configuration sauvegarde"""
        print_step(6, self.total_steps, "Configuration Sauvegarde")
        
        self.config['BACKUP_ENABLED'] = prompt_input("Activer les sauvegardes automatiques ? [O/n]", default="O").lower().startswith('o')
        
        if self.config['BACKUP_ENABLED']:
            self.config['BACKUP_PATH'] = prompt_input("Répertoire de sauvegarde", default="/var/backups/vote-secret")
            self.config['BACKUP_FREQUENCY'] = prompt_input("Fréquence (daily/weekly)", default="daily")
            self.config['BACKUP_RETENTION'] = prompt_input("Rétention (jours)", default="30")
            
            # Sauvegarde distante
            if prompt_input("Configurer sauvegarde distante (S3/FTP) ? [o/N]", default="N").lower().startswith('o'):
                self.config['REMOTE_BACKUP'] = True
                backup_type = prompt_input("Type [1] S3 [2] FTP", default="1")
                
                if backup_type == "1":
                    self.config['S3_BUCKET'] = prompt_input("Nom du bucket S3")
                    self.config['S3_REGION'] = prompt_input("Région S3", default="eu-west-1")
                    self.config['AWS_ACCESS_KEY'] = prompt_input("AWS Access Key", secret=True)
                    self.config['AWS_SECRET_KEY'] = prompt_input("AWS Secret Key", secret=True)
                else:
                    self.config['FTP_HOST'] = prompt_input("Serveur FTP")
                    self.config['FTP_USER'] = prompt_input("Utilisateur FTP")
                    self.config['FTP_PASSWORD'] = prompt_input("Mot de passe FTP", secret=True)
        
        return prompt_continue()

    def step_7_generate_config_files(self) -> bool:
        """Génération des fichiers de configuration"""
        print_step(7, self.total_steps, "Génération des Fichiers de Configuration")
        
        print_info("Génération de tous les fichiers de configuration...")
        
        # Créer les répertoires nécessaires
        config_dirs = ['config', 'scripts']
        for dir_name in config_dirs:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            print_success(f"Répertoire {dir_name}/ créé")
        
        # Détection de l'environnement de déploiement
        has_systemd = os.path.exists('/run/systemd/system')
        has_supervisor = os.path.exists('/usr/bin/supervisorctl') or os.path.exists('/usr/local/bin/supervisorctl')
        
        print_info(f"Environnement détecté: SystemD={has_systemd}, Supervisor={has_supervisor}")
        
        # Génération des configurations selon l'environnement
        configs_generated = []
        
        try:
            # Configuration de base
            configs = {
                '.env': self._generate_root_env(),
                'backend/.env': self._generate_backend_env(),
                'frontend/.env': self._generate_frontend_env(),
            }
            
            # Configuration Nginx (HTTP et SSL)
            configs['config/nginx.conf'] = self._generate_nginx_config_http()
            configs['config/nginx-ssl.conf'] = self._generate_nginx_config_ssl()
            
            # Configuration Gunicorn
            configs['config/gunicorn.conf.py'] = self._generate_gunicorn_config()
            
            # Services selon l'environnement
            if has_systemd:
                configs['config/vote-secret.service'] = self._generate_systemd_service()
                print_info("Configuration SystemD générée")
            
            if has_supervisor:
                configs['config/vote-secret.conf'] = self._generate_supervisor_service()
                print_info("Configuration Supervisor générée")
            
            # Scripts de gestion
            management_scripts = self._generate_management_scripts()
            configs.update({
                'scripts/manage.sh': management_scripts['manage'],
                'scripts/backup.sh': management_scripts['backup'],
                'scripts/monitor.sh': management_scripts['monitor']
            })
            
            # Écriture de tous les fichiers
            for path, content in configs.items():
                if content:  # Éviter d'écrire des fichiers vides
                    success = self._write_config_file(path, content)
                    if success:
                        configs_generated.append(path)
            
            # Guide de déploiement
            deployment_guide = self._generate_deployment_guide()
            if self._write_config_file('DEPLOYMENT_GUIDE.md', deployment_guide):
                configs_generated.append('DEPLOYMENT_GUIDE.md')
            
            print_success(f"Configuration générée avec succès ! ({len(configs_generated)} fichiers)")
            
            # Résumé des fichiers générés
            print_info("Fichiers de configuration générés :")
            for config_file in sorted(configs_generated):
                print(f"  ✓ {config_file}")
            
            # Vérification de la cohérence
            self._validate_generated_configs(configs_generated)
            
            return True
            
        except Exception as e:
            print_error(f"Erreur lors de la génération: {str(e)}")
            return False

    def _generate_root_env(self) -> str:
        return f"""# Vote Secret v2.0 - Configuration Production
# Généré automatiquement le {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Serveur
SERVER_NAME={self.config['SERVER_NAME']}
DOMAIN={self.config['DOMAIN']}
DEPLOYMENT_TYPE=production

# URLs
FRONTEND_URL={self.config['FRONTEND_URL']}
BACKEND_URL={self.config['BACKEND_URL']}

# Base de données
MONGO_URL={self.config['MONGO_URL']}
DB_NAME={self.config['DB_NAME']}

# Sécurité
SECRET_KEY={self.config['SECRET_KEY']}
JWT_SECRET={self.config['JWT_SECRET']}
SESSION_SECRET={self.config['SESSION_SECRET']}
ALLOWED_ORIGINS={self.config['ALLOWED_ORIGINS']}

# Limites
MAX_PARTICIPANTS={self.config['MAX_PARTICIPANTS']}
MAX_POLLS={self.config['MAX_POLLS']}
MAX_MEETINGS={self.config['MAX_MEETINGS']}
RATE_LIMIT_REQUESTS={self.config['RATE_LIMIT_REQUESTS']}
RATE_LIMIT_BURST={self.config['RATE_LIMIT_BURST']}

# Performance
WORKERS={self.config['WORKERS']}
WORKER_CONNECTIONS={self.config['WORKER_CONNECTIONS']}
REDIS_ENABLED={self.config.get('REDIS_ENABLED', False)}
REDIS_URL={self.config.get('REDIS_URL', '')}

# Logs
LOG_LEVEL={self.config['LOG_LEVEL']}
LOG_MAX_SIZE={self.config['LOG_MAX_SIZE']}
LOG_BACKUP_COUNT={self.config['LOG_BACKUP_COUNT']}

# Monitoring
MONITORING_ENABLED={self.config['MONITORING_ENABLED']}
METRICS_PORT={self.config.get('METRICS_PORT', '')}
HEALTH_CHECK_INTERVAL={self.config['HEALTH_CHECK_INTERVAL']}

# SSL
SSL_MODE={self.config['SSL_MODE']}
SSL_EMAIL={self.config.get('SSL_EMAIL', '')}
SSL_CERT_PATH={self.config.get('SSL_CERT_PATH', '')}
SSL_KEY_PATH={self.config.get('SSL_KEY_PATH', '')}

# Sauvegarde
BACKUP_ENABLED={self.config['BACKUP_ENABLED']}
BACKUP_PATH={self.config.get('BACKUP_PATH', '')}
BACKUP_FREQUENCY={self.config.get('BACKUP_FREQUENCY', '')}
BACKUP_RETENTION={self.config.get('BACKUP_RETENTION', '')}
"""

    def _generate_backend_env(self) -> str:
        return f"""# Vote Secret v2.0 - Configuration Backend Production

# Serveur
HOST=0.0.0.0
PORT=8001
WORKERS={self.config['WORKERS']}

# Base de données
MONGO_URL={self.config['MONGO_URL']}
DB_NAME={self.config['DB_NAME']}

# Sécurité
SECRET_KEY={self.config['SECRET_KEY']}
JWT_SECRET={self.config['JWT_SECRET']}
ALLOWED_ORIGINS={self.config['ALLOWED_ORIGINS']}

# Limites applicatives
MAX_PARTICIPANTS={self.config['MAX_PARTICIPANTS']}
MAX_POLLS={self.config['MAX_POLLS']}
MAX_MEETINGS={self.config['MAX_MEETINGS']}

# Cache
REDIS_ENABLED={self.config.get('REDIS_ENABLED', False)}
REDIS_URL={self.config.get('REDIS_URL', '')}

# Logs
LOG_LEVEL={self.config['LOG_LEVEL']}
LOG_MAX_SIZE={self.config['LOG_MAX_SIZE']}MB
LOG_BACKUP_COUNT={self.config['LOG_BACKUP_COUNT']}

# Monitoring
METRICS_ENABLED={self.config['MONITORING_ENABLED']}
METRICS_PORT={self.config.get('METRICS_PORT', '9090')}

# Features
HEARTBEAT_INTERVAL=60
AUTO_DELETE_HOURS=12
PDF_COMPRESSION=true
"""

    def _generate_frontend_env(self) -> str:
        return f"""# Vote Secret v2.0 - Configuration Frontend Production

# URL du backend
REACT_APP_BACKEND_URL={self.config['BACKEND_URL']}

# Configuration application
REACT_APP_APP_NAME=Vote Secret
REACT_APP_VERSION=2.0.0
REACT_APP_DOMAIN={self.config['DOMAIN']}

# Build configuration
GENERATE_SOURCEMAP=false
REACT_APP_ENV=production

# Monitoring
REACT_APP_MONITORING_ENABLED={self.config['MONITORING_ENABLED']}

# Limites UI
REACT_APP_MAX_PARTICIPANTS={self.config['MAX_PARTICIPANTS']}
REACT_APP_MAX_POLLS={self.config['MAX_POLLS']}
"""

    def _generate_nginx_config(self) -> str:
        """Génère la configuration Nginx avec option HTTP temporaire"""
        return self._generate_nginx_config_http()
    
    def _generate_nginx_config_http(self) -> str:
        """Génère une configuration HTTP temporaire (avant SSL)"""
        return f"""# Vote Secret v2.0 - Configuration Nginx Temporaire (HTTP)
# Généré automatiquement - Configuration initiale avant SSL

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate={self.config['RATE_LIMIT_REQUESTS']}r/m;
limit_req_zone $binary_remote_addr zone=general:10m rate=100r/m;

# Main server configuration (HTTP only)
server {{
    listen 80;
    server_name {self.config['DOMAIN']};
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:;" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Let's Encrypt challenge (nécessaire pour certbot)
    location /.well-known/acme-challenge/ {{
        root /var/www/html;
    }}
    
    # Static files
    location /static/ {{
        alias /opt/vote-secret/frontend/build/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # API routes
    location /api/ {{
        limit_req zone=api burst={self.config['RATE_LIMIT_BURST']} nodelay;
        
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
    
    # Frontend routes
    location / {{
        limit_req zone=general burst=20 nodelay;
        
        root /opt/vote-secret/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
    
    # Health check
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
}}
"""
    
    def _generate_nginx_config_ssl(self) -> str:
        """Génère la configuration finale avec SSL"""
        app_name = self.config.get('SERVER_NAME', 'vote-secret')
        www_path = f"/var/www/{app_name}"
        
        ssl_config = ""
        redirect_config = ""
        
        if self.config['SSL_MODE'] == 'letsencrypt':
            redirect_config = f"""
# Redirect HTTP to HTTPS
server {{
    listen 80;
    server_name {self.config['DOMAIN']};
    
    # Let's Encrypt challenge (toujours accessible en HTTP)
    location /.well-known/acme-challenge/ {{
        root {www_path};
    }}
    
    # Redirect all other traffic to HTTPS
    location / {{
        return 301 https://$server_name$request_uri;
    }}
}}

"""
            ssl_config = f"""
    # SSL Configuration (Let's Encrypt)
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/{self.config['DOMAIN']}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{self.config['DOMAIN']}/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;"""
        elif self.config['SSL_MODE'] == 'existing':
            redirect_config = f"""
# Redirect HTTP to HTTPS
server {{
    listen 80;
    server_name {self.config['DOMAIN']};
    return 301 https://$server_name$request_uri;
}}

"""
            ssl_config = f"""
    # SSL Configuration (Certificats existants)
    listen 443 ssl http2;
    ssl_certificate {self.config['SSL_CERT_PATH']};
    ssl_certificate_key {self.config['SSL_KEY_PATH']};
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;"""

        return f"""# Vote Secret v2.0 - Configuration Nginx Production avec SSL
# Généré automatiquement

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate={self.config['RATE_LIMIT_REQUESTS']}r/m;
limit_req_zone $binary_remote_addr zone=general:10m rate=100r/m;
{redirect_config}
# Main server configuration
server {{{ssl_config}
    server_name {self.config['DOMAIN']};
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:;" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Static files
    location /static/ {{
        alias /opt/vote-secret/frontend/build/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # API routes
    location /api/ {{
        limit_req zone=api burst={self.config['RATE_LIMIT_BURST']} nodelay;
        
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
    
    # Frontend routes
    location / {{
        limit_req zone=general burst=20 nodelay;
        
        root /opt/vote-secret/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
    
    # Health check
    location /health {{
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }}
    
    # Monitoring (if enabled)
    {"location /metrics { proxy_pass http://127.0.0.1:" + self.config.get('METRICS_PORT', '9090') + "; allow 127.0.0.1; deny all; }" if self.config['MONITORING_ENABLED'] else ""}
}}
"""

    def _generate_systemd_service_simple(self) -> str:
        """Génère une configuration SystemD simplifiée pour VPS Ubuntu (recommandée)"""
        # Utiliser l'utilisateur ubuntu par défaut ou celui spécifié
        user = self.config.get('DEPLOY_USER', 'ubuntu')
        app_dir = self.config.get('APP_DIR', '/home/ubuntu/vote-secret')
        
        return f"""[Unit]
Description=Vote Secret v2.0 Backend Service
After=network.target
Wants=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={app_dir}/backend
Environment=PATH={app_dir}/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH={app_dir}/backend
ExecStart={app_dir}/venv/bin/gunicorn -w 4 -b 127.0.0.1:8001 --timeout 120 --keepalive 5 --max-requests 1000 server:app
Restart=always
RestartSec=3

# Logs
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""

    def _generate_systemd_service_advanced(self) -> str:
        """Génère une configuration SystemD avancée (pour production sécurisée)"""
        return f"""[Unit]
Description=Vote Secret v2.0 Backend Service
After=network.target mongodb.service
Wants=mongodb.service

[Service]
Type=exec
User=vote-secret
Group=vote-secret
WorkingDirectory=/opt/vote-secret/backend
Environment=PATH=/opt/vote-secret/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/opt/vote-secret/backend
ExecStart=/opt/vote-secret/venv/bin/gunicorn --config /opt/vote-secret/config/gunicorn.conf.py server:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

# Security
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/vote-secret
PrivateDevices=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vote-secret

[Install]
WantedBy=multi-user.target
"""

    def _generate_systemd_service(self) -> str:
        """Génère la configuration SystemD selon le mode de déploiement"""
        # Mode simple par défaut pour VPS Ubuntu
        deploy_mode = self.config.get('DEPLOY_MODE', 'simple')
        
        if deploy_mode == 'advanced':
            return self._generate_systemd_service_advanced()
        else:
            return self._generate_systemd_service_simple()

    def _generate_supervisor_service(self) -> str:
        """Génère la configuration Supervisor (pour environnements conteneurisés)"""
        return f"""[program:vote-secret]
command=/opt/vote-secret/venv/bin/gunicorn --config /opt/vote-secret/config/gunicorn.conf.py server:app
directory=/opt/vote-secret/backend
user=vote-secret
group=vote-secret
environment=PATH="/opt/vote-secret/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",PYTHONPATH="/opt/vote-secret/backend"
autostart=true
autorestart=true
startretries=3
redirect_stderr=true
stdout_logfile=/var/log/supervisor/vote-secret.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
stderr_logfile=/var/log/supervisor/vote-secret-error.log
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=3
killasgroup=true
stopasgroup=true
priority=999
"""

    def _generate_gunicorn_config(self) -> str:
        """Génère la configuration Gunicorn"""
        return f"""# Vote Secret v2.0 - Configuration Gunicorn Production
# Généré automatiquement

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8001"
backlog = 2048

# Worker processes
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 120
keepalive = 2

# Logging
accesslog = "/var/log/vote-secret/gunicorn-access.log"
errorlog = "/var/log/vote-secret/gunicorn-error.log"
loglevel = "{self.config['LOG_LEVEL'].lower()}"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "vote-secret"

# Server mechanics
daemon = False
pidfile = "/var/log/vote-secret/gunicorn.pid"
user = "vote-secret"
group = "vote-secret"
tmp_upload_dir = None

# SSL (not used, handled by Nginx)
keyfile = None
certfile = None

# Application configuration
raw_env = [
    'PYTHONPATH=/opt/vote-secret/backend',
]

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 100

# The maximum number of pending connections
backlog = 2048

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)
"""

    def _generate_management_scripts(self) -> Dict[str, str]:
        manage_script = f"""#!/bin/bash
# Vote Secret v2.0 - Script de gestion

set -e

ACTION="$1"
PROJECT_DIR="/opt/vote-secret"
SERVICE_NAME="vote-secret"

case "$ACTION" in
    start)
        echo "Démarrage de Vote Secret..."
        sudo systemctl start $SERVICE_NAME
        sudo systemctl start nginx
        echo "Services démarrés"
        ;;
    stop)
        echo "Arrêt de Vote Secret..."
        sudo systemctl stop $SERVICE_NAME
        echo "Service arrêté"
        ;;
    restart)
        echo "Redémarrage de Vote Secret..."
        sudo systemctl restart $SERVICE_NAME
        sudo systemctl reload nginx
        echo "Services redémarrés"
        ;;
    status)
        echo "Statut des services:"
        sudo systemctl status $SERVICE_NAME --no-pager
        sudo systemctl status nginx --no-pager
        ;;
    logs)
        echo "Logs en temps réel (Ctrl+C pour quitter):"
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    update)
        echo "Mise à jour de l'application..."
        cd $PROJECT_DIR
        git pull origin main
        source venv/bin/activate
        pip install -r backend/requirements.txt
        cd frontend && npm run build
        sudo systemctl restart $SERVICE_NAME
        echo "Mise à jour terminée"
        ;;
    backup)
        echo "Lancement de la sauvegarde..."
        $PROJECT_DIR/scripts/backup.sh
        ;;
    *)
        echo "Usage: $0 {{start|stop|restart|status|logs|update|backup}}"
        exit 1
        ;;
esac
"""

        backup_script = f"""#!/bin/bash
# Vote Secret v2.0 - Script de sauvegarde

set -e

BACKUP_DIR="{self.config.get('BACKUP_PATH', '/var/backups/vote-secret')}"
DB_NAME="{self.config['DB_NAME']}"
RETENTION_DAYS="{self.config.get('BACKUP_RETENTION', '30')}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "Début de la sauvegarde - $TIMESTAMP"

# Création du répertoire de sauvegarde
sudo mkdir -p "$BACKUP_DIR"

# Sauvegarde MongoDB
echo "Sauvegarde de la base de données..."
mongodump --db "$DB_NAME" --out "$BACKUP_DIR/db_$TIMESTAMP"

# Sauvegarde des fichiers de configuration
echo "Sauvegarde de la configuration..."
sudo tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" -C /opt/vote-secret config/ .env backend/.env frontend/.env

# Compression de la sauvegarde complète
echo "Compression..."
sudo tar -czf "$BACKUP_DIR/full_backup_$TIMESTAMP.tar.gz" -C "$BACKUP_DIR" "db_$TIMESTAMP" "config_$TIMESTAMP.tar.gz"

# Nettoyage des fichiers temporaires
sudo rm -rf "$BACKUP_DIR/db_$TIMESTAMP" "$BACKUP_DIR/config_$TIMESTAMP.tar.gz"

# Suppression des anciennes sauvegardes
echo "Nettoyage des anciennes sauvegardes..."
find "$BACKUP_DIR" -name "full_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Sauvegarde terminée: $BACKUP_DIR/full_backup_$TIMESTAMP.tar.gz"

# Sauvegarde distante si configurée
{"# TODO: Implémenter sauvegarde S3/FTP" if self.config.get('REMOTE_BACKUP') else ""}
"""

        monitor_script = f"""#!/bin/bash
# Vote Secret v2.0 - Script de monitoring

set -e

echo "=== Vote Secret - Status de Santé ==="
echo "Date: $(date)"
echo

# Vérification des services
echo "Services:"
systemctl is-active vote-secret && echo "✅ Backend: Actif" || echo "❌ Backend: Inactif"
systemctl is-active nginx && echo "✅ Nginx: Actif" || echo "❌ Nginx: Inactif"
systemctl is-active mongod && echo "✅ MongoDB: Actif" || echo "❌ MongoDB: Inactif"
echo

# Vérification des ports
echo "Ports d'écoute:"
netstat -tuln | grep :80 && echo "✅ Port 80: Ouvert" || echo "❌ Port 80: Fermé"
netstat -tuln | grep :443 && echo "✅ Port 443: Ouvert" || echo "❌ Port 443: Fermé"
netstat -tuln | grep :8001 && echo "✅ Port 8001: Ouvert" || echo "❌ Port 8001: Fermé"
echo

# Vérification de l'espace disque
echo "Espace disque:"
df -h / | tail -1 | awk '{{print "Utilisation: " $5 " - Disponible: " $4}}'
echo

# Test de connectivité
echo "Tests de connectivité:"
curl -s -o /dev/null -w "%{{http_code}}" http://localhost/health | grep -q 200 && echo "✅ Health check: OK" || echo "❌ Health check: Échec"

# Logs récents
echo
echo "Erreurs récentes (5 dernières):"
journalctl -u vote-secret --since "1 hour ago" -p err --no-pager -n 5

echo
echo "=== Fin du rapport ==="
"""

        return {
            'manage': manage_script,
            'backup': backup_script,
            'monitor': monitor_script
        }

    def _generate_deployment_guide(self) -> str:
        return f"""# Vote Secret v2.0 - Guide de Déploiement Production

**Configuration générée le:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Informations de Configuration

- **Domaine:** {self.config['DOMAIN']}
- **Frontend:** {self.config['FRONTEND_URL']}
- **Backend:** {self.config['BACKEND_URL']}
- **Base de données:** {self.config['DB_NAME']} ({self.config.get('DB_TYPE', 'local')})
- **SSL:** {self.config['SSL_MODE']}

## Étapes de Déploiement

### 1. Préparation du serveur
```bash
# Exécuter en tant qu'utilisateur avec sudo
sudo mkdir -p /opt/vote-secret
sudo useradd -r -s /bin/false vote-secret
sudo chown vote-secret:vote-secret /opt/vote-secret
```

### 2. Déploiement de l'application
```bash
# Copier les fichiers
sudo cp -r . /opt/vote-secret/
sudo chown -R vote-secret:vote-secret /opt/vote-secret

# Installation des dépendances backend
cd /opt/vote-secret
sudo -u vote-secret python3 -m venv venv
sudo -u vote-secret ./venv/bin/pip install -r backend/requirements.txt

# Build frontend
cd frontend
npm install
npm run build
```

### 3. Configuration Nginx
```bash
sudo cp config/nginx.conf /etc/nginx/sites-available/vote-secret
sudo ln -s /etc/nginx/sites-available/vote-secret /etc/nginx/sites-enabled/
{"sudo certbot --nginx -d " + self.config['DOMAIN'] + " --email " + self.config.get('SSL_EMAIL', '') if self.config['SSL_MODE'] == 'letsencrypt' else "# Configuration SSL manuelle requise"}
sudo nginx -t && sudo systemctl reload nginx
```

### 4. Configuration des services
```bash
sudo cp config/vote-secret.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vote-secret
sudo systemctl start vote-secret
```

### 5. Scripts de gestion
```bash
sudo cp scripts/*.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/{{manage,backup,monitor}}.sh
```

### 6. Configuration MongoDB locale
{"" if self.config.get('DB_TYPE') != 'local' else f'''```bash
# Sécurisation MongoDB (si activée)
mongo
use {self.config['DB_NAME']}
db.createUser({{
  user: "{self.config.get('MONGO_USER', '')}",
  pwd: "{self.config.get('MONGO_PASSWORD', '')}",
  roles: [{{ role: "readWrite", db: "{self.config['DB_NAME']}" }}]
}})
exit
```'''}

### 7. Tests de déploiement
```bash
# Vérification des services
./scripts/manage.sh status

# Test de santé
./scripts/monitor.sh

# Test de l'application
curl -I {self.config['FRONTEND_URL']}
```

## Configuration des Sauvegardes

### Sauvegarde automatique
```bash
# Ajouter au crontab
sudo crontab -e

# Sauvegarde quotidienne à 2h00
0 2 * * * /usr/local/bin/backup.sh >> /var/log/vote-secret-backup.log 2>&1
```

## Monitoring et Maintenance

### Commandes utiles
```bash
# Gestion du service
./scripts/manage.sh {{start|stop|restart|status|logs}}

# Monitoring
./scripts/monitor.sh

# Sauvegarde manuelle
./scripts/backup.sh

# Mise à jour
./scripts/manage.sh update
```

### Logs
- **Application:** `journalctl -u vote-secret -f`
- **Nginx:** `tail -f /var/log/nginx/access.log`
- **Erreurs:** `tail -f /var/log/nginx/error.log`

## Sécurité

### Recommandations
1. Configurer le firewall (UFW recommandé)
2. Activer fail2ban pour les tentatives de connexion
3. Mettre à jour régulièrement le système
4. Surveiller les logs d'accès
5. Effectuer des sauvegardes régulières

### Ports à ouvrir
- 80 (HTTP - redirection)
- 443 (HTTPS)
- 22 (SSH - administration)

## Dépannage

### Problèmes courants
1. **Service ne démarre pas:** Vérifier les logs avec `journalctl -u vote-secret`
2. **Erreur 502:** Vérifier que le backend écoute sur le port 8001
3. **Erreur SSL:** Vérifier les certificats et la configuration Nginx
4. **Base de données:** Vérifier la connectivité MongoDB

### Support
- Logs d'application: `/var/log/vote-secret/`
- Configuration: `/opt/vote-secret/config/`
- Scripts: `/usr/local/bin/`

---
*Vote Secret v2.0 - Déploiement Production*
"""

    def _validate_generated_configs(self, configs_generated: list):
        """Valide la cohérence des configurations générées"""
        print_info("Validation des configurations générées...")
        
        validation_results = []
        
        # Vérification des fichiers critiques
        critical_files = ['.env', 'backend/.env', 'frontend/.env', 'config/gunicorn.conf.py']
        for critical_file in critical_files:
            if critical_file in configs_generated:
                validation_results.append(f"✓ {critical_file}")
            else:
                validation_results.append(f"✗ {critical_file} MANQUANT")
        
        # Vérification de la cohérence des URLs
        try:
            frontend_url = self.config.get('FRONTEND_URL', '')
            backend_url = self.config.get('BACKEND_URL', '')
            domain = self.config.get('DOMAIN', '')
            
            if domain in frontend_url and domain in backend_url:
                validation_results.append("✓ URLs cohérentes")
            else:
                validation_results.append("⚠ URLs potentiellement incohérentes")
                
        except Exception:
            validation_results.append("? Impossible de valider les URLs")
        
        # Vérification SSL
        ssl_mode = self.config.get('SSL_MODE', 'none')
        if ssl_mode != 'none' and 'config/nginx-ssl.conf' in configs_generated:
            validation_results.append("✓ Configuration SSL présente")
        elif ssl_mode == 'none':
            validation_results.append("⚠ SSL désactivé (non recommandé pour la production)")
        
        # Affichage des résultats
        print_info("Résultats de validation :")
        for result in validation_results:
            if result.startswith('✓'):
                print_success(result)
            elif result.startswith('⚠'):
                print_warning(result)
            elif result.startswith('✗'):
                print_error(result)
            else:
                print_info(result)
    
    def _write_config_file(self, path: str, content: str) -> bool:
        """Écrit un fichier de configuration avec gestion d'erreurs"""
        if not content.strip():
            print_warning(f"Contenu vide pour {path}, fichier ignoré")
            return False
        
        try:
            file_path = self.project_root / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Sauvegarde si le fichier existe déjà
            if file_path.exists():
                backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
                file_path.rename(backup_path)
                print_info(f"Sauvegarde existante : {backup_path}")
            
            file_path.write_text(content, encoding='utf-8')
            
            # Permissions spéciales pour les scripts
            if path.startswith('scripts/') and path.endswith('.sh'):
                os.chmod(file_path, 0o755)
            elif path.endswith('.env'):
                os.chmod(file_path, 0o600)  # Fichiers sensibles
            
            print_success(f"Fichier créé : {path}")
            return True
            
        except Exception as e:
            print_error(f"Erreur écriture {path}: {str(e)}")
            return False

    def run(self):
        """Exécute la configuration complète"""
        try:
            self.welcome()
            
            steps = [
                self.step_1_server_info,
                self.step_2_database_production,
                self.step_3_security_production,
                self.step_4_performance_config,
                self.step_5_monitoring_config,
                self.step_6_backup_config,
                self.step_7_generate_config_files
            ]
            
            for i, step in enumerate(steps, 1):
                if not step():
                    print_error(f"Étape {i} échouée ou interrompue")
                    sys.exit(1)
            
            print_header("CONFIGURATION TERMINÉE")
            print_success("Environnement de production configuré avec succès !")
            print_info("Fichiers générés :")
            print("  • .env - Configuration globale")
            print("  • backend/.env - Configuration backend")
            print("  • frontend/.env - Configuration frontend")
            print("  • config/nginx.conf - Configuration Nginx")
            print("  • config/vote-secret.service - Service systemd")
            print("  • scripts/*.sh - Scripts de gestion")
            print("  • DEPLOYMENT_GUIDE.md - Guide de déploiement")
            
            print(f"\n{Colors.BLUE}Prochaine étape: Exécutez deploy_nginx.py{Colors.ENDC}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Configuration interrompue.{Colors.ENDC}")
            sys.exit(1)
        except Exception as e:
            print_error(f"Erreur: {str(e)}")
            sys.exit(1)

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Vote Secret v2.0 - Configuration Environnement Production")
        print("Usage: python3 deploy_environment.py")
        return
    
    setup = ProductionEnvironmentSetup()
    setup.run()

if __name__ == "__main__":
    main()