#!/bin/bash

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create necessary directories
mkdir -p static media staticfiles

# Stop and remove existing containers and volumes
docker-compose down -v

# Clean up old images
docker system prune -f

# Pull latest changes
git pull origin main

# Build and start containers
docker-compose up --build -d

# Wait for web service to be ready
echo "Waiting for web service to be ready..."
sleep 10

# Test database connection
max_retries=5
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if docker-compose exec web python manage.py migrate --check; then
        echo "Database connection successful"
        break
    else
        echo "Database connection failed, retrying in 5 seconds..."
        sleep 5
        retry_count=$((retry_count + 1))
    fi
done

if [ $retry_count -eq $max_retries ]; then
    echo "Failed to connect to database after $max_retries attempts"
    exit 1
fi

# Apply database migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Restart Nginx
docker-compose restart nginx

echo "Deployment completed successfully!" 