#!/usr/bin/env python3
"""
Vote Secret v2.0 - Configuration Nginx et SSL
============================================

Script de configuration automatique de Nginx avec SSL pour production.
Gère Let's Encrypt, certificats existants et configuration optimisée.

Auteur: Assistant AI
Version: 2.0.0
Date: 2025-08-01
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Tuple, Optional

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
                timeout=300
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

class NginxSSLSetup:
    """Configuration Nginx et SSL"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config = self._load_config()
        self.total_steps = 6
        
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
        print_header("CONFIGURATION NGINX ET SSL")
        print(f"{Colors.CYAN}Configuration automatique du serveur web Nginx avec SSL{Colors.ENDC}")
        print(f"{Colors.CYAN}Domaine configuré: {self.config.get('DOMAIN', 'Non défini')}{Colors.ENDC}")
        print(f"{Colors.CYAN}Mode SSL: {self.config.get('SSL_MODE', 'Non défini')}{Colors.ENDC}\n")
        
        if not self.config.get('DOMAIN'):
            print_error("Configuration incomplète. Relancez deploy_environment.py")
            sys.exit(1)

    def step_1_install_nginx(self) -> bool:
        """Installation de Nginx"""
        print_step(1, self.total_steps, "Installation de Nginx")
        
        # Vérifier si Nginx est déjà installé
        success, stdout, _ = run_command("nginx -v", "Vérification Nginx", check_success=False)
        if success:
            print_success(f"Nginx déjà installé: {stdout}")
            return prompt_continue()
        
        # Installation selon la distribution
        distro = self._detect_distro()
        
        if distro in ['ubuntu', 'debian']:
            commands = [
                ("sudo apt update", "Mise à jour des paquets"),
                ("sudo apt install -y nginx", "Installation Nginx")
            ]
        elif distro in ['centos', 'rhel', 'rocky', 'almalinux']:
            commands = [
                ("sudo yum install -y epel-release", "Installation EPEL"),
                ("sudo yum install -y nginx", "Installation Nginx")
            ]
        elif distro == 'fedora':
            commands = [
                ("sudo dnf install -y nginx", "Installation Nginx")
            ]
        else:
            print_error(f"Distribution {distro} non supportée")
            return False
        
        for command, description in commands:
            # Les commandes d'installation peuvent nécessiter une interaction utilisateur
            interactive = any(cmd in command for cmd in ['apt install', 'yum install', 'dnf install'])
            success, _, _ = run_command(command, description, interactive=interactive)
            if not success:
                print_error(f"Échec: {description}")
                return False
        
        # Démarrage et activation
        success, _, _ = run_command("sudo systemctl start nginx", "Démarrage Nginx")
        if not success:
            print_warning("Erreur au démarrage de Nginx")
        
        success, _, _ = run_command("sudo systemctl enable nginx", "Activation au démarrage")
        if not success:
            print_warning("Erreur activation automatique Nginx")
        
        return prompt_continue()

    def step_2_backup_default_config(self) -> bool:
        """Sauvegarde de la configuration par défaut"""
        print_step(2, self.total_steps, "Sauvegarde configuration par défaut")
        
        # Sauvegarde des configurations existantes
        commands = [
            ("sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup", "Sauvegarde nginx.conf"),
            ("sudo mkdir -p /etc/nginx/sites-available", "Création sites-available"),
            ("sudo mkdir -p /etc/nginx/sites-enabled", "Création sites-enabled")
        ]
        
        for command, description in commands:
            success, _, _ = run_command(command, description, check_success=False)
            if success:
                print_success(description)
        
        # Suppression de la configuration par défaut si elle existe
        success, _, _ = run_command("sudo rm -f /etc/nginx/sites-enabled/default", "Suppression config par défaut", check_success=False)
        
        return prompt_continue()

    def step_3_configure_nginx(self) -> bool:
        """Configuration de Nginx"""
        print_step(3, self.total_steps, "Configuration Nginx")
        
        # Vérifier que le fichier de configuration existe
        nginx_config_file = self.project_root / 'config' / 'nginx.conf'
        if not nginx_config_file.exists():
            print_error("Fichier config/nginx.conf non trouvé. Exécutez deploy_environment.py")
            return False
        
        # Copier la configuration
        success, _, _ = run_command(
            f"sudo cp {nginx_config_file} /etc/nginx/sites-available/vote-secret",
            "Copie de la configuration"
        )
        if not success:
            return False
        
        # Activer le site
        success, _, _ = run_command(
            "sudo ln -sf /etc/nginx/sites-available/vote-secret /etc/nginx/sites-enabled/",
            "Activation du site"
        )
        if not success:
            return False
        
        # Test de la configuration
        success, stdout, stderr = run_command("sudo nginx -t", "Test de la configuration")
        if not success:
            print_error("Configuration Nginx invalide:")
            print(f"{Colors.FAIL}{stderr}{Colors.ENDC}")
            return False
        
        print_success("Configuration Nginx valide")
        return prompt_continue()

    def step_4_setup_ssl(self) -> bool:
        """Configuration SSL"""
        print_step(4, self.total_steps, "Configuration SSL")
        
        ssl_mode = self.config.get('SSL_MODE', 'none')
        
        if ssl_mode == 'letsencrypt':
            return self._setup_letsencrypt()
        elif ssl_mode == 'existing':
            return self._setup_existing_certs()
        elif ssl_mode == 'selfsigned':
            return self._setup_selfsigned()
        else:
            print_info("Aucune configuration SSL requise")
            return prompt_continue()

    def _setup_letsencrypt(self) -> bool:
        """Configuration Let's Encrypt avec approche en deux phases"""
        print_info("Configuration Let's Encrypt...")
        
        domain = self.config.get('DOMAIN')
        email = self.config.get('SSL_EMAIL')
        
        if not domain or not email:
            print_error("Domaine ou email manquant pour Let's Encrypt")
            return False
        
        # Installation de Certbot
        distro = self._detect_distro()
        
        if distro in ['ubuntu', 'debian']:
            install_commands = [
                ("sudo apt install -y snapd", "Installation snapd"),
                ("sudo snap install core; sudo snap refresh core", "Mise à jour snap"),
                ("sudo snap install --classic certbot", "Installation Certbot"),
                ("sudo ln -sf /snap/bin/certbot /usr/bin/certbot", "Lien symbolique Certbot")
            ]
        elif distro in ['centos', 'rhel', 'rocky', 'almalinux']:
            install_commands = [
                ("sudo yum install -y epel-release", "Installation EPEL"),
                ("sudo yum install -y certbot python3-certbot-nginx", "Installation Certbot")
            ]
        elif distro == 'fedora':
            install_commands = [
                ("sudo dnf install -y certbot python3-certbot-nginx", "Installation Certbot")
            ]
        else:
            print_error(f"Distribution {distro} non supportée pour Let's Encrypt")
            return False
        
        for command, description in install_commands:
            # Les installations peuvent nécessiter interaction
            interactive = any(cmd in command for cmd in ['apt install', 'yum install', 'dnf install'])
            success, _, _ = run_command(command, description, check_success=False, interactive=interactive)
            if not success:
                print_warning(f"Erreur: {description}")
        
        # Créer le répertoire pour le challenge ACME
        success, _, _ = run_command("sudo mkdir -p /var/www/html", "Création répertoire challenge")
        if not success:
            print_warning("Impossible de créer le répertoire challenge")
        
        # Vérifier que Nginx fonctionne avec la configuration HTTP
        success, _, _ = run_command("sudo systemctl reload nginx", "Rechargement Nginx")
        if not success:
            print_error("Nginx ne fonctionne pas correctement avec la configuration HTTP")
            return False
        
        # Obtention du certificat SANS modification automatique de la configuration
        print_info(f"Obtention du certificat SSL pour {domain}...")
        print_warning("Assurez-vous que le domaine pointe vers ce serveur !")
        
        if not prompt_continue(f"Le domaine {domain} pointe-t-il vers ce serveur ?"):
            print_error("Configuration DNS requise avant de continuer")
            return False
        
        # Utiliser certbot certonly (sans --nginx) pour éviter la modification automatique
        certbot_command = f"sudo certbot certonly --webroot -w /var/www/html -d {domain} --email {email} --agree-tos --non-interactive"
        success, stdout, stderr = run_command(certbot_command, "Obtention certificat SSL")
        
        if not success:
            print_error("Échec obtention certificat Let's Encrypt")
            print(f"{Colors.FAIL}{stderr}{Colors.ENDC}")
            print_info("Vérifiez que:")
            print("1. Le domaine pointe vers ce serveur")
            print("2. Les ports 80 et 443 sont ouverts")
            print("3. Aucun autre service n'utilise ces ports")
            print("4. Nginx est accessible en HTTP")
            return False
        
        # Maintenant, reconfigurer Nginx avec SSL en utilisant la configuration SSL générée
        print_info("Configuration Nginx avec SSL...")
        
        # Charger la configuration avec SSL depuis deploy_environment.py
        try:
            import sys
            sys.path.append(str(self.project_root))
            from deploy_environment import EnvironmentSetup
            
            env_setup = EnvironmentSetup()
            env_setup.config = self.config
            ssl_config_content = env_setup._generate_nginx_config_ssl()
            
            # Écrire la configuration SSL
            ssl_config_file = self.project_root / 'config' / 'nginx-ssl.conf'
            ssl_config_file.parent.mkdir(exist_ok=True)
            ssl_config_file.write_text(ssl_config_content)
            
            # Copier la nouvelle configuration
            success, _, _ = run_command(
                f"sudo cp {ssl_config_file} /etc/nginx/sites-available/vote-secret",
                "Mise à jour configuration SSL"
            )
            if not success:
                return False
            
            # Tester la nouvelle configuration
            success, stdout, stderr = run_command("sudo nginx -t", "Test configuration SSL")
            if not success:
                print_error("Configuration SSL invalide:")
                print(f"{Colors.FAIL}{stderr}{Colors.ENDC}")
                return False
            
            # Recharger Nginx avec SSL
            success, _, _ = run_command("sudo systemctl reload nginx", "Rechargement Nginx avec SSL")
            if not success:
                print_error("Échec rechargement Nginx avec SSL")
                return False
            
        except Exception as e:
            print_error(f"Erreur configuration SSL: {str(e)}")
            return False
        
        # Configuration du renouvellement automatique
        success, _, _ = run_command("sudo systemctl enable certbot.timer", "Activation renouvellement auto", check_success=False)
        
        print_success("Certificat SSL Let's Encrypt configuré avec succès")
        print_info("HTTPS est maintenant actif et HTTP redirige vers HTTPS")
        return True

    def _setup_existing_certs(self) -> bool:
        """Configuration avec certificats existants"""
        print_info("Configuration avec certificats existants...")
        
        cert_path = self.config.get('SSL_CERT_PATH')
        key_path = self.config.get('SSL_KEY_PATH')
        
        if not cert_path or not key_path:
            print_error("Chemins des certificats manquants")
            return False
        
        # Vérification de l'existence des certificats
        if not os.path.exists(cert_path):
            print_error(f"Certificat non trouvé: {cert_path}")
            return False
        
        if not os.path.exists(key_path):
            print_error(f"Clé privée non trouvée: {key_path}")
            return False
        
        # Test des certificats
        success, _, _ = run_command(f"sudo openssl x509 -in {cert_path} -text -noout", "Vérification certificat", check_success=False)
        if not success:
            print_error("Certificat invalide")
            return False
        
        print_success("Certificats existants validés")
        return True

    def _setup_selfsigned(self) -> bool:
        """Configuration avec certificats auto-signés"""
        print_info("Génération de certificats auto-signés...")
        print_warning("Les certificats auto-signés ne sont pas recommandés en production")
        
        domain = self.config.get('DOMAIN')
        ssl_dir = "/etc/ssl/vote-secret"
        
        # Création du répertoire SSL
        success, _, _ = run_command(f"sudo mkdir -p {ssl_dir}", "Création répertoire SSL")
        if not success:
            return False
        
        # Génération du certificat auto-signé
        openssl_command = f"""sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
-keyout {ssl_dir}/vote-secret.key \
-out {ssl_dir}/vote-secret.crt \
-subj "/C=FR/ST=France/L=City/O=Organization/OU=IT/CN={domain}" """
        
        success, _, _ = run_command(openssl_command, "Génération certificat auto-signé")
        if not success:
            return False
        
        # Mise à jour des chemins dans la configuration
        self.config['SSL_CERT_PATH'] = f"{ssl_dir}/vote-secret.crt"
        self.config['SSL_KEY_PATH'] = f"{ssl_dir}/vote-secret.key"
        
        print_success("Certificat auto-signé généré")
        print_warning("Les navigateurs afficheront un avertissement de sécurité")
        
        return True

    def step_5_test_configuration(self) -> bool:
        """Test de la configuration complète"""
        print_step(5, self.total_steps, "Test de la configuration")
        
        # Test de la configuration Nginx
        success, _, stderr = run_command("sudo nginx -t", "Test configuration Nginx")
        if not success:
            print_error(f"Configuration Nginx invalide: {stderr}")
            return False
        
        # Rechargement de Nginx
        success, _, _ = run_command("sudo systemctl reload nginx", "Rechargement Nginx")
        if not success:
            print_error("Erreur rechargement Nginx")
            return False
        
        # Test des ports
        time.sleep(2)  # Attendre que Nginx démarre complètement
        
        success, _, _ = run_command("sudo netstat -tuln | grep :80", "Vérification port 80", check_success=False)
        if success:
            print_success("Port 80 ouvert")
        else:
            print_warning("Port 80 non accessible")
        
        success, _, _ = run_command("sudo netstat -tuln | grep :443", "Vérification port 443", check_success=False)
        if success:
            print_success("Port 443 ouvert")
        else:
            print_warning("Port 443 non accessible (normal si pas de SSL)")
        
        # Test HTTP
        domain = self.config.get('DOMAIN', 'localhost')
        success, _, _ = run_command(f"curl -I http://{domain}/health", "Test HTTP", check_success=False)
        if success:
            print_success("Test HTTP réussi")
        else:
            print_warning("Test HTTP échoué (normal si le backend n'est pas encore déployé)")
        
        # Test HTTPS si SSL configuré
        if self.config.get('SSL_MODE') != 'none':
            success, _, _ = run_command(f"curl -I -k https://{domain}/health", "Test HTTPS", check_success=False)
            if success:
                print_success("Test HTTPS réussi")
            else:
                print_warning("Test HTTPS échoué")
        
        return prompt_continue()

    def step_6_security_hardening(self) -> bool:
        """Durcissement sécurité Nginx"""
        print_step(6, self.total_steps, "Durcissement sécurité")
        
        # Configuration nginx.conf principale pour la sécurité
        nginx_security_config = """
# Configuration sécurité générale Nginx
server_tokens off;
client_max_body_size 10M;
client_body_timeout 12;
client_header_timeout 12;
keepalive_timeout 15;
send_timeout 10;

# Rate limiting global
limit_req_zone $binary_remote_addr zone=global:10m rate=10r/m;

# Protection DDoS basique
limit_conn_zone $binary_remote_addr zone=addr:10m;
limit_conn addr 10;
"""
        
        # Écriture de la configuration sécurité
        security_file = "/tmp/nginx_security.conf"
        with open(security_file, 'w') as f:
            f.write(nginx_security_config)
        
        # Inclusion dans la configuration principale
        success, _, _ = run_command(
            f"sudo cp {security_file} /etc/nginx/conf.d/security.conf",
            "Configuration sécurité Nginx"
        )
        
        if success:
            print_success("Configuration sécurité appliquée")
        
        # Nettoyage
        os.remove(security_file)
        
        # Configuration du firewall (UFW si disponible)
        success, _, _ = run_command("which ufw", "Vérification UFW", check_success=False)
        if success:
            print_info("Configuration du firewall UFW...")
            firewall_commands = [
                ("sudo ufw allow 22/tcp", "Autorisation SSH"),
                ("sudo ufw allow 80/tcp", "Autorisation HTTP"),
                ("sudo ufw allow 443/tcp", "Autorisation HTTPS"),
                ("sudo ufw --force enable", "Activation UFW")
            ]
            
            for command, description in firewall_commands:
                success, _, _ = run_command(command, description, check_success=False)
                if success:
                    print_success(description)
        else:
            print_info("UFW non disponible - configurez manuellement le firewall")
        
        # Test final
        success, _, _ = run_command("sudo nginx -t && sudo systemctl reload nginx", "Test final et rechargement")
        if not success:
            print_error("Erreur configuration finale")
            return False
        
        print_success("Durcissement sécurité terminé")
        return True

    def _detect_distro(self) -> str:
        """Détecte la distribution Linux"""
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        return line.split('=')[1].strip().strip('"').lower()
        except:
            pass
        return 'unknown'

    def run(self):
        """Exécute la configuration complète"""
        try:
            self.welcome()
            
            steps = [
                self.step_1_install_nginx,
                self.step_2_backup_default_config,
                self.step_3_configure_nginx,
                self.step_4_setup_ssl,
                self.step_5_test_configuration,
                self.step_6_security_hardening
            ]
            
            for i, step in enumerate(steps, 1):
                if not step():
                    print_error(f"Étape {i} échouée")
                    if not prompt_continue("Continuer malgré l'erreur ?"):
                        sys.exit(1)
            
            print_header("NGINX CONFIGURÉ AVEC SUCCÈS")
            print_success("Serveur web Nginx configuré et sécurisé !")
            
            print_info("Configuration terminée :")
            print(f"  • Nginx installé et configuré")
            print(f"  • SSL: {self.config.get('SSL_MODE', 'aucun')}")
            print(f"  • Domaine: {self.config.get('DOMAIN')}")
            print(f"  • Sécurité renforcée")
            
            print(f"\n{Colors.BLUE}Prochaine étape: Exécutez deploy_systemd.py{Colors.ENDC}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Configuration interrompue.{Colors.ENDC}")
            sys.exit(1)
        except Exception as e:
            print_error(f"Erreur: {str(e)}")
            sys.exit(1)

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Vote Secret v2.0 - Configuration Nginx et SSL")
        print("Usage: python3 deploy_nginx.py")
        return
    
    setup = NginxSSLSetup()
    setup.run()

if __name__ == "__main__":
    main()