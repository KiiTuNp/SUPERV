#!/bin/bash

echo "=== DIAGNOSTIC DU CONFLIT DE PORT 80/443 ==="
echo

echo "1. Services utilisant le port 80 :"
sudo netstat -tlnp | grep :80 || echo "Aucun service trouvé sur le port 80"
echo

echo "2. Services utilisant le port 443 :"
sudo netstat -tlnp | grep :443 || echo "Aucun service trouvé sur le port 443"
echo

echo "3. Processus nginx/apache en cours :"
ps aux | grep -E "(nginx|apache)" | grep -v grep || echo "Aucun processus nginx/apache trouvé"
echo

echo "4. Containers Docker en cours d'exécution :"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

echo "5. Containers Docker utilisant les ports 80/443 :"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E ":(80|443)->" || echo "Aucun container Docker utilisant les ports 80/443"
echo

echo "6. Services systemd actifs (nginx/apache) :"
sudo systemctl is-active nginx 2>/dev/null && echo "nginx: actif" || echo "nginx: inactif"
sudo systemctl is-active apache2 2>/dev/null && echo "apache2: actif" || echo "apache2: inactif"
sudo systemctl is-active httpd 2>/dev/null && echo "httpd: actif" || echo "httpd: inactif"
echo

echo "=== FIN DU DIAGNOSTIC ==="