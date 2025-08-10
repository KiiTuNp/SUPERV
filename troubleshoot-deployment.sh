#!/bin/bash

echo "=== GUIDE DE RESOLUTION DES PROBLEMES DE DEPLOIEMENT ==="
echo

show_help() {
    echo "Commandes disponibles :"
    echo "  diagnose    - Diagnostic complet du conflit de port"
    echo "  fix         - Correction automatique du conflit"
    echo "  alternative - Déploiement avec ports alternatifs"
    echo "  cleanup     - Nettoyage complet Docker"
    echo "  logs        - Affichage des logs Docker"
    echo "  restart     - Redémarrage des services"
    echo "  help        - Affichage de cette aide"
}

diagnose() {
    echo "🔍 Diagnostic en cours..."
    ./diagnose-port-conflict.sh
}

fix_conflict() {
    echo "🔧 Correction du conflit..."
    ./fix-port-conflict.sh
}

use_alternative_ports() {
    echo "🚀 Déploiement avec ports alternatifs..."
    ./deploy-with-alternative-ports.sh
}

cleanup_docker() {
    echo "🧹 Nettoyage Docker complet..."
    docker-compose down --volumes --remove-orphans
    docker system prune -af
    docker volume prune -f
    echo "✅ Nettoyage terminé"
}

show_logs() {
    echo "📋 Logs des containers..."
    if [ -n "$2" ]; then
        docker-compose logs -f "$2"
    else
        docker-compose logs --tail=50
    fi
}

restart_services() {
    echo "🔄 Redémarrage des services..."
    docker-compose down
    sleep 5
    docker-compose up -d
    echo "✅ Services redémarrés"
}

# Main command handling
case "${1:-help}" in
    diagnose)
        diagnose
        ;;
    fix)
        fix_conflict
        ;;
    alternative)
        use_alternative_ports
        ;;
    cleanup)
        cleanup_docker
        ;;
    logs)
        show_logs "$@"
        ;;
    restart)
        restart_services
        ;;
    help|*)
        show_help
        ;;
esac

echo
echo "=== ETAPES SUIVANTES ==="
echo "1. Si le problème persiste, vérifiez les logs : $0 logs"
echo "2. Pour un nettoyage complet : $0 cleanup"
echo "3. Pour redémarrer : $0 restart"