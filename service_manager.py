#!/usr/bin/env python3
"""
Vote Secret - Gestionnaire de Service Adapté
============================================

Script adapté pour environnements conteneurisés (supervisor) et systèmes (systemd).
Détecte automatiquement l'environnement et utilise le bon gestionnaire de services.

Usage:
  python3 service_manager.py start
  python3 service_manager.py stop  
  python3 service_manager.py restart
  python3 service_manager.py status
"""

import os
import sys
import subprocess
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")

def run_command(command, description=""):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def detect_environment():
    """Détecte l'environnement de gestion de services"""
    if os.path.exists('/run/systemd/system'):
        return 'systemd'
    elif os.path.exists('/etc/supervisor') or subprocess.run(['which', 'supervisorctl'], capture_output=True).returncode == 0:
        return 'supervisor'
    else:
        return 'unknown'

def get_service_status():
    """Obtient le statut du service Vote Secret"""
    env = detect_environment()
    
    if env == 'systemd':
        success, stdout, stderr = run_command('systemctl is-active vote-secret.service')
        if success:
            return True, "running"
        else:
            return False, "stopped"
    
    elif env == 'supervisor':
        success, stdout, stderr = run_command('supervisorctl status backend')
        if success and 'RUNNING' in stdout:
            return True, "running"
        else:
            return False, "stopped"
    
    return False, "unknown"

def start_service():
    """Démarre le service Vote Secret"""
    env = detect_environment()
    print_info(f"Environnement détecté: {env}")
    
    if env == 'systemd':
        print_info("Démarrage du service systemd...")
        success, stdout, stderr = run_command('sudo systemctl start vote-secret.service')
        if success:
            print_success("Service Vote Secret démarré")
            return True
        else:
            print_error(f"Échec démarrage: {stderr}")
            return False
    
    elif env == 'supervisor':
        print_info("Démarrage du service supervisor...")
        # Le backend est géré par supervisor sous le nom "backend"
        success, stdout, stderr = run_command('supervisorctl start backend')
        if success:
            print_success("Service Vote Secret (backend) démarré")
            # Optionnel: démarrer aussi le frontend
            success_front, _, _ = run_command('supervisorctl start frontend')
            if success_front:
                print_success("Frontend également démarré")
            return True
        else:
            print_error(f"Échec démarrage: {stderr}")
            return False
    
    else:
        print_error("Environnement de gestion de services non supporté")
        return False

def stop_service():
    """Arrête le service Vote Secret"""
    env = detect_environment()
    print_info(f"Environnement détecté: {env}")
    
    if env == 'systemd':
        print_info("Arrêt du service systemd...")
        success, stdout, stderr = run_command('sudo systemctl stop vote-secret.service')
        if success:
            print_success("Service Vote Secret arrêté")
            return True
        else:
            print_error(f"Échec arrêt: {stderr}")
            return False
    
    elif env == 'supervisor':
        print_info("Arrêt du service supervisor...")
        success, stdout, stderr = run_command('supervisorctl stop backend')
        if success:
            print_success("Service Vote Secret (backend) arrêté")
            return True
        else:
            print_error(f"Échec arrêt: {stderr}")
            return False
    
    else:
        print_error("Environnement de gestion de services non supporté")
        return False

def restart_service():
    """Redémarre le service Vote Secret"""
    env = detect_environment()
    print_info(f"Environnement détecté: {env}")
    
    if env == 'systemd':
        print_info("Redémarrage du service systemd...")
        success, stdout, stderr = run_command('sudo systemctl restart vote-secret.service')
        if success:
            print_success("Service Vote Secret redémarré")
            return True
        else:
            print_error(f"Échec redémarrage: {stderr}")
            return False
    
    elif env == 'supervisor':
        print_info("Redémarrage du service supervisor...")
        success, stdout, stderr = run_command('supervisorctl restart backend')
        if success:
            print_success("Service Vote Secret (backend) redémarré")
            # Optionnel: redémarrer aussi le frontend
            success_front, _, _ = run_command('supervisorctl restart frontend')
            if success_front:
                print_success("Frontend également redémarré")
            return True
        else:
            print_error(f"Échec redémarrage: {stderr}")
            return False
    
    else:
        print_error("Environnement de gestion de services non supporté")
        return False

def show_status():
    """Affiche le statut du service Vote Secret"""
    env = detect_environment()
    print_info(f"Environnement détecté: {env}")
    
    if env == 'systemd':
        print_info("Statut du service systemd:")
        success, stdout, stderr = run_command('systemctl status vote-secret.service')
        print(stdout)
        if stderr:
            print_error(stderr)
    
    elif env == 'supervisor':
        print_info("Statut des services supervisor:")
        success, stdout, stderr = run_command('supervisorctl status backend frontend')
        print(stdout)
        
        # Test de connectivité API
        print_info("Test de connectivité API:")
        success, stdout, stderr = run_command('curl -s http://localhost:8001/api/health')
        if success and '"status":"healthy"' in stdout:
            print_success("API Vote Secret accessible et fonctionnelle")
            print(f"Réponse: {stdout}")
        else:
            print_error("API Vote Secret non accessible")
    
    else:
        print_error("Environnement de gestion de services non supporté")

def show_logs():
    """Affiche les logs du service"""
    env = detect_environment()
    print_info(f"Environnement détecté: {env}")
    
    if env == 'systemd':
        print_info("Logs systemd:")
        success, stdout, stderr = run_command('journalctl -u vote-secret.service -n 20')
        print(stdout)
    
    elif env == 'supervisor':
        print_info("Logs supervisor:")
        print(f"{Colors.BOLD}=== Backend Logs ==={Colors.ENDC}")
        success, stdout, stderr = run_command('tail -n 10 /var/log/supervisor/backend.out.log')
        if success:
            print(stdout)
        
        success, stdout, stderr = run_command('tail -n 10 /var/log/supervisor/backend.err.log')
        if success and stdout.strip():
            print(f"{Colors.BOLD}=== Backend Errors ==={Colors.ENDC}")
            print(stdout)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} {{start|stop|restart|status|logs}}")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    print(f"{Colors.BOLD}=== Vote Secret Service Manager ==={Colors.ENDC}")
    
    if action == 'start':
        success = start_service()
    elif action == 'stop':
        success = stop_service()
    elif action == 'restart':
        success = restart_service()
    elif action == 'status':
        show_status()
        success = True
    elif action == 'logs':
        show_logs()
        success = True
    else:
        print_error(f"Action non reconnue: {action}")
        print("Actions disponibles: start, stop, restart, status, logs")
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()