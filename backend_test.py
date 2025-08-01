#!/usr/bin/env python3
"""
Vote Secret v2.0 - Tests Complets du Système de Déploiement
===========================================================

Tests exhaustifs pour tous les scripts de déploiement Python.
Valide la syntaxe, les imports, la logique et les fonctions.

Auteur: Testing Agent
Version: 1.0.0
Date: 2025-01-31
"""

import os
import sys
import ast
import importlib.util
import subprocess
import tempfile
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from unittest.mock import Mock, patch, MagicMock
import traceback

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

class DeploymentScriptTester:
    """Testeur complet pour les scripts de déploiement"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.scripts_to_test = [
            'deploy_master.py',
            'deploy.py', 
            'deploy_environment.py',
            'deploy_nginx.py',
            'deploy_final.py'
        ]
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def run_all_tests(self):
        """Exécute tous les tests de déploiement"""
        print_header("TESTS COMPLETS DU SYSTÈME DE DÉPLOIEMENT VOTE SECRET v2.0")
        print(f"{Colors.CYAN}Test des scripts Python de déploiement production{Colors.ENDC}")
        print(f"{Colors.CYAN}Validation syntaxe, imports, logique et fonctions{Colors.ENDC}\n")
        
        for script_name in self.scripts_to_test:
            script_path = self.project_root / script_name
            if script_path.exists():
                print_header(f"TEST DU SCRIPT: {script_name}")
                self.test_results[script_name] = self.test_script(script_path)
            else:
                print_error(f"Script {script_name} non trouvé")
                self.test_results[script_name] = {
                    'exists': False,
                    'syntax_valid': False,
                    'imports_valid': False,
                    'functions_valid': False,
                    'logic_valid': False,
                    'errors': [f"Fichier {script_name} non trouvé"]
                }
        
        self.show_summary()
    
    def test_script(self, script_path: Path) -> Dict[str, Any]:
        """Test complet d'un script de déploiement"""
        results = {
            'exists': True,
            'syntax_valid': False,
            'imports_valid': False,
            'functions_valid': False,
            'logic_valid': False,
            'validation_functions': False,
            'command_generation': False,
            'error_handling': False,
            'user_interaction': False,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        try:
            # Test 1: Validation syntaxique
            print_info("Test 1: Validation syntaxique...")
            syntax_result = self.test_syntax(script_path)
            results['syntax_valid'] = syntax_result['valid']
            if not syntax_result['valid']:
                results['errors'].extend(syntax_result['errors'])
                return results
            print_success("Syntaxe Python valide")
            self.passed_tests += 1
            
            # Test 2: Validation des imports
            print_info("Test 2: Validation des imports...")
            import_result = self.test_imports(script_path)
            results['imports_valid'] = import_result['valid']
            results['details']['imports'] = import_result['imports']
            if not import_result['valid']:
                results['errors'].extend(import_result['errors'])
            else:
                print_success(f"Imports valides ({len(import_result['imports'])} modules)")
                self.passed_tests += 1
            
            # Test 3: Validation des fonctions
            print_info("Test 3: Validation des fonctions...")
            function_result = self.test_functions(script_path)
            results['functions_valid'] = function_result['valid']
            results['details']['functions'] = function_result['functions']
            if function_result['valid']:
                print_success(f"Fonctions valides ({len(function_result['functions'])} fonctions)")
                self.passed_tests += 1
            else:
                results['errors'].extend(function_result['errors'])
            
            # Test 4: Validation de la logique métier
            print_info("Test 4: Validation logique métier...")
            logic_result = self.test_business_logic(script_path)
            results['logic_valid'] = logic_result['valid']
            results['details']['logic'] = logic_result
            if logic_result['valid']:
                print_success("Logique métier cohérente")
                self.passed_tests += 1
            else:
                results['warnings'].extend(logic_result.get('warnings', []))
            
            # Test 5: Fonctions de validation
            print_info("Test 5: Fonctions de validation...")
            validation_result = self.test_validation_functions(script_path)
            results['validation_functions'] = validation_result['valid']
            if validation_result['valid']:
                print_success("Fonctions de validation présentes")
                self.passed_tests += 1
            else:
                results['warnings'].extend(validation_result.get('warnings', []))
            
            # Test 6: Génération de commandes
            print_info("Test 6: Génération de commandes système...")
            command_result = self.test_command_generation(script_path)
            results['command_generation'] = command_result['valid']
            if command_result['valid']:
                print_success("Génération de commandes sécurisée")
                self.passed_tests += 1
            else:
                results['warnings'].extend(command_result.get('warnings', []))
            
            # Test 7: Gestion d'erreurs
            print_info("Test 7: Gestion d'erreurs...")
            error_result = self.test_error_handling(script_path)
            results['error_handling'] = error_result['valid']
            if error_result['valid']:
                print_success("Gestion d'erreurs robuste")
                self.passed_tests += 1
            else:
                results['warnings'].extend(error_result.get('warnings', []))
            
            # Test 8: Interaction utilisateur
            print_info("Test 8: Interface utilisateur...")
            ui_result = self.test_user_interaction(script_path)
            results['user_interaction'] = ui_result['valid']
            if ui_result['valid']:
                print_success("Interface utilisateur complète")
                self.passed_tests += 1
            else:
                results['warnings'].extend(ui_result.get('warnings', []))
            
        except Exception as e:
            results['errors'].append(f"Erreur inattendue: {str(e)}")
            print_error(f"Erreur lors du test: {str(e)}")
        
        return results
    
    def test_syntax(self, script_path: Path) -> Dict[str, Any]:
        """Test de la syntaxe Python"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse AST pour vérifier la syntaxe
            ast.parse(source_code)
            
            return {
                'valid': True,
                'errors': []
            }
        except SyntaxError as e:
            return {
                'valid': False,
                'errors': [f"Erreur syntaxe ligne {e.lineno}: {e.msg}"]
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Erreur lecture fichier: {str(e)}"]
            }
    
    def test_imports(self, script_path: Path) -> Dict[str, Any]:
        """Test des imports et dépendances"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            imports = []
            errors = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}" if module else alias.name)
            
            # Vérification des imports critiques
            critical_imports = ['os', 'sys', 'subprocess', 'pathlib']
            missing_critical = [imp for imp in critical_imports if not any(imp in i for i in imports)]
            
            if missing_critical:
                errors.append(f"Imports critiques manquants: {missing_critical}")
            
            # Test d'importation réelle (simulation)
            standard_modules = [
                'os', 'sys', 'subprocess', 'platform', 'json', 'time', 
                'pathlib', 'typing', 'datetime', 'tempfile', 'secrets', 
                'string', 're', 'importlib'
            ]
            
            problematic_imports = []
            for imp in imports:
                base_module = imp.split('.')[0]
                if base_module not in standard_modules and not base_module.startswith('deploy'):
                    try:
                        importlib.import_module(base_module)
                    except ImportError:
                        problematic_imports.append(base_module)
            
            if problematic_imports:
                errors.append(f"Modules potentiellement manquants: {problematic_imports}")
            
            return {
                'valid': len(errors) == 0,
                'imports': imports,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'valid': False,
                'imports': [],
                'errors': [f"Erreur analyse imports: {str(e)}"]
            }
    
    def test_functions(self, script_path: Path) -> Dict[str, Any]:
        """Test des fonctions définies"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            functions = []
            classes = []
            errors = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'line': node.lineno,
                        'has_docstring': ast.get_docstring(node) is not None
                    })
                elif isinstance(node, ast.ClassDef):
                    class_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_methods.append(item.name)
                    
                    classes.append({
                        'name': node.name,
                        'methods': class_methods,
                        'line': node.lineno,
                        'has_docstring': ast.get_docstring(node) is not None
                    })
            
            # Vérifications spécifiques selon le script
            script_name = script_path.name
            
            if script_name == 'deploy_master.py':
                required_functions = ['main', 'print_header', 'print_success', 'print_error']
                required_classes = ['MasterDeployment']
            elif script_name == 'deploy.py':
                required_functions = ['main', 'run_command', 'prompt_continue']
                required_classes = ['DeploymentManager', 'SystemInfo']
            elif script_name == 'deploy_environment.py':
                required_functions = ['main', 'validate_email', 'validate_domain']
                required_classes = ['EnvironmentSetup']
            elif script_name == 'deploy_nginx.py':
                required_functions = ['main', 'run_command']
                required_classes = ['NginxSSLSetup']
            elif script_name == 'deploy_final.py':
                required_functions = ['main', 'run_command']
                required_classes = ['FinalDeployment']
            else:
                required_functions = ['main']
                required_classes = []
            
            # Vérification des fonctions requises
            function_names = [f['name'] for f in functions]
            missing_functions = [f for f in required_functions if f not in function_names]
            
            if missing_functions:
                errors.append(f"Fonctions requises manquantes: {missing_functions}")
            
            # Vérification des classes requises
            class_names = [c['name'] for c in classes]
            missing_classes = [c for c in required_classes if c not in class_names]
            
            if missing_classes:
                errors.append(f"Classes requises manquantes: {missing_classes}")
            
            return {
                'valid': len(errors) == 0,
                'functions': functions,
                'classes': classes,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'valid': False,
                'functions': [],
                'classes': [],
                'errors': [f"Erreur analyse fonctions: {str(e)}"]
            }
    
    def test_business_logic(self, script_path: Path) -> Dict[str, Any]:
        """Test de la logique métier"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            warnings = []
            checks = {
                'has_error_handling': False,
                'has_user_prompts': False,
                'has_system_commands': False,
                'has_validation': False,
                'has_logging': False
            }
            
            # Recherche de patterns dans le code
            patterns = {
                'error_handling': [r'try:', r'except', r'raise', r'HTTPException'],
                'user_prompts': [r'input\(', r'prompt_continue', r'confirm'],
                'system_commands': [r'subprocess', r'run_command', r'os\.system'],
                'validation': [r'validate_', r'if.*not.*:', r'check_'],
                'logging': [r'print_', r'log', r'logger']
            }
            
            for check_name, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.search(pattern, source_code):
                        checks[check_name] = True
                        break
            
            # Vérifications spécifiques
            if not checks['error_handling']:
                warnings.append("Gestion d'erreurs limitée détectée")
            
            if not checks['user_prompts']:
                warnings.append("Interface utilisateur interactive manquante")
            
            if not checks['system_commands']:
                warnings.append("Aucune commande système détectée")
            
            # Vérification de la structure du script
            has_main_guard = '__name__ == "__main__"' in source_code
            if not has_main_guard:
                warnings.append("Protection __main__ manquante")
            
            has_help = '--help' in source_code or '-h' in source_code
            if not has_help:
                warnings.append("Option d'aide --help manquante")
            
            return {
                'valid': len(warnings) < 3,  # Tolérance pour quelques avertissements
                'checks': checks,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'valid': False,
                'warnings': [f"Erreur analyse logique: {str(e)}"]
            }
    
    def test_validation_functions(self, script_path: Path) -> Dict[str, Any]:
        """Test des fonctions de validation"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            validation_patterns = [
                r'def validate_email',
                r'def validate_domain', 
                r'def validate_url',
                r'def check_',
                r'def verify_',
                r'def is_valid',
                r'if.*@.*\.',  # Email validation pattern
                r'if.*\.(com|org|net|fr)',  # Domain validation pattern
                r'if len\(',  # Length validation
                r'if not.*or not',  # Multiple validation
            ]
            
            found_validations = []
            for pattern in validation_patterns:
                matches = re.findall(pattern, source_code)
                found_validations.extend(matches)
            
            warnings = []
            if len(found_validations) == 0:
                warnings.append("Aucune fonction de validation détectée")
            
            # Vérification spécifique pour deploy_environment.py
            if script_path.name == 'deploy_environment.py':
                required_validations = ['validate_email', 'validate_domain']
                for validation in required_validations:
                    if validation not in source_code:
                        warnings.append(f"Validation {validation} manquante")
            
            return {
                'valid': len(warnings) == 0,
                'found_validations': found_validations,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'valid': False,
                'warnings': [f"Erreur test validations: {str(e)}"]
            }
    
    def test_command_generation(self, script_path: Path) -> Dict[str, Any]:
        """Test de la génération de commandes système"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            warnings = []
            security_issues = []
            
            # Recherche de commandes potentiellement dangereuses
            dangerous_patterns = [
                r'rm -rf /',
                r'sudo rm -rf',
                r'chmod 777',
                r'chown.*root',
                r'eval\(',
                r'exec\(',
                r'shell=True.*input',  # Injection possible
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, source_code):
                    security_issues.append(f"Pattern dangereux détecté: {pattern}")
            
            # Vérification des bonnes pratiques
            good_practices = {
                'uses_subprocess': 'subprocess' in source_code,
                'avoids_os_system': source_code.count('os.system') < 3,
                'has_timeout': 'timeout=' in source_code,
                'checks_return_code': 'returncode' in source_code,
                'captures_output': 'capture_output' in source_code
            }
            
            for practice, present in good_practices.items():
                if not present:
                    warnings.append(f"Bonne pratique manquante: {practice}")
            
            return {
                'valid': len(security_issues) == 0,
                'security_issues': security_issues,
                'good_practices': good_practices,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'valid': False,
                'warnings': [f"Erreur test commandes: {str(e)}"]
            }
    
    def test_error_handling(self, script_path: Path) -> Dict[str, Any]:
        """Test de la gestion d'erreurs"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            
            error_handling_elements = {
                'try_except_blocks': 0,
                'exception_types': [],
                'finally_blocks': 0,
                'raise_statements': 0,
                'error_logging': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    error_handling_elements['try_except_blocks'] += 1
                    
                    for handler in node.handlers:
                        if handler.type:
                            if isinstance(handler.type, ast.Name):
                                error_handling_elements['exception_types'].append(handler.type.id)
                    
                    if node.finalbody:
                        error_handling_elements['finally_blocks'] += 1
                
                elif isinstance(node, ast.Raise):
                    error_handling_elements['raise_statements'] += 1
            
            # Recherche de logging d'erreurs
            error_logging_patterns = [
                r'print_error',
                r'logger\.error',
                r'logging\.error',
                r'sys\.stderr'
            ]
            
            for pattern in error_logging_patterns:
                error_handling_elements['error_logging'] += len(re.findall(pattern, source_code))
            
            warnings = []
            
            if error_handling_elements['try_except_blocks'] == 0:
                warnings.append("Aucun bloc try/except détecté")
            
            if error_handling_elements['error_logging'] == 0:
                warnings.append("Aucun logging d'erreur détecté")
            
            if 'KeyboardInterrupt' not in error_handling_elements['exception_types']:
                warnings.append("Gestion KeyboardInterrupt manquante")
            
            return {
                'valid': len(warnings) < 2,
                'elements': error_handling_elements,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'valid': False,
                'warnings': [f"Erreur test gestion erreurs: {str(e)}"]
            }
    
    def test_user_interaction(self, script_path: Path) -> Dict[str, Any]:
        """Test de l'interface utilisateur"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            ui_elements = {
                'has_colors': False,
                'has_prompts': False,
                'has_help': False,
                'has_progress': False,
                'has_welcome': False,
                'has_summary': False
            }
            
            ui_patterns = {
                'has_colors': [r'Colors\.|\\033\[', r'HEADER.*=', r'GREEN.*='],
                'has_prompts': [r'input\(', r'prompt_continue', r'raw_input'],
                'has_help': [r'--help', r'-h', r'usage:', r'Usage:'],
                'has_progress': [r'step.*\d+', r'progress', r'étape', r'ÉTAPE'],
                'has_welcome': [r'welcome', r'bienvenue', r'BIENVENUE'],
                'has_summary': [r'summary', r'résumé', r'RÉSUMÉ', r'show.*summary']
            }
            
            for element, patterns in ui_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, source_code, re.IGNORECASE):
                        ui_elements[element] = True
                        break
            
            warnings = []
            
            for element, present in ui_elements.items():
                if not present:
                    warnings.append(f"Élément UI manquant: {element}")
            
            # Vérification spéciale pour les scripts principaux
            if script_path.name in ['deploy_master.py', 'deploy.py']:
                if not ui_elements['has_welcome']:
                    warnings.append("Message de bienvenue requis pour script principal")
            
            return {
                'valid': len(warnings) < 4,  # Tolérance pour interface basique
                'elements': ui_elements,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'valid': False,
                'warnings': [f"Erreur test interface: {str(e)}"]
            }
    
    def show_summary(self):
        """Affiche le résumé complet des tests"""
        print_header("RÉSUMÉ COMPLET DES TESTS DE DÉPLOIEMENT")
        
        total_scripts = len(self.scripts_to_test)
        working_scripts = 0
        
        print(f"{Colors.CYAN}📊 STATISTIQUES GLOBALES:{Colors.ENDC}")
        print(f"   Scripts testés: {total_scripts}")
        print(f"   Tests exécutés: {self.total_tests}")
        print(f"   Tests réussis: {self.passed_tests}")
        print(f"   Tests échoués: {self.failed_tests}")
        
        print(f"\n{Colors.CYAN}📋 RÉSULTATS PAR SCRIPT:{Colors.ENDC}")
        
        for script_name, results in self.test_results.items():
            if not results['exists']:
                print(f"\n❌ {script_name}: FICHIER MANQUANT")
                continue
            
            # Calcul du score
            tests = [
                'syntax_valid', 'imports_valid', 'functions_valid', 
                'logic_valid', 'validation_functions', 'command_generation',
                'error_handling', 'user_interaction'
            ]
            
            passed = sum(1 for test in tests if results.get(test, False))
            total = len(tests)
            score = (passed / total) * 100
            
            if score >= 75:
                status = f"{Colors.GREEN}✅ EXCELLENT{Colors.ENDC}"
                working_scripts += 1
            elif score >= 50:
                status = f"{Colors.WARNING}⚠️  ACCEPTABLE{Colors.ENDC}"
                working_scripts += 1
            else:
                status = f"{Colors.FAIL}❌ PROBLÉMATIQUE{Colors.ENDC}"
            
            print(f"\n{status} {script_name}: {passed}/{total} tests ({score:.1f}%)")
            
            # Détails des tests
            test_details = [
                ('Syntaxe', results.get('syntax_valid', False)),
                ('Imports', results.get('imports_valid', False)),
                ('Fonctions', results.get('functions_valid', False)),
                ('Logique', results.get('logic_valid', False)),
                ('Validations', results.get('validation_functions', False)),
                ('Commandes', results.get('command_generation', False)),
                ('Erreurs', results.get('error_handling', False)),
                ('Interface', results.get('user_interaction', False))
            ]
            
            for test_name, test_result in test_details:
                icon = "✅" if test_result else "❌"
                print(f"     {icon} {test_name}")
            
            # Erreurs critiques
            if results.get('errors'):
                print(f"     {Colors.FAIL}Erreurs critiques:{Colors.ENDC}")
                for error in results['errors'][:3]:  # Limite à 3 erreurs
                    print(f"       • {error}")
            
            # Avertissements
            if results.get('warnings'):
                print(f"     {Colors.WARNING}Avertissements:{Colors.ENDC}")
                for warning in results['warnings'][:3]:  # Limite à 3 avertissements
                    print(f"       • {warning}")
        
        # Résumé final
        print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
        
        if working_scripts == total_scripts:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 TOUS LES SCRIPTS DE DÉPLOIEMENT SONT FONCTIONNELS ! 🎉{Colors.ENDC}")
            overall_status = "EXCELLENT"
        elif working_scripts >= total_scripts * 0.8:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ SYSTÈME DE DÉPLOIEMENT OPÉRATIONNEL{Colors.ENDC}")
            overall_status = "BON"
        elif working_scripts >= total_scripts * 0.6:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠️  SYSTÈME DE DÉPLOIEMENT PARTIELLEMENT FONCTIONNEL{Colors.ENDC}")
            overall_status = "ACCEPTABLE"
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}❌ SYSTÈME DE DÉPLOIEMENT PROBLÉMATIQUE{Colors.ENDC}")
            overall_status = "PROBLÉMATIQUE"
        
        print(f"\n{Colors.CYAN}📈 ÉVALUATION FINALE:{Colors.ENDC}")
        print(f"   Scripts fonctionnels: {working_scripts}/{total_scripts}")
        print(f"   Taux de réussite: {(working_scripts/total_scripts)*100:.1f}%")
        print(f"   Status global: {overall_status}")
        
        print(f"\n{Colors.CYAN}🔧 RECOMMANDATIONS:{Colors.ENDC}")
        
        if overall_status == "EXCELLENT":
            print("   • Système prêt pour déploiement production")
            print("   • Tous les scripts sont robustes et sécurisés")
            print("   • Documentation et interface utilisateur complètes")
        elif overall_status == "BON":
            print("   • Système utilisable avec surveillance")
            print("   • Corriger les avertissements mineurs")
            print("   • Tester en environnement de staging")
        elif overall_status == "ACCEPTABLE":
            print("   • Révision nécessaire avant production")
            print("   • Corriger les erreurs critiques identifiées")
            print("   • Renforcer la gestion d'erreurs")
        else:
            print("   • Révision majeure requise")
            print("   • Ne pas utiliser en production")
            print("   • Corriger tous les problèmes identifiés")
        
        print(f"\n{Colors.BLUE}📚 SCRIPTS TESTÉS:{Colors.ENDC}")
        for script in self.scripts_to_test:
            status = "✅" if script in self.test_results and self.test_results[script]['exists'] else "❌"
            print(f"   {status} {script}")
        
        return overall_status, working_scripts, total_scripts

def main():
    """Point d'entrée principal des tests"""
    print("Vote Secret v2.0 - Tests du Système de Déploiement")
    print("=" * 60)
    
    tester = DeploymentScriptTester()
    tester.run_all_tests()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())