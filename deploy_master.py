#!/usr/bin/env python3
"""
Vote Secret v2.0 - Déploiement Production Maître
===============================================

Script maître qui orchestre tout le processus de déploiement en production.
Lance séquentiellement tous les scripts de déploiement avec gestion d'erreurs.

Auteur: Assistant AI
Version: 2.0.0
Date: 2025-08-01
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Tuple

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
        print_warning("Réponse invalide.")

class MasterDeployment:
    """Orchestrateur principal du déploiement"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_scripts = [
            {
                'script': 'deploy.py',
                'name': 'Installation Prérequis Système',
                'description': 'Installation Python, Node.js, MongoDB et prérequis système',
                'required': True
            },
            {
                'script': 'deploy_environment.py', 
                'name': 'Configuration Environnement',
                'description': 'Configuration des variables d\'environnement et paramètres',
                'required': True
            },
            {
                'script': 'deploy_nginx.py',
                'name': 'Configuration Serveur Web',
                'description': 'Installation et configuration Nginx avec SSL',
                'required': True
            },
            {
                'script': 'deploy_final.py',
                'name': 'Déploiement Final',
                'description': 'Services systemd et mise en production',
                'required': True
            }
        ]
        self.completed_steps = []
        self.start_time = time.time()
    
    def welcome(self):
        print_header("VOTE SECRET v2.0 - DÉPLOIEMENT PRODUCTION MAÎTRE")
        print(f"{Colors.CYAN}🚀 Assistant de déploiement automatisé complet{Colors.ENDC}")
        print(f"{Colors.CYAN}Ce script orchestre tout le processus de déploiement en production.{Colors.ENDC}\n")
        
        print_info("Étapes du déploiement :")
        for i, step in enumerate(self.deployment_scripts, 1):
            required = "REQUIS" if step['required'] else "OPTIONNEL"
            print(f"  {i}. {step['name']} ({required})")
            print(f"     {step['description']}")
        
        print(f"\n{Colors.WARNING}⚠️  ATTENTION:{Colors.ENDC}")
        print("• Ce processus peut prendre 30-60 minutes")
        print("• Assurez-vous d'avoir les droits sudo")
        print("• Gardez une connexion stable pendant tout le processus")
        print("• Préparez les informations suivantes :")
        print("  - Nom de domaine pointant vers ce serveur")
        print("  - Email pour les certificats SSL")
        print("  - Configuration de base de données souhaitée")
        
        if not prompt_continue("Êtes-vous prêt à commencer le déploiement complet ?"):
            print_info("Déploiement annulé par l'utilisateur.")
            sys.exit(0)

    def run_deployment_script(self, script_info: dict) -> bool:
        """Exécute un script de déploiement"""
        script_name = script_info['script']
        script_path = self.project_root / script_name
        
        if not script_path.exists():
            print_error(f"Script {script_name} non trouvé")
            return False
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}🔄 Lancement: {script_info['name']}{Colors.ENDC}")
        print(f"{Colors.CYAN}Description: {script_info['description']}{Colors.ENDC}")
        print(f"{Colors.CYAN}Script: {script_name}{Colors.ENDC}")
        
        if not prompt_continue(f"Lancer {script_info['name']} ?"):
            if script_info['required']:
                print_error("Cette étape est requise pour le déploiement")
                return False
            else:
                print_warning("Étape optionnelle ignorée")
                return True
        
        try:
            # Exécution du script
            process = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                text=True,
                timeout=3600  # 1 heure maximum par script
            )
            
            if process.returncode == 0:
                print_success(f"{script_info['name']} - Terminé avec succès")
                self.completed_steps.append(script_info['name'])
                return True
            else:
                print_error(f"{script_info['name']} - Échec (code: {process.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            print_error(f"{script_info['name']} - Timeout (>1 heure)")
            return False
        except KeyboardInterrupt:
            print_warning(f"{script_info['name']} - Interrompu par l'utilisateur")
            raise
        except Exception as e:
            print_error(f"{script_info['name']} - Exception: {str(e)}")
            return False

    def handle_failure(self, failed_step: dict, step_number: int) -> bool:
        """Gère les échecs d'étapes"""
        print_header("ÉCHEC D'ÉTAPE DÉTECTÉ")
        print_error(f"L'étape {step_number} a échoué: {failed_step['name']}")
        
        print(f"\n{Colors.CYAN}Options disponibles:{Colors.ENDC}")
        print("1. Réessayer cette étape")
        print("2. Ignorer et continuer (risqué)")
        print("3. Arrêter le déploiement")
        print("4. Afficher les logs de dépannage")
        
        while True:
            choice = input(f"\n{Colors.BLUE}Votre choix [1-4]{Colors.ENDC}: ").strip()
            
            if choice == "1":
                print_info("Nouvelle tentative...")
                return self.run_deployment_script(failed_step)
            elif choice == "2":
                if failed_step['required']:
                    print_error("Cette étape est requise, impossible d'ignorer")
                    continue
                else:
                    print_warning("Étape ignorée - le déploiement peut être incomplet")
                    return True
            elif choice == "3":
                print_info("Déploiement arrêté par l'utilisateur")
                return False
            elif choice == "4":
                self.show_troubleshooting_info()
                continue
            else:
                print_warning("Choix invalide")

    def show_troubleshooting_info(self):
        """Affiche les informations de dépannage"""
        print(f"\n{Colors.CYAN}=== INFORMATIONS DE DÉPANNAGE ==={Colors.ENDC}")
        
        # Informations système
        print(f"\n{Colors.BLUE}Système:{Colors.ENDC}")
        os.system("uname -a")
        
        # Espace disque
        print(f"\n{Colors.BLUE}Espace disque:{Colors.ENDC}")
        os.system("df -h /")
        
        # Mémoire
        print(f"\n{Colors.BLUE}Mémoire:{Colors.ENDC}")
        os.system("free -h")
        
        # Services
        print(f"\n{Colors.BLUE}Services critiques:{Colors.ENDC}")
        services = ['nginx', 'mongod', 'vote-secret']
        for service in services:
            os.system(f"systemctl is-active {service} 2>/dev/null && echo '{service}: actif' || echo '{service}: inactif'")
        
        # Logs récents
        print(f"\n{Colors.BLUE}Logs système récents:{Colors.ENDC}")
        os.system("journalctl --since '10 minutes ago' -p err --no-pager -n 10")
        
        print(f"\n{Colors.CYAN}Pour plus d'aide:{Colors.ENDC}")
        print("• Vérifiez les logs détaillés: journalctl -u vote-secret -f")
        print("• Consultez: /opt/vote-secret/DEPLOYMENT_GUIDE.md")
        print("• Testez manuellement chaque composant")

    def show_progress_summary(self):
        """Affiche le résumé de progression"""
        total_steps = len(self.deployment_scripts)
        completed = len(self.completed_steps)
        
        print(f"\n{Colors.CYAN}=== PROGRESSION DU DÉPLOIEMENT ==={Colors.ENDC}")
        print(f"Étapes terminées: {completed}/{total_steps}")
        
        if self.completed_steps:
            print(f"\n{Colors.GREEN}✅ Étapes réussies:{Colors.ENDC}")
            for step in self.completed_steps:
                print(f"   • {step}")
        
        remaining_steps = [s['name'] for s in self.deployment_scripts[completed:]]
        if remaining_steps:
            print(f"\n{Colors.BLUE}⏳ Étapes restantes:{Colors.ENDC}")
            for step in remaining_steps:
                print(f"   • {step}")

    def run(self):
        """Exécute le déploiement complet"""
        try:
            self.welcome()
            
            # Exécution séquentielle de tous les scripts
            for i, script_info in enumerate(self.deployment_scripts, 1):
                print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
                print(f"{Colors.HEADER}ÉTAPE {i}/{len(self.deployment_scripts)}: {script_info['name'].upper()}{Colors.ENDC}")
                print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
                
                success = self.run_deployment_script(script_info)
                
                if not success:
                    # Gestion de l'échec
                    if not self.handle_failure(script_info, i):
                        print_error("Déploiement abandonné")
                        self.show_progress_summary()
                        sys.exit(1)
                
                # Petit délai entre les étapes
                time.sleep(2)
            
            # Déploiement terminé avec succès
            self.show_deployment_success()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Déploiement interrompu par l'utilisateur{Colors.ENDC}")
            self.show_progress_summary()
            sys.exit(1)
        except Exception as e:
            print_error(f"Erreur inattendue: {str(e)}")
            self.show_progress_summary()
            sys.exit(1)

    def show_deployment_success(self):
        """Affiche le message de succès final"""
        duration = int(time.time() - self.start_time)
        minutes = duration // 60
        seconds = duration % 60
        
        print_header("🎉 DÉPLOIEMENT COMPLET TERMINÉ ! 🎉")
        
        print(f"{Colors.GREEN}{Colors.BOLD}Vote Secret v2.0 a été déployé avec succès !{Colors.ENDC}")
        print(f"{Colors.CYAN}Durée totale: {minutes}m {seconds}s{Colors.ENDC}\n")
        
        # Vérification finale des services
        print(f"{Colors.CYAN}🔍 VÉRIFICATION FINALE:{Colors.ENDC}")
        
        try:
            # Lecture de la configuration
            config = {}
            env_file = self.project_root / '.env'
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            config[key] = value
            
            domain = config.get('DOMAIN', 'localhost')
            frontend_url = config.get('FRONTEND_URL', f'http://{domain}')
            
            print(f"🌐 Application: {frontend_url}")
            print(f"🖥️  Serveur: {domain}")
            
        except Exception:
            print("Configuration non disponible")
        
        print(f"\n{Colors.CYAN}📋 ÉTAPES POST-DÉPLOIEMENT:{Colors.ENDC}")
        print("1. Testez l'application dans votre navigateur")
        print("2. Vérifiez les logs: /usr/local/bin/monitor.sh")
        print("3. Configurez la sauvegarde automatique")
        print("4. Documentez l'accès pour votre équipe")
        
        print(f"\n{Colors.CYAN}🛠️  GESTION QUOTIDIENNE:{Colors.ENDC}")
        print("• Status: /usr/local/bin/manage.sh status")
        print("• Logs: /usr/local/bin/manage.sh logs")
        print("• Sauvegarde: /usr/local/bin/backup.sh")
        print("• Monitoring: /usr/local/bin/monitor.sh")
        
        print(f"\n{Colors.GREEN}🎯 Vote Secret v2.0 est maintenant en production !{Colors.ENDC}")
        print(f"{Colors.GREEN}Tous les composants sont déployés et opérationnels.{Colors.ENDC}")

def main():
    """Point d'entrée principal"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Vote Secret v2.0 - Déploiement Production Maître")
        print("Usage: python3 deploy_master.py")
        print("\nCe script orchestre tout le processus de déploiement automatique.")
        print("Il lance séquentiellement tous les scripts de déploiement nécessaires.")
        return
    
    # Vérifications préliminaires
    if os.geteuid() == 0:
        print_error("Ne pas exécuter ce script en tant que root !")
        print_info("Exécutez avec un utilisateur sudo : python3 deploy_master.py")
        sys.exit(1)
    
    # Vérification des fichiers requis
    required_files = ['deploy.py', 'deploy_environment.py', 'deploy_nginx.py', 'deploy_final.py']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print_error("Fichiers de déploiement manquants:")
        for file in missing_files:
            print(f"  • {file}")
        sys.exit(1)
    
    # Lancement du déploiement maître
    deployment = MasterDeployment()
    deployment.run()

if __name__ == "__main__":
    main()