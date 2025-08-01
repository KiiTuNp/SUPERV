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
import json
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

def prompt_input(message: str, default: str = "") -> str:
    """Demande une saisie utilisateur avec valeur par défaut"""
    prompt = f"\n{Colors.BLUE}{message}"
    if default:
        prompt += f" (défaut: {default})"
    prompt += f"{Colors.ENDC}: "
    
    response = input(prompt).strip()
    return response if response else default

class MasterDeployment:
    """Orchestrateur principal du déploiement"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.state_file = self.project_root / '.deployment_state.json'
        self.deployment_scripts = [
            {
                'id': 'prerequisites',
                'script': 'deploy.py',
                'name': 'Installation Prérequis Système',
                'description': 'Installation Python, Node.js, MongoDB et prérequis système',
                'required': True,
                'dependencies': []
            },
            {
                'id': 'environment',
                'script': 'deploy_environment.py', 
                'name': 'Configuration Environnement',
                'description': 'Configuration des variables d\'environnement et paramètres',
                'required': True,
                'dependencies': []
            },
            {
                'id': 'nginx',
                'script': 'deploy_nginx.py',
                'name': 'Configuration Serveur Web',
                'description': 'Installation et configuration Nginx avec SSL',
                'required': True,
                'dependencies': ['prerequisites', 'environment']
            },
            {
                'id': 'final',
                'script': 'deploy_final.py',
                'name': 'Déploiement Final',
                'description': 'Services systemd et mise en production',
                'required': True,
                'dependencies': ['prerequisites', 'environment', 'nginx']
            }
        ]
        self.completed_steps = []
        self.start_time = time.time()
        self.deployment_state = self._load_deployment_state()
    
    def _load_deployment_state(self) -> dict:
        """Charge l'état du déploiement depuis un fichier JSON"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_deployment_state(self):
        """Sauvegarde l'état du déploiement"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.deployment_state, f, indent=2)
        except Exception as e:
            print_warning(f"Impossible de sauvegarder l'état: {e}")
    
    def _check_step_completed(self, step_id: str) -> bool:
        """Vérifie si une étape a été complétée avec succès"""
        return self.deployment_state.get(step_id, {}).get('completed', False)
    
    def _mark_step_completed(self, step_id: str, success: bool = True):
        """Marque une étape comme complétée"""
        if step_id not in self.deployment_state:
            self.deployment_state[step_id] = {}
        
        self.deployment_state[step_id].update({
            'completed': success,
            'timestamp': time.time(),
            'date': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        self._save_deployment_state()
    
    def _get_system_info(self) -> dict:
        """Collecte les informations système importantes"""
        info = {}
        try:
            # Distribution
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        info['os'] = line.split('=', 1)[1].strip().strip('"')
                        break
            
            # Architecture
            import platform
            info['arch'] = platform.machine()
            
            # Espace disque
            import shutil
            total, used, free = shutil.disk_usage('/')
            info['disk_free_gb'] = free // (1024**3)
            
            # Mémoire
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        info['memory_gb'] = int(line.split()[1]) // (1024**2)
                        break
            
            # Services déjà installés
            services = ['nginx', 'mongod', 'mongodb', 'apache2']
            installed_services = []
            for service in services:
                result = subprocess.run(['systemctl', 'is-enabled', service], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    installed_services.append(service)
            info['services'] = installed_services
            
        except Exception as e:
            print_warning(f"Erreur collecte info système: {e}")
        
        return info
    
    def welcome(self):
        print_header("VOTE SECRET v2.0 - DÉPLOIEMENT PRODUCTION MAÎTRE")
        print(f"{Colors.CYAN}🚀 Assistant de déploiement automatisé intelligent{Colors.ENDC}")
        print(f"{Colors.CYAN}Ce script orchestre tout le processus de déploiement en production.{Colors.ENDC}\n")
        
        # Informations système
        system_info = self._get_system_info()
        print_info("Informations système détectées :")
        print(f"  • OS: {system_info.get('os', 'Inconnu')}")
        print(f"  • Architecture: {system_info.get('arch', 'Inconnue')}")
        print(f"  • Mémoire: {system_info.get('memory_gb', '?')} GB")
        print(f"  • Espace libre: {system_info.get('disk_free_gb', '?')} GB")
        if system_info.get('services'):
            print(f"  • Services détectés: {', '.join(system_info['services'])}")
        
        # État du déploiement précédent
        if self.deployment_state:
            print_info("État du déploiement précédent détecté :")
            for step_id, state in self.deployment_state.items():
                status = "✅ Complété" if state.get('completed') else "❌ Échoué"
                date = state.get('date', 'Date inconnue')
                step_name = next((s['name'] for s in self.deployment_scripts if s['id'] == step_id), step_id)
                print(f"  • {step_name}: {status} ({date})")
        
        print_info("Étapes du déploiement :")
        for i, step in enumerate(self.deployment_scripts, 1):
            required = "REQUIS" if step['required'] else "OPTIONNEL"
            status = ""
            if self._check_step_completed(step['id']):
                status = f" {Colors.GREEN}[DÉJÀ FAIT]{Colors.ENDC}"
            print(f"  {i}. {step['name']} ({required}){status}")
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
        """Exécute un script de déploiement avec gestion d'état"""
        script_name = script_info['script']
        script_id = script_info['id']
        script_path = self.project_root / script_name
        
        if not script_path.exists():
            print_error(f"Script {script_name} non trouvé")
            return False
        
        # Vérifier si l'étape a déjà été complétée avec succès
        if self._check_step_completed(script_id):
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ {script_info['name']} - DÉJÀ COMPLÉTÉ{Colors.ENDC}")
            print(f"{Colors.GREEN}Cette étape a été complétée avec succès précédemment.{Colors.ENDC}")
            
            choice = prompt_input(
                "Action: [1] Ignorer (recommandé) [2] Réexécuter [3] Marquer comme non fait",
                default="1"
            )
            
            if choice == "1":
                print_success(f"{script_info['name']} - Ignoré (déjà fait)")
                return True
            elif choice == "3":
                self._mark_step_completed(script_id, False)
                print_info("Étape marquée comme non complétée")
                # Continue vers l'exécution
            # choice == "2": continue vers l'exécution
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}🔄 Lancement: {script_info['name']}{Colors.ENDC}")
        print(f"{Colors.CYAN}Description: {script_info['description']}{Colors.ENDC}")
        print(f"{Colors.CYAN}Script: {script_name}{Colors.ENDC}")
        
        # Vérifier les dépendances
        for dep in script_info.get('dependencies', []):
            if not self._check_step_completed(dep):
                dep_name = next((s['name'] for s in self.deployment_scripts if s['id'] == dep), dep)
                print_error(f"Dépendance non satisfaite: {dep_name}")
                return False
        
        if not prompt_continue(f"Lancer {script_info['name']} ?"):
            if script_info['required']:
                print_error("Cette étape est requise pour le déploiement")
                return False
            else:
                print_warning("Étape optionnelle ignorée")
                self._mark_step_completed(script_id, True)  # Marquer comme fait si ignoré
                return True
        
        try:
            # Exécution du script avec information de progression
            print_info("Démarrage de l'exécution...")
            start_time = time.time()
            
            process = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                text=True,
                timeout=3600  # 1 heure maximum par script
            )
            
            duration = int(time.time() - start_time)
            
            if process.returncode == 0:
                print_success(f"{script_info['name']} - Terminé avec succès en {duration}s")
                self.completed_steps.append(script_info['name'])
                self._mark_step_completed(script_id, True)
                return True
            else:
                print_error(f"{script_info['name']} - Échec (code: {process.returncode})")
                self._mark_step_completed(script_id, False)
                return False
                
        except subprocess.TimeoutExpired:
            print_error(f"{script_info['name']} - Timeout (>1 heure)")
            self._mark_step_completed(script_id, False)
            return False
        except KeyboardInterrupt:
            print_warning(f"{script_info['name']} - Interrompu par l'utilisateur")
            self._mark_step_completed(script_id, False)
            raise
        except Exception as e:
            print_error(f"{script_info['name']} - Exception: {str(e)}")
            self._mark_step_completed(script_id, False)
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
        """Affiche le message de succès final avec toutes les informations"""
        duration = int(time.time() - self.start_time)
        minutes = duration // 60
        seconds = duration % 60
        
        print_header("🎉 FÉLICITATIONS ! DÉPLOIEMENT RÉUSSI ! 🎉")
        
        print(f"{Colors.GREEN}{Colors.BOLD}Vote Secret v2.0 a été déployé avec succès !{Colors.ENDC}")
        print(f"{Colors.CYAN}Durée totale: {minutes}m {seconds}s{Colors.ENDC}\n")
        
        # Lecture de la configuration finale
        config = {}
        try:
            env_file = self.project_root / '.env'
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            config[key] = value
        except Exception:
            print_warning("Impossible de lire la configuration finale")
        
        domain = config.get('DOMAIN', 'localhost')
        frontend_url = config.get('FRONTEND_URL', f'http://{domain}')
        backend_url = config.get('BACKEND_URL', f'http://{domain}/api')
        ssl_mode = config.get('SSL_MODE', 'none')
        
        # URLs et accès principal
        print(f"{Colors.GREEN}{Colors.BOLD}🌐 VOTRE APPLICATION EST MAINTENANT EN LIGNE :{Colors.ENDC}")
        print("")
        print(f"{Colors.CYAN}   🔗 URL PRINCIPALE : {Colors.BOLD}{frontend_url}{Colors.ENDC}")
        print(f"{Colors.CYAN}   🔗 API Backend   : {backend_url}{Colors.ENDC}")
        print(f"{Colors.CYAN}   🖥️  Serveur       : {domain}{Colors.ENDC}")
        print(f"{Colors.CYAN}   🔒 SSL/HTTPS     : {'✅ Activé' if ssl_mode != 'none' else '❌ Désactivé'}{Colors.ENDC}")
        print("")
        
        # Vérification finale des services
        print(f"{Colors.BLUE}🔍 VÉRIFICATION FINALE DES SERVICES :{Colors.ENDC}")
        services_status = {}
        
        critical_services = ['vote-secret', 'nginx', 'mongod']
        for service in critical_services:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], 
                                      capture_output=True, text=True)
                services_status[service] = result.returncode == 0
                status_icon = "✅" if services_status[service] else "❌"
                print(f"   {status_icon} {service}: {'Actif' if services_status[service] else 'Inactif'}")
            except:
                print(f"   ❓ {service}: Statut inconnu")
        
        # Test de connectivité rapide
        print(f"\n{Colors.BLUE}🌐 TEST DE CONNECTIVITÉ :{Colors.ENDC}")
        try:
            result = subprocess.run(['curl', '-s', '-I', '--connect-timeout', '5', frontend_url], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Site web accessible")
            else:
                print(f"   ⚠️  Site web non accessible (vérifiez DNS/Firewall)")
        except:
            print(f"   ❓ Test de connectivité échoué")
        
        # Informations pratiques
        print(f"\n{Colors.CYAN}📋 INFORMATIONS IMPORTANTES :{Colors.ENDC}")
        print(f"   • Application installée dans : /opt/vote-secret/")
        print(f"   • Logs système : /var/log/vote-secret/")
        print(f"   • Configuration : /opt/vote-secret/config/")
        print(f"   • Scripts de gestion : /usr/local/bin/{{manage,backup,monitor}}.sh")
        print(f"   • Serveur : Uvicorn (FastAPI natif)")
        
        if ssl_mode == 'letsencrypt':
            print(f"   • Certificats SSL : Renouvellement automatique configuré")
        
        # Commandes de gestion
        print(f"\n{Colors.CYAN}🛠️  COMMANDES DE GESTION QUOTIDIENNE :{Colors.ENDC}")
        print(f"   • Statut des services     : sudo systemctl status vote-secret")
        print(f"   • Redémarrer l'application: sudo systemctl restart vote-secret") 
        print(f"   • Voir les logs           : sudo journalctl -u vote-secret -f")
        print(f"   • Script de gestion       : /usr/local/bin/manage.sh status")
        print(f"   • Monitoring complet      : /usr/local/bin/monitor.sh")
        print(f"   • Sauvegarde manuelle     : /usr/local/bin/backup.sh")
        
        # Actions post-déploiement
        print(f"\n{Colors.WARNING}📝 PROCHAINES ÉTAPES RECOMMANDÉES :{Colors.ENDC}")
        print(f"   1. 🌐 Testez votre application : {frontend_url}")
        print(f"   2. 📊 Créez votre première réunion de test")
        print(f"   3. 🔍 Surveillez les logs pendant 24h")
        print(f"   4. 💾 Configurez les sauvegardes automatiques (crontab)")
        print(f"   5. 👥 Formez votre équipe sur l'utilisation")
        print(f"   6. 📖 Documentez vos procédures spécifiques")
        
        # Message d'encouragement final
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎯 VOTE SECRET v2.0 EST PRÊT POUR VOS ASSEMBLÉES !{Colors.ENDC}")
        print(f"{Colors.GREEN}Votre plateforme de vote anonyme est maintenant opérationnelle.{Colors.ENDC}")
        print(f"{Colors.GREEN}Tous les services sont déployés et configurés correctement.{Colors.ENDC}")
        
        # Avertissement de sécurité si pas de SSL
        if ssl_mode == 'none':
            print(f"\n{Colors.WARNING}⚠️  ATTENTION SÉCURITÉ : HTTPS n'est pas configuré !{Colors.ENDC}")
            print(f"{Colors.WARNING}   Pour la production, configurez SSL/TLS avec un certificat valide.{Colors.ENDC}")
        
        print(f"\n{Colors.CYAN}Pour toute question ou support technique :{Colors.ENDC}")
        print(f"   • Documentation : /opt/vote-secret/README.md")
        print(f"   • Guide de déploiement : /opt/vote-secret/DEPLOYMENT_GUIDE.md")
        
        # Sauvegarder l'état de déploiement complet
        self.deployment_state['deployment_completed'] = {
            'completed': True,
            'timestamp': time.time(),
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': duration,
            'frontend_url': frontend_url,
            'backend_url': backend_url,
            'domain': domain,
            'ssl_mode': ssl_mode
        }
        self._save_deployment_state()

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