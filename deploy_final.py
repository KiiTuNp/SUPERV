#!/usr/bin/env python3
"""
Vote Secret v2.0 - Déploiement Final et Services Systemd
======================================================

Script final de déploiement qui configure les services systemd,
déploie l'application et effectue les optimisations finales.

Auteur: Assistant AI
Version: 2.0.0
Date: 2025-08-01
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path
from typing import Tuple, List

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
        print_warning("Réponse invalide.")

def run_command(command: str, description: str = "", check_success: bool = True, interactive: bool = False) -> Tuple[bool, str, str]:
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
                timeout=600  # 10 minutes pour les builds
            )
            
            success = process.returncode == 0
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            
            if success:
                if description:
                    print_success(f"{description} - Terminé")
            else:
                if check_success:
                    print_error(f"{description} - Échec")
                    if stderr:
                        print(f"{Colors.FAIL}Erreur: {stderr}{Colors.ENDC}")
            
            return success, stdout, stderr
        
    except subprocess.TimeoutExpired:
        print_error(f"{description} - Timeout")
        return False, "", "Timeout"
    except Exception as e:
        print_error(f"{description} - Exception: {str(e)}")
        return False, "", str(e)

class FinalDeployment:
    """Déploiement final et configuration des services"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config = self._load_config()
        self.total_steps = 8
        self.deployment_path = Path("/opt/vote-secret")
        
    def _load_config(self) -> dict:
        """Charge la configuration depuis .env"""
        config = {}
        env_file = self.project_root / '.env'
        
        if not env_file.exists():
            print_error("Fichier .env non trouvé. Exécutez d'abord deploy_environment.py")
            sys.exit(1)
        
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
        
        return config
    
    def welcome(self):
        print_header("DÉPLOIEMENT FINAL ET SERVICES SYSTEMD")
        print(f"{Colors.CYAN}Déploiement final de Vote Secret en production{Colors.ENDC}")
        print(f"{Colors.CYAN}Domaine: {self.config.get('DOMAIN', 'Non défini')}{Colors.ENDC}")
        print(f"{Colors.CYAN}Répertoire de déploiement: {self.deployment_path}{Colors.ENDC}\n")
        
        print_warning("Cette étape va:")
        print("  • Créer l'utilisateur système vote-secret")
        print("  • Déployer l'application dans /opt/vote-secret")
        print("  • Configurer les services systemd")
        print("  • Installer les dépendances")
        print("  • Effectuer les tests de production")

    def step_1_create_system_user(self) -> bool:
        """Création de l'utilisateur système"""
        print_step(1, self.total_steps, "Création utilisateur système")
        
        # Vérifier si l'utilisateur existe déjà
        success, _, _ = run_command("id vote-secret", "Vérification utilisateur", check_success=False)
        if success:
            print_success("Utilisateur vote-secret existe déjà")
        else:
            # Créer l'utilisateur système
            success, _, _ = run_command(
                "sudo useradd -r -s /bin/false -d /opt/vote-secret -c 'Vote Secret Application' vote-secret",
                "Création utilisateur vote-secret"
            )
            if not success:
                print_error("Échec création utilisateur")
                return False
        
        # Créer le répertoire d'application
        success, _, _ = run_command(f"sudo mkdir -p {self.deployment_path}", "Création répertoire application")
        if not success:
            return False
        
        # Définir les permissions
        success, _, _ = run_command(
            f"sudo chown vote-secret:vote-secret {self.deployment_path}",
            "Configuration permissions"
        )
        if not success:
            return False
        
        return prompt_continue()

    def step_2_deploy_application(self) -> bool:
        """Déploiement de l'application"""
        print_step(2, self.total_steps, "Déploiement de l'application")
        
        # Copier les fichiers de l'application
        print_info("Copie des fichiers de l'application...")
        
        # Fichiers à copier
        items_to_copy = [
            ('backend/', 'backend/'),
            ('frontend/', 'frontend/'),
            ('config/', 'config/'),
            ('scripts/', 'scripts/'),
            ('.env', '.env'),
            ('backend/.env', 'backend/.env'),
            ('frontend/.env', 'frontend/.env'),
            ('README.md', 'README.md'),
            ('PROJECT_STATUS.md', 'PROJECT_STATUS.md'),
            ('DEPLOYMENT_GUIDE.md', 'DEPLOYMENT_GUIDE.md')
        ]
        
        for src, dst in items_to_copy:
            src_path = self.project_root / src
            dst_path = self.deployment_path / dst
            
            if src_path.exists():
                if src_path.is_dir():
                    success, _, _ = run_command(
                        f"sudo cp -r {src_path} {dst_path.parent}/",
                        f"Copie {src}"
                    )
                else:
                    success, _, _ = run_command(
                        f"sudo mkdir -p {dst_path.parent} && sudo cp {src_path} {dst_path}",
                        f"Copie {src}"
                    )
                
                if not success:
                    print_warning(f"Erreur copie {src}")
        
        # Ajuster les permissions
        success, _, _ = run_command(
            f"sudo chown -R vote-secret:vote-secret {self.deployment_path}",
            "Ajustement permissions"
        )
        
        # Rendre les scripts exécutables
        success, _, _ = run_command(
            f"sudo chmod +x {self.deployment_path}/scripts/*.sh",
            "Scripts exécutables"
        )
        
        return prompt_continue()

    def step_3_install_dependencies(self) -> bool:
        """Installation des dépendances"""
        print_step(3, self.total_steps, "Installation des dépendances")
        
        # Environnement virtuel Python
        venv_path = self.deployment_path / 'venv'
        
        success, _, _ = run_command(
            f"sudo -u vote-secret python3 -m venv {venv_path}",
            "Création environnement virtuel Python"
        )
        if not success:
            return False
        
        # Installation des dépendances Python
        pip_path = venv_path / 'bin' / 'pip'
        requirements_path = self.deployment_path / 'backend' / 'requirements.txt'
        
        success, _, _ = run_command(
            f"sudo -u vote-secret {pip_path} install --upgrade pip setuptools wheel",
            "Mise à jour pip"
        )
        
        success, _, _ = run_command(
            f"sudo -u vote-secret {pip_path} install -r {requirements_path}",
            "Installation dépendances Python"
        )
        if not success:
            print_error("Échec installation dépendances Python")
            return False
        
        # Installation Gunicorn pour la production
        success, _, _ = run_command(
            f"sudo -u vote-secret {pip_path} install gunicorn",
            "Installation Gunicorn"
        )
        
        # Build du frontend
        frontend_path = self.deployment_path / 'frontend'
        
        print_info("Build du frontend (peut prendre plusieurs minutes)...")
        success, _, stderr = run_command(
            f"cd {frontend_path} && sudo -u vote-secret yarn install --production",
            "Installation dépendances frontend"
        )
        
        if not success:
            print_warning("Erreur yarn, tentative avec npm...")
            success, _, _ = run_command(
                f"cd {frontend_path} && sudo -u vote-secret npm install --production",
                "Installation dépendances frontend (npm)"
            )
        
        # Build de production
        success, _, stderr = run_command(
            f"cd {frontend_path} && sudo -u vote-secret npm run build",
            "Build frontend production"
        )
        
        if not success:
            print_error(f"Échec build frontend: {stderr}")
            return False
        
        print_success("Build frontend terminé")
        
        # Copie du build vers /var/www pour le serveur web
        app_name = self.config.get('SERVER_NAME', 'vote-secret')
        www_path = f"/var/www/{app_name}"
        build_path = frontend_path / 'build'
        
        if not build_path.exists():
            print_error("Répertoire build/ non trouvé après la compilation")
            return False
        
        # Créer le répertoire web et définir les permissions
        success, _, _ = run_command(f"sudo mkdir -p {www_path}", "Création répertoire web")
        if not success:
            return False
        
        # Copier les fichiers buildés
        success, _, _ = run_command(
            f"sudo cp -r {build_path}/* {www_path}/",
            "Copie build frontend vers /var/www"
        )
        if not success:
            print_error("Échec copie des fichiers web")
            return False
        
        # Définir les bonnes permissions pour le serveur web
        success, _, _ = run_command(
            f"sudo chown -R www-data:www-data {www_path}",
            "Configuration permissions serveur web"
        )
        if not success:
            print_warning("Impossible de définir les permissions www-data")
        
        # Permissions lecture pour tous
        success, _, _ = run_command(
            f"sudo chmod -R 755 {www_path}",
            "Configuration permissions lecture"
        )
        
        print_success(f"Frontend déployé dans {www_path}")
        return prompt_continue()

    def step_4_create_gunicorn_config(self) -> bool:
        """Configuration Gunicorn"""
        print_step(4, self.total_steps, "Configuration Gunicorn")
        
        gunicorn_config = f"""# Vote Secret v2.0 - Configuration Gunicorn
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8001"

# Worker processes
workers = {self.config.get('WORKERS', '4')}
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = {self.config.get('WORKER_CONNECTIONS', '1000')}

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Timeout
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/vote-secret/access.log"
errorlog = "/var/log/vote-secret/error.log"
loglevel = "{self.config.get('LOG_LEVEL', 'info').lower()}"

# Process naming
proc_name = 'vote-secret'

# Server mechanics
daemon = False
pidfile = '/var/run/vote-secret.pid'
user = 'vote-secret'
group = 'vote-secret'
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/key"
# certfile = "/path/to/cert"

def when_ready(server):
    server.log.info("Vote Secret server is ready. Listening on %s", server.address)

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized")

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)
"""
        
        # Création du répertoire de logs
        success, _, _ = run_command("sudo mkdir -p /var/log/vote-secret", "Création répertoire logs")
        success, _, _ = run_command("sudo chown vote-secret:vote-secret /var/log/vote-secret", "Permissions logs")
        
        # Écriture de la configuration Gunicorn
        config_path = self.deployment_path / 'config' / 'gunicorn.conf.py'
        
        with open('/tmp/gunicorn.conf.py', 'w') as f:
            f.write(gunicorn_config)
        
        success, _, _ = run_command(
            f"sudo mv /tmp/gunicorn.conf.py {config_path} && sudo chown vote-secret:vote-secret {config_path}",
            "Installation configuration Gunicorn"
        )
        
        return prompt_continue()

    def step_5_create_systemd_service(self) -> bool:
        """Création du service systemd"""
        print_step(5, self.total_steps, "Configuration service systemd")
        
        # Vérifier que le fichier service existe
        service_file = self.project_root / 'config' / 'vote-secret.service'
        if not service_file.exists():
            print_error("Fichier vote-secret.service non trouvé")
            return False
        
        # Copier le service systemd
        success, _, _ = run_command(
            f"sudo cp {service_file} /etc/systemd/system/",
            "Installation service systemd"
        )
        if not success:
            return False
        
        # Recharger systemd
        success, _, _ = run_command("sudo systemctl daemon-reload", "Rechargement systemd")
        if not success:
            return False
        
        # Activer le service
        success, _, _ = run_command("sudo systemctl enable vote-secret", "Activation service au démarrage")
        if not success:
            return False
        
        return prompt_continue()

    def step_6_install_scripts(self) -> bool:
        """Installation des scripts de gestion"""
        print_step(6, self.total_steps, "Installation scripts de gestion")
        
        scripts = ['manage.sh', 'backup.sh', 'monitor.sh']
        
        for script in scripts:
            script_path = self.deployment_path / 'scripts' / script
            if script_path.exists():
                success, _, _ = run_command(
                    f"sudo cp {script_path} /usr/local/bin/ && sudo chmod +x /usr/local/bin/{script}",
                    f"Installation {script}"
                )
                if success:
                    print_success(f"Script {script} installé")
        
        # Configuration logrotate
        logrotate_config = f"""/var/log/vote-secret/*.log {{
    daily
    missingok
    rotate {self.config.get('LOG_BACKUP_COUNT', '5')}
    compress
    delaycompress
    notifempty
    create 644 vote-secret vote-secret
    postrotate
        systemctl reload vote-secret
    endscript
}}"""
        
        with open('/tmp/vote-secret-logrotate', 'w') as f:
            f.write(logrotate_config)
        
        success, _, _ = run_command(
            "sudo mv /tmp/vote-secret-logrotate /etc/logrotate.d/vote-secret",
            "Configuration rotation logs"
        )
        
        return prompt_continue()

    def step_7_start_services(self) -> bool:
        """Démarrage des services"""
        print_step(7, self.total_steps, "Démarrage des services")
        
        # Démarrage du service Vote Secret
        success, _, stderr = run_command("sudo systemctl start vote-secret", "Démarrage Vote Secret")
        if not success:
            print_error(f"Échec démarrage service: {stderr}")
            print_info("Vérification des logs...")
            run_command("sudo journalctl -u vote-secret --no-pager -n 20", "Logs service")
            return False
        
        # Vérification du statut
        time.sleep(3)  # Attendre le démarrage
        
        success, stdout, _ = run_command("sudo systemctl status vote-secret --no-pager", "Vérification statut")
        if "active (running)" in stdout:
            print_success("Service Vote Secret actif")
        else:
            print_warning("Service Vote Secret non actif")
            print(stdout)
        
        # Test de connectivité backend
        success, _, _ = run_command("curl -s http://127.0.0.1:8001/health", "Test backend", check_success=False)
        if success:
            print_success("Backend répond correctement")
        else:
            print_warning("Backend ne répond pas (peut être normal si l'endpoint /health n'existe pas)")
        
        # Redémarrage de Nginx pour s'assurer de la configuration
        success, _, _ = run_command("sudo systemctl reload nginx", "Rechargement Nginx")
        
        return prompt_continue()

    def step_8_final_tests(self) -> bool:
        """Tests finaux et validation"""
        print_step(8, self.total_steps, "Tests finaux et validation")
        
        domain = self.config.get('DOMAIN', 'localhost')
        frontend_url = self.config.get('FRONTEND_URL', f'http://{domain}')
        
        print_info("Exécution des tests de validation...")
        
        # Test 1: Connectivité HTTP
        success, _, _ = run_command(f"curl -I {frontend_url}", "Test connectivité frontend", check_success=False)
        if success:
            print_success("Frontend accessible")
        else:
            print_warning("Frontend non accessible")
        
        # Test 2: API Backend
        api_url = self.config.get('BACKEND_URL', f'{frontend_url}/api')
        success, _, _ = run_command(f"curl -I {api_url}/health", "Test API backend", check_success=False)
        if success:
            print_success("API backend accessible")
        else:
            print_warning("API backend non accessible")
        
        # Test 3: Services système
        services = ['vote-secret', 'nginx', 'mongod']
        all_services_ok = True
        
        for service in services:
            success, _, _ = run_command(f"sudo systemctl is-active {service}", f"Vérification {service}", check_success=False)
            if success:
                print_success(f"Service {service} actif")
            else:
                print_warning(f"Service {service} inactif")
                all_services_ok = False
        
        # Test 4: Permissions et fichiers
        important_paths = [
            '/opt/vote-secret/backend/.env',
            '/opt/vote-secret/frontend/build/index.html',
            '/var/log/vote-secret',
            '/etc/systemd/system/vote-secret.service'
        ]
        
        for path in important_paths:
            if os.path.exists(path):
                print_success(f"Fichier/dossier {path} présent")
            else:
                print_warning(f"Fichier/dossier {path} manquant")
        
        # Test 5: Monitoring script
        success, _, _ = run_command("/usr/local/bin/monitor.sh", "Test script monitoring", check_success=False)
        if success:
            print_success("Script de monitoring fonctionnel")
        
        print_info("\n" + "="*60)
        print_info("RÉSUMÉ DES TESTS:")
        print_info("="*60)
        
        if all_services_ok:
            print_success("✅ Tous les services système sont actifs")
        else:
            print_warning("⚠️ Certains services ont des problèmes")
        
        print_info(f"Frontend: {frontend_url}")
        print_info(f"Backend: {api_url}")
        print_info("Logs: /var/log/vote-secret/")
        print_info("Scripts: /usr/local/bin/{manage,backup,monitor}.sh")
        
        return True

    def run(self):
        """Exécute le déploiement complet"""
        try:
            self.welcome()
            
            if not prompt_continue("Commencer le déploiement final ?"):
                print_info("Déploiement annulé")
                return
            
            steps = [
                self.step_1_create_system_user,
                self.step_2_deploy_application,
                self.step_3_install_dependencies,
                self.step_4_create_gunicorn_config,
                self.step_5_create_systemd_service,
                self.step_6_install_scripts,
                self.step_7_start_services,
                self.step_8_final_tests
            ]
            
            for i, step in enumerate(steps, 1):
                if not step():
                    print_error(f"Étape {i} échouée")
                    if not prompt_continue("Continuer malgré l'erreur ?"):
                        sys.exit(1)
            
            print_header("🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS ! 🎉")
            
            self._show_deployment_summary()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Déploiement interrompu.{Colors.ENDC}")
            sys.exit(1)
        except Exception as e:
            print_error(f"Erreur: {str(e)}")
            sys.exit(1)

    def _show_deployment_summary(self):
        """Affiche le résumé du déploiement"""
        domain = self.config.get('DOMAIN', 'localhost')
        frontend_url = self.config.get('FRONTEND_URL', f'http://{domain}')
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}Vote Secret v2.0 est maintenant déployé en production !{Colors.ENDC}\n")
        
        print(f"{Colors.CYAN}🌐 ACCÈS À L'APPLICATION:{Colors.ENDC}")
        print(f"   Frontend: {frontend_url}")
        print(f"   Domaine: {domain}")
        
        print(f"\n{Colors.CYAN}🔧 GESTION DE L'APPLICATION:{Colors.ENDC}")
        print("   sudo systemctl start/stop/restart vote-secret")
        print("   /usr/local/bin/manage.sh {start|stop|restart|status|logs}")
        print("   /usr/local/bin/monitor.sh (surveillance)")
        print("   /usr/local/bin/backup.sh (sauvegarde)")
        
        print(f"\n{Colors.CYAN}📁 FICHIERS IMPORTANTS:{Colors.ENDC}")
        print("   Application: /opt/vote-secret/")
        print("   Configuration: /opt/vote-secret/config/")
        print("   Logs: /var/log/vote-secret/")
        print("   Service: /etc/systemd/system/vote-secret.service")
        
        print(f"\n{Colors.CYAN}📖 DOCUMENTATION:{Colors.ENDC}")
        print("   Guide: /opt/vote-secret/DEPLOYMENT_GUIDE.md")
        print("   Status: /opt/vote-secret/PROJECT_STATUS.md")
        print("   README: /opt/vote-secret/README.md")
        
        if self.config.get('SSL_MODE') == 'letsencrypt':
            print(f"\n{Colors.CYAN}🔒 CERTIFICATS SSL:{Colors.ENDC}")
            print("   Renouvellement automatique activé")
            print("   Vérification: sudo certbot certificates")
        
        print(f"\n{Colors.CYAN}⚡ PROCHAINES ÉTAPES:{Colors.ENDC}")
        print("1. Testez l'application dans votre navigateur")
        print("2. Configurez les sauvegardes automatiques (crontab)")
        print("3. Surveillez les logs pendant les premiers jours")
        print("4. Documentez les procédures pour votre équipe")
        
        print(f"\n{Colors.GREEN}🎉 Vote Secret v2.0 est prêt pour la production ! 🎉{Colors.ENDC}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Vote Secret v2.0 - Déploiement Final")
        print("Usage: python3 deploy_final.py")
        return
    
    deployment = FinalDeployment()
    deployment.run()

if __name__ == "__main__":
    main()