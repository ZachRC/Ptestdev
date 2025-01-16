# Deployment Guide

This guide will help you deploy this web application using Digital Ocean, Supabase, and set up your domain.

## Prerequisites

- A Digital Ocean account
- A Supabase account
- A domain name
- Stripe account (for subscription handling)

## Step 1: Database Setup (Supabase)

1. Create a new Supabase project
2. Go to Project Settings > Database
3. Copy your database connection string, it will look like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```
4. Save this for later use in your environment variables as `DATABASE_URL`

## Step 2: Digital Ocean Setup

1. Create a new Digital Ocean Droplet:
   - Choose Ubuntu 22.04 LTS
   - Select Basic Plan
   - Choose Regular CPU (Basic)
   - Select $6/mo plan (minimum recommended)
   - Choose a datacenter region close to your target audience
   - Add your SSH key or create a new one
   - Choose a hostname related to your project

2. Once created, note down your Droplet's IP address

3. SSH into your Droplet:
   ```bash
   ssh root@your_droplet_ip
   ```

4. Update system and install required packages:
   ```bash
   apt update && apt upgrade -y
   apt install python3-pip python3-venv nginx certbot python3-certbot-nginx -y
   ```

## Step 3: Domain Setup

1. Add DNS Records in your domain provider:
   - Add an A record:
     - Host: @ (or subdomain)
     - Points to: Your Droplet's IP
   - Add another A record:
     - Host: www
     - Points to: Your Droplet's IP

2. Wait for DNS propagation (can take up to 48 hours, usually much faster)

## Step 4: Project Setup

1. Clone this repository to your Droplet:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo/webapp
   ```

2. Create and edit your `.env` file:
   ```bash
   nano .env
   ```

3. Add the following environment variables:
   ```
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   DATABASE_URL=your-supabase-connection-string
   STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
   STRIPE_SECRET_KEY=your-stripe-secret-key
   SUBSCRIPTION_PRICE_AMOUNT=500
   SITE_URL=https://yourdomain.com
   ```

4. Set up Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

## Step 5: Nginx Configuration

1. Create Nginx configuration:
   ```bash
   nano /etc/nginx/sites-available/your-domain.com
   ```

2. Add this configuration (replace your-domain.com with your actual domain):
   ```nginx
   upstream webapp {
       server 127.0.0.1:8000;
   }

   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;
       
       location /.well-known/acme-challenge/ {
           root /var/www/certbot;
           try_files $uri =404;
       }

       location / {
           return 301 https://$host$request_uri;
       }
   }

   server {
       listen 443 ssl;
       server_name your-domain.com www.your-domain.com;

       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       location / {
           proxy_pass http://webapp;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static/ {
           alias /path/to/your/repo/webapp/staticfiles/;
           expires 30d;
           add_header Cache-Control "public, no-transform";
       }

       location /media/ {
           alias /path/to/your/repo/webapp/media/;
           expires 30d;
           add_header Cache-Control "public, no-transform";
       }
   }
   ```

3. Enable the site:
   ```bash
   ln -s /etc/nginx/sites-available/your-domain.com /etc/nginx/sites-enabled/
   rm /etc/nginx/sites-enabled/default
   nginx -t
   systemctl restart nginx
   ```

## Step 6: SSL Certificate

1. Get SSL certificate:
   ```bash
   certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

## Step 7: Gunicorn Setup

1. Create systemd service file:
   ```bash
   nano /etc/systemd/system/gunicorn.service
   ```

2. Add this configuration:
   ```ini
   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=root
   Group=www-data
   WorkingDirectory=/path/to/your/repo/webapp
   ExecStart=/path/to/your/repo/webapp/venv/bin/gunicorn core.wsgi:application --workers 3 --bind 127.0.0.1:8000

   [Install]
   WantedBy=multi-user.target
   ```

3. Start and enable Gunicorn:
   ```bash
   systemctl start gunicorn
   systemctl enable gunicorn
   ```

## Step 8: Stripe Setup

1. Go to Stripe Dashboard
2. Get your API keys (test or live)
3. Update your `.env` file with the keys
4. Set up webhook endpoints in Stripe Dashboard:
   - Add endpoint: https://your-domain.com/stripe/webhook/
   - Select events: customer.subscription.updated, customer.subscription.deleted

## Final Steps

1. Test your site by visiting https://your-domain.com
2. Create a test subscription to verify Stripe integration
3. Monitor your logs for any issues:
   ```bash
   tail -f /path/to/your/repo/webapp/django.log
   ```

## Common Issues

1. If static files aren't loading:
   ```bash
   python manage.py collectstatic --no-input
   ```

2. If database isn't connecting:
   - Verify DATABASE_URL in .env
   - Check Supabase firewall rules

3. If Stripe isn't working:
   - Verify webhook endpoints
   - Check STRIPE_* environment variables

## Security Notes

- Keep your .env file secure and never commit it to version control
- Regularly update your packages
- Monitor Nginx and Django logs for suspicious activity
- Set up regular database backups in Supabase 