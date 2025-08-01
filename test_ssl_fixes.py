#!/usr/bin/env python3
"""
Test des corrections SSL Nginx Vote Secret v2.0
===============================================

Script de test pour valider les corrections apportées à la configuration SSL:
- Configuration HTTP temporaire sans références SSL
- Configuration SSL séparée pour après obtention certificats
- Logique en deux phases dans deploy_nginx.py

Auteur: Assistant AI
Version: 2.0.2
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

def test_nginx_http_config():
    """Test de la configuration HTTP temporaire (sans SSL)"""
    print_header("TEST CONFIGURATION HTTP TEMPORAIRE")
    
    try:  
        # Simuler la configuration avec deploy_environment.py
        sys.path.append('/app')
        from deploy_environment import ProductionEnvironmentSetup
        
        env_setup = ProductionEnvironmentSetup()
        env_setup.config = {
            'DOMAIN': 'vote.super-csn.ca',
            'SSL_MODE': 'letsencrypt',
            'RATE_LIMIT_REQUESTS': '60',
            'RATE_LIMIT_BURST': '10',
            'MONITORING_ENABLED': True,
            'METRICS_PORT': '9090'
        }
        
        # Générer la configuration HTTP temporaire
        http_config = env_setup._generate_nginx_config_http()
        
        # Vérifications
        checks = [
            ("Pas de références SSL", "ssl_certificate" not in http_config),
            ("Pas de listen 443", "listen 443" not in http_config),
            ("Présence listen 80", "listen 80" in http_config),
            ("Challenge ACME présent", "/.well-known/acme-challenge/" in http_config),
            ("Pas de redirection HTTPS", "return 301 https://" not in http_config),
            ("API routes présentes", "location /api/" in http_config),
            ("Frontend routes présentes", "location /" in http_config),
            ("Health check présent", "location /health" in http_config)
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
        print_error(f"Erreur test config HTTP: {e}")
        return False

def test_nginx_ssl_config():
    """Test de la configuration SSL finale"""
    print_header("TEST CONFIGURATION SSL FINALE")
    
    try:
        sys.path.append('/app')  
        from deploy_environment import ProductionEnvironmentSetup
        
        env_setup = ProductionEnvironmentSetup()
        env_setup.config = {
            'DOMAIN': 'vote.super-csn.ca',
            'SSL_MODE': 'letsencrypt',
            'RATE_LIMIT_REQUESTS': '60',
            'RATE_LIMIT_BURST': '10',
            'MONITORING_ENABLED': True,
            'METRICS_PORT': '9090'
        }
        
        # Générer la configuration SSL finale
        ssl_config = env_setup._generate_nginx_config_ssl()
        
        # Vérifications
        checks = [
            ("Certificats SSL présents", "/etc/letsencrypt/live/vote.super-csn.ca/fullchain.pem" in ssl_config),
            ("Listen 443 présent", "listen 443 ssl http2" in ssl_config),
            ("Redirection HTTP→HTTPS", "return 301 https://" in ssl_config),
            ("Challenge ACME accessible", "/.well-known/acme-challenge/" in ssl_config),
            ("HSTS header présent", "Strict-Transport-Security" in ssl_config),
            ("SSL protocols sécurisés", "ssl_protocols TLSv1.2 TLSv1.3" in ssl_config),
            ("API routes SSL", "location /api/" in ssl_config),
            ("Headers sécurité", "X-Frame-Options" in ssl_config)
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
        print_error(f"Erreur test config SSL: {e}")
        return False

def test_deploy_nginx_logic():
    """Test de la logique deploy_nginx.py corrigée"""
    print_header("TEST LOGIQUE DEPLOY_NGINX.PY")
    
    try:
        with open('/app/deploy_nginx.py', 'r') as f:
            content = f.read()
        
        # Vérifications
        checks = [
            ("Certbot certonly", "certbot certonly" in content),
            ("WebRoot method", "--webroot" in content),
            ("Configuration SSL séparée", "_generate_nginx_config_ssl" in content),
            ("Deux phases SSL", "Configuration Nginx avec SSL" in content),
            ("Test config SSL", "nginx -t" in content and "Test configuration SSL" in content),
            ("Rechargement après SSL", "systemctl reload nginx" in content),
            ("Pas d'usage --nginx", "certbot --nginx" not in content)  # Recherche spécifique de la commande problématique
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
        print_error(f"Erreur test deploy_nginx.py: {e}")
        return False

def test_file_generation():
    """Test de génération des fichiers de configuration"""
    print_header("TEST GÉNÉRATION FICHIERS CONFIGURATION")
    
    try:
        sys.path.append('/app')
        from deploy_environment import ProductionEnvironmentSetup
        
        env_setup = ProductionEnvironmentSetup()
        env_setup.config = {
            'DOMAIN': 'vote.super-csn.ca',
            'SSL_MODE': 'letsencrypt',
            'SSL_EMAIL': 'admin@super-csn.ca',
            'RATE_LIMIT_REQUESTS': '60',
            'RATE_LIMIT_BURST': '10',
            'MONITORING_ENABLED': True
        }
        
        # Test de génération sans erreurs
        http_config = env_setup._generate_nginx_config_http()
        ssl_config = env_setup._generate_nginx_config_ssl()
        
        # Vérifications basiques
        checks = [
            ("Config HTTP générée", len(http_config) > 1000),
            ("Config SSL générée", len(ssl_config) > 1000),
            ("Config HTTP valide", "server {" in http_config and "}" in http_config),
            ("Config SSL valide", "server {" in ssl_config and "}" in ssl_config),
            ("Domaine présent HTTP", "vote.super-csn.ca" in http_config),
            ("Domaine présent SSL", "vote.super-csn.ca" in ssl_config)
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

def test_syntax_validation():
    """Test de validation syntaxique des scripts modifiés"""
    print_header("TEST VALIDATION SYNTAXIQUE SCRIPTS MODIFIÉS")
    
    scripts_to_test = [
        '/app/deploy_environment.py',
        '/app/deploy_nginx.py'
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
    print_header("TESTS DES CORRECTIONS SSL NGINX")
    print_info("Validation des corrections apportées au problème SSL")
    
    tests = [
        ("Configuration HTTP Temporaire", test_nginx_http_config),
        ("Configuration SSL Finale", test_nginx_ssl_config),
        ("Logique Deploy Nginx", test_deploy_nginx_logic),
        ("Génération Fichiers", test_file_generation),
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
    print_header("RÉSUMÉ DES TESTS SSL")
    success_rate = (passed_tests / total_tests) * 100
    
    if passed_tests == total_tests:
        print_success(f"Tous les tests réussis: {passed_tests}/{total_tests} (100%)")
        print_info("Les corrections SSL sont validées!")
    else:
        print_error(f"Tests échoués: {total_tests - passed_tests}/{total_tests}")
        print_info(f"Taux de réussite: {success_rate:.1f}%")
    
    # Conseils d'utilisation
    print_header("SOLUTION AU PROBLÈME SSL")
    print_info("Problème résolu:")
    print("  ❌ AVANT: Configuration SSL créée avec certificats inexistants")
    print("  ✅ APRÈS: Configuration HTTP temporaire → Obtention certificats → Configuration SSL")
    print()
    print_info("Processus corrigé:")
    print("  1. deploy_environment.py génère nginx.conf (HTTP) et nginx-ssl.conf (SSL)")
    print("  2. deploy_nginx.py utilise d'abord la config HTTP")
    print("  3. Nginx démarre avec HTTP seulement")
    print("  4. certbot obtient les certificats via webroot")
    print("  5. deploy_nginx.py reconfigure avec nginx-ssl.conf")
    print("  6. Nginx redémarre avec SSL opérationnel")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)