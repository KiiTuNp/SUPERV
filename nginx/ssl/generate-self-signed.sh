#!/bin/bash
# Génération de certificats auto-signés pour l'initialisation

mkdir -p /etc/nginx/ssl

# Générer la clé privée
openssl genrsa -out /etc/nginx/ssl/nginx-selfsigned.key 2048

# Générer le certificat auto-signé
openssl req -new -x509 \
    -key /etc/nginx/ssl/nginx-selfsigned.key \
    -out /etc/nginx/ssl/nginx-selfsigned.crt \
    -days 365 \
    -subj "/C=CA/ST=QC/L=Montreal/O=VoteSecret/OU=IT/CN=localhost"

echo "✅ Certificats auto-signés générés dans /etc/nginx/ssl/"