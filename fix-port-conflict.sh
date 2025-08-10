#!/bin/bash

echo "=== RESOLUTION DU CONFLIT DE PORT ==="
echo

# Function to stop conflicting services
stop_conflicting_services() {
    echo "Arrêt des services web conflictuels..."
    
    # Stop nginx if running
    if sudo systemctl is-active --quiet nginx; then
        echo "Arrêt de nginx systemd..."
        sudo systemctl stop nginx
        sudo systemctl disable nginx
    fi
    
    # Stop apache if running
    if sudo systemctl is-active --quiet apache2; then
        echo "Arrêt d'apache2 systemd..."
        sudo systemctl stop apache2
        sudo systemctl disable apache2
    fi
    
    # Stop httpd if running
    if sudo systemctl is-active --quiet httpd; then
        echo "Arrêt d'httpd systemd..."
        sudo systemctl stop httpd
        sudo systemctl disable httpd
    fi
}

# Function to clean old Docker containers
clean_old_containers() {
    echo "Nettoyage des anciens containers Docker..."
    
    # Stop and remove containers with vote-secret prefix
    docker ps -a --format "{{.Names}}" | grep "vote-secret" | xargs -r docker stop
    docker ps -a --format "{{.Names}}" | grep "vote-secret" | xargs -r docker rm
    
    # Remove containers using ports 80/443
    docker ps -a --format "{{.Names}} {{.Ports}}" | grep -E ":(80|443)->" | awk '{print $1}' | xargs -r docker stop
    docker ps -a --format "{{.Names}} {{.Ports}}" | grep -E ":(80|443)->" | awk '{print $1}' | xargs -r docker rm
    
    echo "Containers nettoyés."
}

# Function to clean Docker system
clean_docker_system() {
    echo "Nettoyage du système Docker..."
    docker system prune -f
    docker network prune -f
    docker volume prune -f
}

# Main execution
echo "Choisissez une action :"
echo "1. Arrêter les services web conflictuels (nginx/apache)"
echo "2. Nettoyer les anciens containers Docker"
echo "3. Nettoyage complet (services + containers + système Docker)"
echo "4. Diagnostic seulement"

read -p "Votre choix (1-4): " choice

case $choice in
    1)
        stop_conflicting_services
        ;;
    2)
        clean_old_containers
        ;;
    3)
        stop_conflicting_services
        clean_old_containers
        clean_docker_system
        ;;
    4)
        echo "Exécution du diagnostic..."
        ./diagnose-port-conflict.sh
        ;;
    *)
        echo "Choix invalide. Utilisation : $0 [1-4]"
        exit 1
        ;;
esac

echo
echo "=== VERIFICATION POST-CORRECTION ==="
echo "Ports 80/443 maintenant libres :"
sudo netstat -tlnp | grep -E ":(80|443) " || echo "✅ Ports 80 et 443 sont maintenant libres"

echo
echo "Vous pouvez maintenant relancer le déploiement avec :"
echo "docker-compose up -d"