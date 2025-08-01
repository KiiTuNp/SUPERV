#!/usr/bin/env python3
"""
Vote Secret v2.0 - Déploiement Production Automatisé
===================================================

Script de déploiement complet pour serveur de production.
Installe tous les prérequis, configure l'environnement et met en production.

Auteur: Assistant AI
Version: 2.0.0
Date: 2025-08-01
"""

import os
import sys
import subprocess
import platform
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import importlib.util

# Configuration des couleurs et styles
class Colors:
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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_step(step_num: int, total_steps: int, description: str):
    """Affiche une étape du processus"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}[ÉTAPE {step_num}/{total_steps}] {description}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.ENDC}")

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
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

def prompt_continue(message: str = "Continuer avec l'étape suivante ?") -> bool:
    """Demande confirmation pour continuer"""
    while True:
        response = input(f"\n{Colors.BLUE}{message} [O/n]{Colors.ENDC}: ").strip().lower()
        if response in ['', 'o', 'oui', 'y', 'yes']:
            return True
        elif response in ['n', 'non', 'no']:
            return False
        print_warning("Réponse invalide. Utilisez 'o' pour oui ou 'n' pour non.")

def run_command(command: str, description: str = "", check_success: bool = True, interactive: bool = False) -> Tuple[bool, str, str]:
    """Exécute une commande système avec gestion d'erreur"""
    if description:
        print(f"{Colors.BLUE}🔄 {description}...{Colors.ENDC}")
    
    try:
        if interactive:
            # Pour les commandes interactives, afficher la commande et laisser l'utilisateur la voir
            print(f"{Colors.CYAN}Commande: {command}{Colors.ENDC}")
            process = subprocess.run(
                command,
                shell=True,
                text=True,
                timeout=600  # 10 minutes pour les commandes interactives
            )
            success = process.returncode == 0
            return success, "", ""
        else:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            success = process.returncode == 0
            
            if success:
                if description:
                    print_success(f"{description} - Terminé")
                return True, stdout, stderr
            else:
                if check_success:
                    print_error(f"{description} - Échec")
                    if stderr:
                        print(f"{Colors.FAIL}Erreur: {stderr}{Colors.ENDC}")
                    if stdout:
                        print(f"{Colors.WARNING}Sortie: {stdout}{Colors.ENDC}")
                return False, stdout, stderr
            
    except subprocess.TimeoutExpired:
        print_error(f"{description} - Timeout")
        return False, "", "Timeout"
    except Exception as e:
        print_error(f"{description} - Exception: {str(e)}")
        return False, "", str(e)

class SystemInfo:
    """Collecte les informations système"""
    
    def __init__(self):
        self.os_name = platform.system().lower()
        self.os_version = platform.release()
        self.architecture = platform.machine()
        self.python_version = sys.version_info
        self.is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        self.distro = self._get_linux_distro() if self.os_name == 'linux' else None
        
    def _get_linux_distro(self) -> Optional[str]:
        """Détecte la distribution Linux"""
        try:
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('ID='):
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
        return None
    
    def is_supported(self) -> Tuple[bool, str]:
        """Vérifie si le système est supporté"""
        if self.os_name != 'linux':
            return False, f"Système non supporté: {self.os_name}. Seul Linux est supporté."
        
        if self.distro not in ['ubuntu', 'debian', 'centos', 'rhel', 'fedora', 'rocky', 'almalinux']:
            return False, f"Distribution non supportée: {self.distro}. Supportées: Ubuntu, Debian, CentOS, RHEL, Fedora, Rocky, AlmaLinux."
        
        if self.python_version < (3, 8):
            return False, f"Python {self.python_version.major}.{self.python_version.minor} trop ancien. Python 3.8+ requis."
        
        return True, "Système compatible"

class DeploymentManager:
    """Gestionnaire principal du déploiement"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.system_info = SystemInfo()
        self.config = {}
        self.steps = [
            "Vérification du système",
            "Installation des prérequis système", 
            "Installation Python et Node.js",
            "Installation et configuration MongoDB",
            "Configuration de l'environnement",
            "Installation des dépendances de l'application",
            "Configuration du serveur web (Nginx)",
            "Création des services systemd",
            "Déploiement de l'application",
            "Tests de fonctionnement",
            "Optimisations finales"
        ]
        
    def welcome(self):
        """Affiche le message de bienvenue"""
        print_header("VOTE SECRET v2.0 - DÉPLOIEMENT PRODUCTION")
        print(f"{Colors.CYAN}🚀 Assistant de déploiement automatisé pour serveur de production{Colors.ENDC}")
        print(f"{Colors.CYAN}Ce script va installer et configurer automatiquement Vote Secret sur votre serveur.{Colors.ENDC}\n")
        
        print_info("Informations système détectées :")
        print(f"  • Système: {self.system_info.os_name.title()} {self.system_info.os_version}")
        print(f"  • Distribution: {self.system_info.distro or 'Inconnue'}")
        print(f"  • Architecture: {self.system_info.architecture}")
        print(f"  • Python: {self.system_info.python_version.major}.{self.system_info.python_version.minor}.{self.system_info.python_version.micro}")
        print(f"  • Privilèges: {'Root (sudo)' if self.system_info.is_root else 'Utilisateur standard'}")
        
        print(f"\n{Colors.WARNING}⚠️  ATTENTION: Ce script va modifier la configuration système !{Colors.ENDC}")
        print(f"{Colors.WARNING}   Assurez-vous d'avoir une sauvegarde et les droits administrateur.{Colors.ENDC}")
        
        if not prompt_continue("Êtes-vous prêt à commencer le déploiement ?"):
            print_info("Déploiement annulé par l'utilisateur.")
            sys.exit(0)
    
    def step_1_system_check(self) -> bool:
        """Étape 1: Vérification du système"""
        print_step(1, len(self.steps), "Vérification du système")
        
        # Vérification de la compatibilité
        is_supported, message = self.system_info.is_supported()
        if not is_supported:
            print_error(f"Système incompatible: {message}")
            print_info("Déploiement impossible sur ce système.")
            return False
        
        print_success(message)
        
        # Vérification des privilèges
        if not self.system_info.is_root:
            print_warning("Script exécuté sans privilèges root.")
            print_info("Certaines étapes nécessiteront 'sudo'. Assurez-vous d'avoir les droits.")
            
            # Test sudo
            success, _, _ = run_command("sudo -n true", "Test des privilèges sudo", check_success=False)
            if not success:
                print_warning("Sudo sans mot de passe non configuré.")
                print_info("Vous devrez saisir votre mot de passe pendant l'installation.")
        
        # Vérification de l'espace disque
        success, stdout, _ = run_command("df -h /", "Vérification espace disque", check_success=False)
        if success:
            lines = stdout.split('\n')
            if len(lines) > 1:
                disk_info = lines[1].split()
                if len(disk_info) > 3:
                    available = disk_info[3]
                    print_info(f"Espace disque disponible: {available}")
                    
                    # Extraire la valeur numérique (approximative)
                    try:
                        size_str = available.replace('G', '').replace('M', '').replace('K', '')
                        if 'G' in available:
                            size_gb = float(size_str)
                            if size_gb < 5:
                                print_warning(f"Espace disque faible: {available}. Recommandé: 5GB+")
                        elif 'M' in available:
                            print_warning(f"Espace disque très faible: {available}. Recommandé: 5GB+")
                    except:
                        pass
        
        # Vérification de la mémoire
        success, stdout, _ = run_command("free -h", "Vérification mémoire RAM", check_success=False)
        if success:
            lines = stdout.split('\n')
            for line in lines:
                if 'Mem:' in line:
                    mem_info = line.split()
                    if len(mem_info) > 1:
                        total_mem = mem_info[1]
                        print_info(f"Mémoire RAM totale: {total_mem}")
                        break
        
        # Vérification des ports
        ports_to_check = [80, 443, 3000, 8001, 27017]
        print_info("Vérification des ports requis...")
        
        for port in ports_to_check:
            success, stdout, _ = run_command(f"netstat -tuln | grep :{port}", f"Port {port}", check_success=False)
            if success and stdout:
                print_warning(f"Port {port} déjà utilisé. Cela pourrait causer des conflits.")
        
        print_success("Vérification système terminée")
        return prompt_continue()
    
    def step_2_system_prerequisites(self) -> bool:
        """Étape 2: Installation des prérequis système"""
        print_step(2, len(self.steps), "Installation des prérequis système")
        
        # Mise à jour du système
        if self.system_info.distro in ['ubuntu', 'debian']:
            commands = [
                ("sudo apt update", "Mise à jour de la liste des paquets"),
                ("sudo apt upgrade -y", "Mise à jour du système"),
                ("sudo apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates lsb-release", "Installation des outils de base")
            ]
        elif self.system_info.distro in ['centos', 'rhel', 'rocky', 'almalinux']:
            commands = [
                ("sudo yum update -y", "Mise à jour du système"),
                ("sudo yum install -y curl wget gnupg2 yum-utils", "Installation des outils de base")
            ]
        elif self.system_info.distro == 'fedora':
            commands = [
                ("sudo dnf update -y", "Mise à jour du système"),  
                ("sudo dnf install -y curl wget gnupg2", "Installation des outils de base")
            ]
        else:
            print_error(f"Distribution {self.system_info.distro} non supportée pour cette étape")
            return False
        
        for command, description in commands:
            success, _, _ = run_command(command, description)
            if not success:
                print_error(f"Échec: {description}")
                if not prompt_continue("Ignorer cette erreur et continuer ?"):
                    return False
        
        print_success("Prérequis système installés")
        return prompt_continue()
    
    def step_3_python_nodejs(self) -> bool:
        """Étape 3: Installation Python et Node.js"""
        print_step(3, len(self.steps), "Installation Python et Node.js")
        
        # Vérification Python actuel
        success, stdout, _ = run_command("python3 --version", "Vérification Python3")
        if success:
            print_info(f"Python3 détecté: {stdout}")
        
        # Installation Python 3.11+ si nécessaire
        if self.system_info.python_version < (3, 11):
            print_warning("Python 3.11+ recommandé pour Vote Secret")
            
            if self.system_info.distro in ['ubuntu', 'debian']:
                commands = [
                    ("sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip", "Installation Python 3.11")
                ]
            else:
                print_info("Installation manuelle de Python 3.11+ recommandée sur cette distribution")
        
        # Installation pip et outils Python
        python_commands = [
            ("sudo apt install -y python3-pip python3-venv python3-dev build-essential", "Installation outils Python") if self.system_info.distro in ['ubuntu', 'debian'] else
            ("sudo yum install -y python3-pip python3-devel gcc gcc-c++ make", "Installation outils Python")
        ]
        
        for command, description in python_commands:
            success, _, _ = run_command(command, description)
            if not success:
                print_warning(f"Erreur: {description}")
        
        # Installation Node.js 20+
        print_info("Installation de Node.js 20.x...")
        
        if self.system_info.distro in ['ubuntu', 'debian']:
            node_commands = [
                ("curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -", "Ajout du dépôt NodeSource"),
                ("sudo apt install -y nodejs", "Installation Node.js 20.x")
            ]
        elif self.system_info.distro in ['centos', 'rhel', 'rocky', 'almalinux']:
            node_commands = [
                ("curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -", "Ajout du dépôt NodeSource"),
                ("sudo yum install -y nodejs", "Installation Node.js 20.x")
            ]
        elif self.system_info.distro == 'fedora':
            node_commands = [
                ("curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -", "Ajout du dépôt NodeSource"),
                ("sudo dnf install -y nodejs", "Installation Node.js 20.x")
            ]
        
        for command, description in node_commands:
            success, _, _ = run_command(command, description)
            if not success:
                print_error(f"Échec: {description}")
                return False
        
        # Installation Yarn
        success, _, _ = run_command("sudo npm install -g yarn", "Installation Yarn")
        if not success:
            print_warning("Erreur installation Yarn, mais peut continuer avec npm")
        
        # Vérification des versions installées
        success, stdout, _ = run_command("node --version", "Vérification Node.js")
        if success:
            print_success(f"Node.js installé: {stdout}")
        
        success, stdout, _ = run_command("npm --version", "Vérification npm")
        if success:
            print_success(f"npm installé: {stdout}")
        
        success, stdout, _ = run_command("yarn --version", "Vérification Yarn", check_success=False)
        if success:
            print_success(f"Yarn installé: {stdout}")
        
        return prompt_continue()
    
    def step_4_mongodb(self) -> bool:
        """Étape 4: Installation et configuration MongoDB"""
        print_step(4, len(self.steps), "Installation et configuration MongoDB")
        
        print_info("Installation de MongoDB 8.0...")
        
        if self.system_info.distro in ['ubuntu', 'debian']:
            mongo_commands = [
                ("curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor", "Ajout de la clé GPG MongoDB"),
                (f"echo 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/{self.system_info.distro} $(lsb_release -cs)/mongodb-org/8.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list", "Ajout du dépôt MongoDB"),
                ("sudo apt update", "Mise à jour des sources"),
                ("sudo apt install -y mongodb-org", "Installation MongoDB")
            ]
        elif self.system_info.distro in ['centos', 'rhel', 'rocky', 'almalinux']:
            # Créer le fichier repo MongoDB
            repo_content = """[mongodb-org-8.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/8.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-8.0.asc"""
            
            success, _, _ = run_command(f"echo '{repo_content}' | sudo tee /etc/yum.repos.d/mongodb-org-8.0.repo", "Création du fichier repo MongoDB")
            if not success:
                print_error("Erreur création du repo MongoDB")
                return False
            
            mongo_commands = [
                ("sudo yum install -y mongodb-org", "Installation MongoDB")
            ]
        elif self.system_info.distro == 'fedora':
            mongo_commands = [
                ("sudo dnf install -y mongodb mongodb-server", "Installation MongoDB")
            ]
        
        for command, description in mongo_commands:
            success, _, _ = run_command(command, description)
            if not success:
                print_error(f"Échec: {description}")
                print_info("Vous pouvez installer MongoDB manuellement ou utiliser MongoDB Atlas")
                if not prompt_continue("Continuer sans MongoDB local ?"):
                    return False
                break
        else:
            # Configuration et démarrage MongoDB
            config_commands = [
                ("sudo systemctl start mongod", "Démarrage MongoDB"),
                ("sudo systemctl enable mongod", "Activation au démarrage MongoDB"),
                ("sudo systemctl status mongod", "Vérification statut MongoDB")
            ]
            
            for command, description in config_commands:
                success, _, _ = run_command(command, description, check_success=False)
                if success and "status" in command:
                    print_success("MongoDB démarré et actif")
                elif not success and "start" in command:
                    print_warning("Erreur démarrage MongoDB - vérification manuelle requise")
        
        return prompt_continue()
    
    def run(self):
        """Exécute le processus complet de déploiement"""
        try:
            self.welcome()
            
            # Exécution séquentielle des étapes
            steps_methods = [
                self.step_1_system_check,
                self.step_2_system_prerequisites,
                self.step_3_python_nodejs,
                self.step_4_mongodb,
                # Les autres étapes seront ajoutées dans les scripts séparés
            ]
            
            for i, step_method in enumerate(steps_methods, 1):
                if not step_method():
                    print_error(f"Étape {i} échouée ou interrompue par l'utilisateur")
                    print_info("Déploiement arrêté")
                    sys.exit(1)
            
            print_header("SUITE DU DÉPLOIEMENT")
            print(f"{Colors.GREEN}✅ Prérequis système installés avec succès !{Colors.ENDC}")
            print(f"{Colors.CYAN}Les étapes suivantes seront disponibles dans les scripts complémentaires :{Colors.ENDC}")
            print("  • deploy_environment.py - Configuration environnement")
            print("  • deploy_nginx.py - Configuration serveur web")
            print("  • deploy_systemd.py - Services système")
            print("  • deploy_application.py - Déploiement application")
            print("  • deploy_optimize.py - Optimisations finales")
            
            print(f"\n{Colors.BLUE}Exécutez ces scripts dans l'ordre pour terminer le déploiement.{Colors.ENDC}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Déploiement interrompu par l'utilisateur.{Colors.ENDC}")
            sys.exit(1)
        except Exception as e:
            print_error(f"Erreur inattendue: {str(e)}")
            sys.exit(1)

def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Vote Secret v2.0 - Assistant de Déploiement Production")
        print("Usage: python3 deploy.py")
        print("\nCe script installe automatiquement Vote Secret sur un serveur de production.")
        print("Il configure tous les prérequis système et prépare l'environnement.")
        return
    
    if os.geteuid() == 0:
        print_error("Ne pas exécuter ce script en tant que root !")
        print_info("Exécutez avec un utilisateur sudo : python3 deploy.py")
        sys.exit(1)
    
    deployment = DeploymentManager()
    deployment.run()

if __name__ == "__main__":
    main()