#!/usr/bin/env python3
"""
Vote Secret - Diagnostic et Réparation Automatique
==================================================

Script de diagnostic pour identifier et résoudre automatiquement les problèmes
de déploiement et de service Vote Secret.

Usage:
  python3 diagnostic.py              # Diagnostic complet
  python3 diagnostic.py --fix        # Diagnostic + corrections automatiques
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
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

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== {text} ==={Colors.ENDC}")

def run_command(command, capture=True):
    """Exécute une commande et retourne le résultat"""
    try:
        if capture:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def check_environment():
    """Vérifie l'environnement d'exécution"""
    print_header("DIAGNOSTIC ENVIRONNEMENT")
    issues = []
    
    # Détection du type d'environnement
    if os.path.exists('/run/systemd/system'):
        print_success("Environnement SystemD détecté")
        env_type = 'systemd'
    elif os.path.exists('/etc/supervisor') or subprocess.run(['which', 'supervisorctl'], capture_output=True).returncode == 0:
        print_success("Environnement Supervisor détecté (conteneurisé)")
        env_type = 'supervisor'
    else:
        print_error("Aucun gestionnaire de services détecté")
        issues.append("no_service_manager")
        env_type = 'unknown'
    
    # Vérification des répertoires de base
    if os.path.exists('/app'):
        print_success("Répertoire application /app trouvé")
    else:
        print_error("Répertoire application /app manquant")
        issues.append("missing_app_dir")
    
    # Vérification de l'environnement Python
    success, stdout, stderr = run_command('python3 --version')
    if success:
        print_success(f"Python disponible: {stdout.strip()}")
    else:
        print_error("Python3 non disponible")
        issues.append("missing_python")
    
    return env_type, issues

def check_application_files():
    """Vérifie la présence des fichiers d'application"""
    print_header("DIAGNOSTIC FICHIERS APPLICATION")
    issues = []
    
    critical_files = [
        '/app/backend/server.py',
        '/app/backend/requirements.txt',
        '/app/frontend/package.json',
        '/app/frontend/src/App.js'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print_success(f"Fichier critique trouvé: {file_path}")
        else:
            print_error(f"Fichier critique manquant: {file_path}")
            issues.append(f"missing_file:{file_path}")
    
    return issues

def check_services_status():
    """Vérifie le statut des services"""
    print_header("DIAGNOSTIC SERVICES")
    issues = []
    
    # Vérification supervisor
    success, stdout, stderr = run_command('supervisorctl status')
    if success:
        print_info("Services supervisor:")
        for line in stdout.strip().split('\n'):
            if line.strip():
                if 'RUNNING' in line:
                    print_success(f"  {line}")
                else:
                    print_warning(f"  {line}")
                    if 'backend' in line.lower():
                        issues.append("backend_not_running")
    else:
        print_error("Impossible d'obtenir le statut supervisor")
        issues.append("supervisor_unavailable")
    
    # Test de connectivité API
    success, stdout, stderr = run_command('curl -s -w "%{http_code}" http://localhost:8001/api/health')
    if success and '200' in stdout:
        print_success("API Vote Secret accessible (port 8001)")
    else:
        print_error("API Vote Secret non accessible (port 8001)")
        issues.append("api_not_accessible")
    
    # Test de connectivité frontend
    success, stdout, stderr = run_command('curl -s -w "%{http_code}" http://localhost:3000')
    if success and ('200' in stdout or '302' in stdout):
        print_success("Frontend Vote Secret accessible (port 3000)")
    else:
        print_error("Frontend Vote Secret non accessible (port 3000)")
        issues.append("frontend_not_accessible")
    
    return issues

def check_dependencies():
    """Vérifie les dépendances"""
    print_header("DIAGNOSTIC DÉPENDANCES")
    issues = []
    
    # Vérification dépendances Python backend
    backend_deps = ['fastapi', 'uvicorn', 'pymongo', 'motor', 'reportlab']
    for dep in backend_deps:
        success, stdout, stderr = run_command(f'cd /app/backend && python3 -c "import {dep}"; echo "OK"')
        if success and 'OK' in stdout:
            print_success(f"Dépendance Python disponible: {dep}")
        else:
            print_error(f"Dépendance Python manquante: {dep}")
            issues.append(f"missing_python_dep:{dep}")
    
    # Vérification Node.js et dépendances frontend
    success, stdout, stderr = run_command('node --version')
    if success:
        print_success(f"Node.js disponible: {stdout.strip()}")
    else:
        print_error("Node.js non disponible")
        issues.append("missing_nodejs")
    
    success, stdout, stderr = run_command('yarn --version')
    if success:
        print_success(f"Yarn disponible: {stdout.strip()}")
    else:
        print_error("Yarn non disponible")
        issues.append("missing_yarn")
    
    return issues

def check_database():
    """Vérifie la base de données"""
    print_header("DIAGNOSTIC BASE DE DONNÉES")
    issues = []
    
    # Vérification MongoDB
    success, stdout, stderr = run_command('mongosh --eval "db.adminCommand({ping: 1})" --quiet')
    if success:
        print_success("MongoDB accessible et fonctionnel")
    else:
        print_error("MongoDB non accessible")
        issues.append("mongodb_not_accessible")
    
    return issues

def fix_supervisor_service():
    """Corrige les problèmes de service supervisor"""
    print_info("Tentative de correction des services supervisor...")
    
    # Redémarrer les services
    success, stdout, stderr = run_command('supervisorctl restart backend frontend')
    if success:
        print_success("Services redémarrés avec succès")
        return True
    else:
        print_error(f"Échec redémarrage: {stderr}")
        return False

def fix_missing_dependencies():
    """Installe les dépendances manquantes"""
    print_info("Installation des dépendances manquantes...")
    
    # Installation dépendances Python
    success, stdout, stderr = run_command('cd /app/backend && pip install -r requirements.txt')
    if success:
        print_success("Dépendances Python installées")
    else:
        print_error("Échec installation dépendances Python")
        return False
    
    # Installation dépendances Node.js
    success, stdout, stderr = run_command('cd /app/frontend && yarn install')
    if success:
        print_success("Dépendances Node.js installées")
    else:
        print_warning("Problème installation dépendances Node.js")
    
    return True

def generate_solution_guide(issues):
    """Génère un guide de solutions pour les problèmes identifiés"""
    print_header("GUIDE DE SOLUTIONS")
    
    if not issues:
        print_success("Aucun problème détecté ! Vote Secret fonctionne correctement.")
        return
    
    solutions = {
        'no_service_manager': "Installer systemd ou supervisor selon l'environnement",
        'missing_app_dir': "Cloner le dépôt Vote Secret dans /app",
        'missing_python': "Installer Python 3.8+ sur le système",
        'backend_not_running': "Redémarrer le service backend avec service_manager.py",
        'api_not_accessible': "Vérifier que le backend écoute sur le port 8001",
        'frontend_not_accessible': "Vérifier que le frontend écoute sur le port 3000",
        'mongodb_not_accessible': "Démarrer MongoDB ou vérifier la configuration",
        'missing_nodejs': "Installer Node.js 16+ sur le système",
        'missing_yarn': "Installer Yarn package manager"
    }
    
    for issue in issues:
        if issue.startswith('missing_file:'):
            file_path = issue.split(':', 1)[1]
            print_error(f"Fichier manquant: {file_path}")
            print_info("Solution: Restaurer le fichier depuis le dépôt Git")
        elif issue.startswith('missing_python_dep:'):
            dep = issue.split(':', 1)[1]
            print_error(f"Dépendance Python manquante: {dep}")
            print_info(f"Solution: pip install {dep}")
        elif issue in solutions:
            print_error(f"Problème: {issue}")
            print_info(f"Solution: {solutions[issue]}")
        else:
            print_warning(f"Problème non documenté: {issue}")

def main():
    fix_mode = '--fix' in sys.argv
    
    print(f"{Colors.BOLD}=== DIAGNOSTIC VOTE SECRET v2.0 ==={Colors.ENDC}")
    if fix_mode:
        print_info("Mode correction automatique activé")
    
    all_issues = []
    
    # Diagnostic complet
    env_type, env_issues = check_environment()
    all_issues.extend(env_issues)
    
    app_issues = check_application_files()
    all_issues.extend(app_issues)
    
    service_issues = check_services_status()
    all_issues.extend(service_issues)
    
    dep_issues = check_dependencies()
    all_issues.extend(dep_issues)
    
    db_issues = check_database()
    all_issues.extend(db_issues)
    
    # Corrections automatiques si demandées
    if fix_mode and all_issues:
        print_header("CORRECTIONS AUTOMATIQUES")
        
        if 'backend_not_running' in all_issues or 'api_not_accessible' in all_issues:
            fix_supervisor_service()
        
        if any(issue.startswith('missing_python_dep:') for issue in all_issues):
            fix_missing_dependencies()
    
    # Guide de solutions
    generate_solution_guide(all_issues)
    
    # Résumé final
    print_header("RÉSUMÉ")
    if not all_issues:
        print_success("Vote Secret fonctionne parfaitement !")
        print_info("Vous pouvez utiliser l'application normalement.")
    else:
        print_warning(f"{len(all_issues)} problème(s) détecté(s)")
        print_info("Consultez le guide de solutions ci-dessus.")
        if not fix_mode:
            print_info("Utilisez --fix pour tenter les corrections automatiques.")
    
    # Test final de connectivité
    print_info("Test final de connectivité...")
    success, stdout, stderr = run_command('curl -s http://localhost:8001/api/health')
    if success and '"status":"healthy"' in stdout:
        print_success("🎉 Vote Secret est opérationnel !")
        print(f"API Health: {stdout}")
    else:
        print_error("Vote Secret n'est pas complètement opérationnel")
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)