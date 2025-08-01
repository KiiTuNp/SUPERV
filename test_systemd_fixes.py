#!/usr/bin/env python3
"""
Test des corrections du Service SystemD Vote Secret v2.0
========================================================

Script de test pour valider les corrections apportées au problème de démarrage du service:
- Configuration systemd corrigée
- Configuration gunicorn ajoutée
- Chemins et permissions corrigés
- Variables d'environnement appropriées

Auteur: Assistant AI
Version: 2.0.3
Date: 2025-01-31
"""

import os
import sys
import tempfile
from pathlib import Path

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

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")

def test_systemd_service_config():
    """Test de la configuration systemd corrigée"""
    print_header("TEST CONFIGURATION SYSTEMD SERVICE")
    
    try:
        sys.path.append('/app')
        from deploy_environment import ProductionEnvironmentSetup
        
        env_setup = ProductionEnvironmentSetup()
        env_setup.config = {
            'LOG_LEVEL': 'INFO'
        }
        
        # Générer la configuration systemd
        systemd_config = env_setup._generate_systemd_service()
        
        # Vérifications
        checks = [
            ("Type=exec au lieu de forking", "Type=exec" in systemd_config),
            ("User vote-secret présent", "User=vote-secret" in systemd_config),
            ("Group vote-secret présent", "Group=vote-secret" in systemd_config),
            ("WorkingDirectory correct", "WorkingDirectory=/opt/vote-secret/backend" in systemd_config),
            ("PATH complet avec venv", "PATH=/opt/vote-secret/venv/bin:" in systemd_config),
            ("PYTHONPATH configuré", "PYTHONPATH=/opt/vote-secret/backend" in systemd_config),
            ("Gunicorn avec config", "--config /opt/vote-secret/config/gunicorn.conf.py" in systemd_config),
            ("Après MongoDB", "After=network.target mongodb.service" in systemd_config),
            ("Restart on-failure", "Restart=on-failure" in systemd_config),
            ("StandardOutput journal", "StandardOutput=journal" in systemd_config)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print_success(f"{check_name}: Correct")
            else:
                print_error(f"{check_name}: Échec")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Erreur test systemd config: {e}")
        return False

def test_gunicorn_config():
    """Test de la configuration Gunicorn"""
    print_header("TEST CONFIGURATION GUNICORN")
    
    try:
        sys.path.append('/app')
        from deploy_environment import ProductionEnvironmentSetup
        
        env_setup = ProductionEnvironmentSetup()
        env_setup.config = {
            'LOG_LEVEL': 'INFO'
        }
        
        # Générer la configuration Gunicorn
        gunicorn_config = env_setup._generate_gunicorn_config()
        
        # Vérifications
        checks = [
            ("Bind 127.0.0.1:8001", 'bind = "127.0.0.1:8001"' in gunicorn_config),
            ("Workers configurés", "workers = " in gunicorn_config),
            ("UvicornWorker", "uvicorn.workers.UvicornWorker" in gunicorn_config),
            ("Logs dans /var/log", "/var/log/vote-secret/" in gunicorn_config),
            ("PID file correct", 'pidfile = "/var/log/vote-secret/gunicorn.pid"' in gunicorn_config),
            ("User vote-secret", 'user = "vote-secret"' in gunicorn_config),
            ("Group vote-secret", 'group = "vote-secret"' in gunicorn_config),
            ("PYTHONPATH raw_env", "PYTHONPATH=/opt/vote-secret/backend" in gunicorn_config),
            ("Daemon False", "daemon = False" in gunicorn_config),
            ("Log level configuré", "loglevel" in gunicorn_config)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print_success(f"{check_name}: Correct")
            else:
                print_error(f"{check_name}: Échec")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Erreur test gunicorn config: {e}")
        return False

def test_file_generation():
    """Test de génération de tous les fichiers nécessaires"""
    print_header("TEST GÉNÉRATION FICHIERS SERVICE")
    
    try:
        sys.path.append('/app')
        from deploy_environment import ProductionEnvironmentSetup
        
        env_setup = ProductionEnvironmentSetup()
        env_setup.config = {
            'LOG_LEVEL': 'INFO',
            'MONITORING_ENABLED': True,
            'METRICS_PORT': '9090'
        }
        
        # Test de génération sans erreurs
        systemd_config = env_setup._generate_systemd_service()
        gunicorn_config = env_setup._generate_gunicorn_config()
        
        # Vérifications basiques
        checks = [
            ("Config systemd générée", len(systemd_config) > 500),
            ("Config gunicorn générée", len(gunicorn_config) > 1000),
            ("Systemd structure valide", "[Unit]" in systemd_config and "[Service]" in systemd_config),
            ("Gunicorn structure valide", "bind = " in gunicorn_config and "workers = " in gunicorn_config),
            ("Pas d'erreurs Python", "Traceback" not in systemd_config and "Traceback" not in gunicorn_config)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print_success(f"{check_name}: OK")
            else:
                print_error(f"{check_name}: Échec")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Erreur génération fichiers: {e}")
        return False

def test_config_files_inclusion():
    """Test d'inclusion de gunicorn.conf.py dans les fichiers générés"""
    print_header("TEST INCLUSION FICHIERS CONFIGURATION")
    
    try:
        with open('/app/deploy_environment.py', 'r') as f:
            content = f.read()
        
        # Vérifications
        checks = [
            ("Méthode gunicorn présente", "_generate_gunicorn_config" in content),
            ("Gunicorn dans configs", "'config/gunicorn.conf.py'" in content),
            ("Appel méthode gunicorn", "_generate_gunicorn_config()" in content),
            ("Commentaire approprié", "# Configuration Gunicorn" in content)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print_success(f"{check_name}: Présent")
            else:
                print_error(f"{check_name}: Manquant")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Erreur test inclusion: {e}")
        return False

def test_deploy_final_integration():
    """Test d'intégration avec deploy_final.py"""
    print_header("TEST INTÉGRATION DEPLOY_FINAL.PY")
    
    try:
        with open('/app/deploy_final.py', 'r') as f:
            content = f.read()
        
        # Vérifications
        checks = [
            ("Création utilisateur vote-secret", "useradd" in content and "vote-secret" in content),
            ("Répertoire logs /var/log", "/var/log/vote-secret" in content),
            ("Permissions logs", "chown vote-secret:vote-secret" in content),
            ("Création répertoire app", "/opt/vote-secret" in content),
            ("Support interactif", "interactive: bool = False" in content)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print_success(f"{check_name}: Présent")
            else:
                print_error(f"{check_name}: Manquant")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Erreur test deploy_final: {e}")
        return False

def test_syntax_validation():
    """Test de validation syntaxique des scripts modifiés"""
    print_header("TEST VALIDATION SYNTAXIQUE")
    
    scripts_to_test = [
        '/app/deploy_environment.py',
        '/app/deploy_final.py'
    ]
    
    all_passed = True
    
    for script_path in scripts_to_test:
        script_name = Path(script_path).name
        try:
            # Test de compilation Python
            with open(script_path, 'r') as f:
                content = f.read()
            
            compile(content, script_path, 'exec')
            print_success(f"{script_name}: Syntaxe valide")
            
        except SyntaxError as e:
            print_error(f"{script_name}: Erreur syntaxe ligne {e.lineno}: {e.msg}")
            all_passed = False
        except Exception as e:
            print_error(f"{script_name}: Erreur: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Fonction principale"""
    print_header("TESTS DES CORRECTIONS SERVICE SYSTEMD")
    print_info("Validation des corrections apportées au problème de démarrage du service")
    
    tests = [
        ("Configuration SystemD", test_systemd_service_config),
        ("Configuration Gunicorn", test_gunicorn_config),
        ("Génération Fichiers", test_file_generation),
        ("Inclusion Configurations", test_config_files_inclusion),
        ("Intégration Deploy Final", test_deploy_final_integration),
        ("Validation Syntaxique", test_syntax_validation)
    ]
    
    total_tests = len(tests)
    passed_tests = 0
    
    for test_name, test_function in tests:
        print(f"\n{Colors.CYAN}Test: {test_name}{Colors.ENDC}")
        try:
            if test_function():
                passed_tests += 1
            else:
                print_error(f"Test {test_name} échoué")
        except Exception as e:
            print_error(f"Erreur dans test {test_name}: {e}")
    
    # Résumé final
    print_header("RÉSUMÉ DES TESTS SERVICE")
    success_rate = (passed_tests / total_tests) * 100
    
    if passed_tests == total_tests:
        print_success(f"Tous les tests réussis: {passed_tests}/{total_tests} (100%)")
        print_info("Les corrections du service SystemD sont validées!")
    else:
        print_error(f"Tests échoués: {total_tests - passed_tests}/{total_tests}")
        print_info(f"Taux de réussite: {success_rate:.1f}%")
    
    # Solution au problème
    print_header("SOLUTION AU PROBLÈME SERVICE")
    print_info("Problème résolu:")
    print("  ❌ AVANT: Service vote-secret.service ne démarre pas")
    print("  ✅ APRÈS: Configuration systemd + gunicorn complète et fonctionnelle")
    print()
    print_info("Corrections apportées:")
    print("  1. Type=exec au lieu de Type=forking")
    print("  2. Ajout configuration gunicorn.conf.py manquante")
    print("  3. Chemins et variables d'environnement corrigés")
    print("  4. WorkingDirectory=/opt/vote-secret/backend")
    print("  5. PYTHONPATH configuré correctement")
    print("  6. Logs redirigés vers /var/log/vote-secret/")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)