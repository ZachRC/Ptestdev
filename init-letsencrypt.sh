#!/bin/bash

# Stop execution if a command fails
set -e

domains=(solforge.live www.solforge.live)
rsa_key_size=4096
data_path="./certbot"
email="zacharyrcherney@gmail.com"
staging=1 # Set to 0 once testing is complete

echo "### Creating directory structure"
mkdir -p "$data_path/conf/live/$domains"

echo "### Downloading recommended TLS parameters ..."
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"

echo "### Removing old certificates ..."
docker-compose down
rm -rf "$data_path/conf/live"
mkdir -p "$data_path/conf/live"

echo "### Creating dummy certificate ..."
openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout "$data_path/conf/live/$domains/privkey.pem" \
    -out "$data_path/conf/live/$domains/fullchain.pem" \
    -subj '/CN=localhost'

echo "### Starting nginx ..."
docker-compose up -d nginx

echo "### Waiting for nginx to start ..."
sleep 5

echo "### Requesting Let's Encrypt certificate for ${domains[*]} ..."
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $email \
    --agree-tos \
    --no-eff-email \
    --staging \
    --force-renewal \
    ${staging:+"--staging"} \
    ${domains[@]/#/-d }

echo "### Reloading nginx ..."
docker-compose exec nginx nginx -s reload 