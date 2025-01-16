#!/bin/bash

# Stop execution if a command fails
set -e

domains=(reachero.com www.reachero.com)
rsa_key_size=4096
data_path="./certbot"
email="zacharyrcherney@gmail.com"
staging=1 # Set to 0 once testing is complete

# Make sure docker-compose is down
docker-compose down

# Remove any existing certificates
rm -rf "$data_path"

# Create the required directories
mkdir -p "$data_path/www"
mkdir -p "$data_path/conf/live/reachero.com"

# Download TLS parameters
echo "### Downloading recommended TLS parameters ..."
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"

# Create dummy certificates
echo "### Creating dummy certificate for ${domains[0]} ..."
openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1\
  -keyout "$data_path/conf/live/reachero.com/privkey.pem" \
  -out "$data_path/conf/live/reachero.com/fullchain.pem" \
  -subj '/CN=localhost' 2>/dev/null

# Start nginx
echo "### Starting nginx ..."
docker-compose up -d nginx

# Wait for nginx to start
echo "### Waiting for nginx to start ..."
sleep 10

# Request the real certificate
echo "### Requesting Let's Encrypt certificate for ${domains[*]} ..."
docker-compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    --email $email \
    --agree-tos \
    --no-eff-email \
    --staging \
    --force-renewal \
    -d reachero.com -d www.reachero.com" certbot

echo "### Reloading nginx ..."
docker-compose exec nginx nginx -s reload 