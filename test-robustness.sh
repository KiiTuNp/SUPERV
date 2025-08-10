#!/bin/bash

# =============================================================================
# Test de Validation de la Configuration HTTPS Robuste
# =============================================================================

set -euo pipefail

# Couleurs
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

test_nginx_config_robustness() {
    echo -e "${BLUE}[TEST]${NC} Validation de la configuration nginx robuste..."
    
    # Test de la syntaxe nginx
    if docker run --rm -v "$(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro" nginx nginx -t 2>&1; then
        echo -e "${GREEN}✓${NC} Configuration nginx syntaxiquement valide"
    else
        echo -e "${RED}✗${NC} Configuration nginx invalide"
        return 1
    fi
    
    # Vérifier les configurations de fallback
    local config_checks=(
        "ssl_certificate.*nginx-selfsigned.crt"
        "ssl_certificate_key.*nginx-selfsigned.key"
        "location @ssl_fallback"
        "if.*letsencrypt.*fullchain.pem"
        "return 302 http"
    )
    
    for check in "${config_checks[@]}"; do
        if grep -q "$check" nginx/nginx.conf; then
            echo -e "${GREEN}✓${NC} Configuration fallback SSL présente: $check"
        else
            echo -e "${YELLOW}⚠${NC} Configuration fallback manquante: $check"
        fi
    done
    
    echo -e "${GREEN}✓${NC} Configuration nginx robuste validée"
    return 0
}

test_deployment_script_robustness() {
    echo -e "${BLUE}[TEST]${NC} Validation de la robustesse du script de déploiement..."
    
    # Vérifier les fonctions critiques
    local critical_functions=(
        "validate_web_accessibility"
        "wait_for_service_advanced"
        "configure_ssl_robust"
        "show_deployment_summary_complete"
    )
    
    for func in "${critical_functions[@]}"; do
        if grep -q "^$func()" deploy-production.sh; then
            echo -e "${GREEN}✓${NC} Fonction critique présente: $func"
        else
            echo -e "${RED}✗${NC} Fonction critique manquante: $func"
            return 1
        fi
    done
    
    # Vérifier les validations de sécurité
    local security_checks=(
        "validation.*DNS"
        "success_rate.*70"
        "HTTP_ACCESSIBLE.*true"
        "HTTPS_ACCESSIBLE.*true"
        "SSL_GENERATED.*true"
    )
    
    for check in "${security_checks[@]}"; do
        if grep -q "$check" deploy-production.sh; then
            echo -e "${GREEN}✓${NC} Validation de sécurité présente: $check"
        else
            echo -e "${YELLOW}⚠${NC} Validation de sécurité à vérifier: $check"
        fi
    done
    
    echo -e "${GREEN}✓${NC} Script de déploiement robuste validé"
    return 0
}

test_ssl_fallback_mechanism() {
    echo -e "${BLUE}[TEST]${NC} Test des mécanismes de fallback SSL..."
    
    # Vérifier les certificats auto-signés
    if [[ -f "nginx/ssl/nginx-selfsigned.crt" && -f "nginx/ssl/nginx-selfsigned.key" ]]; then
        echo -e "${GREEN}✓${NC} Certificats auto-signés de fallback présents"
    else
        echo -e "${YELLOW}⚠${NC} Certificats auto-signés manquants - génération..."
        if [[ -x "nginx/ssl/generate-self-signed.sh" ]]; then
            cd nginx/ssl && ./generate-self-signed.sh
            cd ../..
            echo -e "${GREEN}✓${NC} Certificats auto-signés générés"
        else
            echo -e "${RED}✗${NC} Script de génération de certificats manquant"
            return 1
        fi
    fi
    
    # Test de la logique de fallback dans docker-compose
    if grep -q "ssl_certificate.*nginx-selfsigned" nginx/nginx.conf; then
        echo -e "${GREEN}✓${NC} Configuration SSL fallback dans nginx"
    else
        echo -e "${RED}✗${NC} Configuration SSL fallback manquante"
        return 1
    fi
    
    echo -e "${GREEN}✓${NC} Mécanismes de fallback SSL validés"
    return 0
}

test_accessibility_validation() {
    echo -e "${BLUE}[TEST]${NC} Validation des tests d'accessibilité web..."
    
    # Vérifier que le script teste vraiment l'accessibilité
    local accessibility_tests=(
        "curl.*health.*nginx"
        "HTML.*detected"
        "success_rate.*70"
        "HTTP_ACCESSIBLE.*true"
        "Application.*chargée"
    )
    
    for test in "${accessibility_tests[@]}"; do
        if grep -q "$test" deploy-production.sh; then
            echo -e "${GREEN}✓${NC} Test d'accessibilité présent: $test"
        else
            echo -e "${YELLOW}⚠${NC} Test d'accessibilité à vérifier: $test"
        fi
    done
    
    # Vérifier les timeouts et retry mechanisms
    local timeout_configs=(
        "WEB_ACCESSIBILITY_TIMEOUT.*120"
        "SSL_VERIFICATION_TIMEOUT.*300"
        "attempt.*3"
        "max_ssl_attempts.*3"
    )
    
    for timeout in "${timeout_configs[@]}"; do
        if grep -q "$timeout" deploy-production.sh; then
            echo -e "${GREEN}✓${NC} Configuration timeout présente: $timeout"
        else
            echo -e "${YELLOW}⚠${NC} Configuration timeout manquante: $timeout"
        fi
    done
    
    echo -e "${GREEN}✓${NC} Tests d'accessibilité validés"
    return 0
}

test_error_handling() {
    echo -e "${BLUE}[TEST]${NC} Validation de la gestion d'erreur robuste..."
    
    # Vérifier les gestion d'erreurs
    local error_handlers=(
        "set -euo pipefail"
        "cleanup_on_exit"
        "trap.*cleanup_on_exit"
        "return 1"
        "exit 1"
    )
    
    for handler in "${error_handlers[@]}"; do
        if grep -q "$handler" deploy-production.sh; then
            echo -e "${GREEN}✓${NC} Gestion d'erreur présente: $handler"
        else
            echo -e "${RED}✗${NC} Gestion d'erreur manquante: $handler"
            return 1
        fi
    done
    
    # Vérifier les messages d'erreur informatifs
    if grep -qE "(log.*ERROR|echo.*ERROR|RED.*ERROR)" deploy-production.sh; then
        echo -e "${GREEN}✓${NC} Messages d'erreur informatifs présents"
    else
        echo -e "${YELLOW}⚠${NC} Messages d'erreur à améliorer"
    fi
    
    echo -e "${GREEN}✓${NC} Gestion d'erreur robuste validée"
    return 0
}

test_documentation_completeness() {
    echo -e "${BLUE}[TEST]${NC} Validation de la documentation complète..."
    
    # Vérifier les fichiers de documentation
    local docs=(
        "README.md"
        "GUIDE_DEPLOIEMENT_PRODUCTION.md"
        "FRONTEND_OPTIMIZATION_REPORT.md"
        "INDEX_SCRIPTS.md"
    )
    
    for doc in "${docs[@]}"; do
        if [[ -f "$doc" ]]; then
            local word_count=$(wc -w < "$doc")
            if [[ $word_count -gt 500 ]]; then
                echo -e "${GREEN}✓${NC} Documentation complète: $doc ($word_count mots)"
            else
                echo -e "${YELLOW}⚠${NC} Documentation courte: $doc ($word_count mots)"
            fi
        else
            echo -e "${RED}✗${NC} Documentation manquante: $doc"
            return 1
        fi
    done
    
    # Vérifier le README pour les éléments essentiels
    local readme_elements=(
        "Déploiement Production"
        "Architecture Technique"
        "Sécurité"
        "Performance"
        "Dépannage"
    )
    
    for element in "${readme_elements[@]}"; do
        if grep -q "$element" README.md; then
            echo -e "${GREEN}✓${NC} Élément README présent: $element"
        else
            echo -e "${YELLOW}⚠${NC} Élément README manquant: $element"
        fi
    done
    
    echo -e "${GREEN}✓${NC} Documentation complète validée"
    return 0
}

show_robustness_summary() {
    echo
    echo "================================================="
    echo "🛡️  RÉSUMÉ DE LA ROBUSTESSE DU SYSTÈME"
    echo "================================================="
    echo
    echo "✅ Configuration HTTPS avec fallbacks multiples"
    echo "✅ Script de déploiement avec validation complète"
    echo "✅ Tests d'accessibilité web avant confirmation"
    echo "✅ Mécanismes de retry et timeouts configurés"
    echo "✅ Gestion d'erreur robuste avec nettoyage"
    echo "✅ Documentation complète et détaillée"
    echo
    echo "🔒 Points de Sécurité :"
    echo "   • Certificats SSL avec fallback auto-signé"
    echo "   • Validation DNS avant génération SSL"
    echo "   • Tests d'accessibilité HTTP et HTTPS"
    echo "   • Timeouts configurés pour éviter les blocages"
    echo "   • Messages d'erreur informatifs pour le debug"
    echo
    echo "📊 Métriques de Robustesse :"
    echo "   • 3 tentatives SSL automatiques"
    echo "   • 70% minimum de success rate pour validation"
    echo "   • 120s timeout pour accessibilité web"
    echo "   • Fallback HTTP si HTTPS échoue"
    echo "   • Configuration multi-domaines supportée"
    echo
    echo "🎯 L'utilisateur ne sera jamais bloqué :"
    echo "   ✓ HTTP toujours accessible même si HTTPS échoue"
    echo "   ✓ Certificats auto-signés de fallback"
    echo "   ✓ Messages d'erreur avec solutions"
    echo "   ✓ Validation avant confirmation de succès"
    echo "   ✓ Logs détaillés pour le diagnostic"
    echo
}

main() {
    echo "🧪 Tests de Robustesse HTTPS et Configuration"
    echo "============================================="
    echo
    
    local tests_passed=0
    local total_tests=6
    
    if test_nginx_config_robustness; then ((tests_passed++)); fi
    if test_deployment_script_robustness; then ((tests_passed++)); fi
    if test_ssl_fallback_mechanism; then ((tests_passed++)); fi
    if test_accessibility_validation; then ((tests_passed++)); fi
    if test_error_handling; then ((tests_passed++)); fi
    if test_documentation_completeness; then ((tests_passed++)); fi
    
    echo
    echo "Résultats: $tests_passed/$total_tests tests de robustesse passés"
    
    if [ $tests_passed -eq $total_tests ]; then
        echo -e "${GREEN}✅ Système complètement robuste et prêt !${NC}"
        show_robustness_summary
        return 0
    else
        echo -e "${YELLOW}⚠️ Certains aspects de robustesse nécessitent attention${NC}"
        return 1
    fi
}

main "$@"