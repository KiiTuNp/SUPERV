#!/usr/bin/env python3
"""
Test des corrections de déploiement Vote Secret v2.0
====================================================

Script de test pour valider les corrections apportées aux scripts de déploiement:
- Installation MongoDB avec séquence correcte
- Vérification installation Nginx
- Support interactivité utilisateur

Auteur: Assistant AI
Version: 2.0.1
Date: 2025-01-31
"""

import os
import sys
import subprocess
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

def test_mongodb_sequence():
    """Test de la séquence MongoDB corrigée"""
    print_header("TEST DE LA SÉQUENCE MONGODB CORRIGÉE")
    
    # Lire le fichier deploy.py et vérifier les corrections
    try:
        with open('/app/deploy.py', 'r') as f:
            content = f.read()
            
        # Vérifications
        checks = [
            ("Installation gnupg curl", "sudo apt-get install gnupg curl" in content),
            ("Dépôt MongoDB jammy", "ubuntu jammy/mongodb-org/8.0 multiverse" in content),
            ("Pas de lsb_release", "$(lsb_release" not in content),
            ("Fonction interactive", "interactive: bool = False" in content),
            ("Mode interactif apt-get", "interactive = 'apt-get install' in command" in content)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print_success(f"{check_name}: Corrigé")
            else:
                print_error(f"{check_name}: Échec")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Erreur lecture deploy.py: {e}")
        return False

def test_nginx_verification():
    """Test de la vérification Nginx"""
    print_header("TEST DE LA VÉRIFICATION NGINX")
    
    try:
        with open('/app/deploy_nginx.py', 'r') as f:
            content = f.read()
            
        # Vérifications
        checks = [
            ("Vérification Nginx installé", "nginx -v" in content),
            ("Installation selon distribution", "_detect_distro()" in content),
            ("Fonction interactive", "interactive: bool = False" in content),
            ("Mode interactif installations", "interactive = any(cmd in command for cmd in" in content)
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
        print_error(f"Erreur lecture deploy_nginx.py: {e}")
        return False

def test_interactive_support():
    """Test du support interactif"""
    print_header("TEST DU SUPPORT INTERACTIF")
    
    scripts_to_test = [
        '/app/deploy.py',
        '/app/deploy_nginx.py',
        '/app/deploy_final.py'
    ]
    
    all_passed = True
    
    for script_path in scripts_to_test:
        script_name = Path(script_path).name
        try:
            with open(script_path, 'r') as f:
                content = f.read()
                
            # Vérifications
            has_interactive_param = "interactive: bool = False" in content
            has_interactive_logic = "if interactive:" in content
            has_command_display = "print(f\"{Colors.CYAN}Commande: {command}{Colors.ENDC}\")" in content
            
            if has_interactive_param and has_interactive_logic and has_command_display:
                print_success(f"{script_name}: Support interactif complet")
            else:
                print_error(f"{script_name}: Support interactif incomplet")
                all_passed = False
                
        except Exception as e:
            print_error(f"Erreur lecture {script_name}: {e}")
            all_passed = False
    
    return all_passed

def test_syntax_validation():
    """Test de validation syntaxique des scripts"""
    print_header("TEST DE VALIDATION SYNTAXIQUE")
    
    scripts_to_test = [
        '/app/deploy.py',
        '/app/deploy_nginx.py',
        '/app/deploy_final.py',
        '/app/deploy_master.py',
        '/app/deploy_environment.py'
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
    print_header("TESTS DES CORRECTIONS DE DÉPLOIEMENT")
    print_info("Validation des corrections apportées aux scripts de déploiement")
    
    tests = [
        ("Séquence MongoDB", test_mongodb_sequence),
        ("Vérification Nginx", test_nginx_verification),
        ("Support Interactif", test_interactive_support),
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
    print_header("RÉSUMÉ DES TESTS")
    success_rate = (passed_tests / total_tests) * 100
    
    if passed_tests == total_tests:
        print_success(f"Tous les tests réussis: {passed_tests}/{total_tests} (100%)")
        print_info("Les corrections de déploiement sont validées!")
    else:
        print_error(f"Tests échoués: {total_tests - passed_tests}/{total_tests}")
        print_info(f"Taux de réussite: {success_rate:.1f}%")
    
    # Conseils d'utilisation
    print_header("CONSEILS D'UTILISATION")
    print_info("Pour utiliser les scripts corrigés:")
    print("  1. python3 deploy_master.py - Script principal orchestrateur")
    print("  2. Les commandes interactives afficheront la commande avant exécution")
    print("  3. MongoDB utilisera la séquence d'installation corrigée")
    print("  4. Nginx sera vérifié avant configuration")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)