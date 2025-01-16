# Premium Web Application with Desktop Client

A full-stack subscription-based web application with an integrated desktop client. The system includes user authentication, Stripe subscription management, and a desktop application that's accessible only to subscribed users.

## System Architecture

### Web Application (Django)
- **Authentication System**: Custom user model with email/username login
- **Subscription Management**: Stripe integration for handling subscriptions
- **Case-insensitive Authentication**: Email and username handling is case-insensitive
- **Security Features**: CSP headers, CSRF protection, and secure session handling

### Desktop Application (PyWebView)
- **Authentication**: Connects to web app's API for user validation
- **Subscription Check**: Only allows access to users with active subscriptions
- **Cross-platform**: Works on Windows, macOS, and Linux

## Setup Guide

### 1. Environment Variables
Create a `.env` file in the webapp directory with the following variables:
```env
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DATABASE_URL=your_database_url
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
SUBSCRIPTION_PRICE_AMOUNT=500  # $5.00 in cents
SITE_URL=https://yourdomain.com
```

### 2. Database Setup
1. Create a PostgreSQL database
2. Update the `DATABASE_URL` in `.env` with your database credentials:
```
DATABASE_URL=postgres://user:password@host:port/database_name
```

### 3. Stripe Setup
1. Create a Stripe account
2. Get your API keys from the Stripe dashboard
3. Update the `.env` file with your Stripe keys
4. Set up a webhook in Stripe dashboard pointing to: `https://yourdomain.com/stripe/webhook/`

### 4. Web Application Deployment
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Collect static files:
```bash
python manage.py collectstatic
```

4. Configure your web server (Nginx configuration provided in `nginx/nginx.conf`)

### 5. Desktop Application Setup
1. Navigate to the desktop directory
2. Create a `.env` file:
```env
API_BASE_URL=https://yourdomain.com
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the desktop app:
```bash
python app.py
```

## Migrating to a New Server/Domain

### 1. Database Migration
1. Create a backup of your existing database:
```bash
pg_dump your_old_db > backup.sql
```

2. Restore to the new database:
```bash
psql your_new_db < backup.sql
```

### 2. Environment Updates

#### Web Application
1. Update `.env` file with new values:
   - `ALLOWED_HOSTS`
   - `CSRF_TRUSTED_ORIGINS`
   - `DATABASE_URL`
   - `SITE_URL`

2. Update Stripe webhook URL in Stripe dashboard to point to your new domain

#### Desktop Application
1. Update `.env` file:
   - `API_BASE_URL` to point to your new domain

### 3. DNS and SSL
1. Update DNS records to point to your new server
2. Generate new SSL certificates:
```bash
certbot certonly --webroot -w /var/www/certbot -d yourdomain.com -d www.yourdomain.com
```

### 4. Nginx Configuration
1. Update `nginx/nginx.conf`:
   - Server names
   - SSL certificate paths
   - Static/media file paths

## Security Considerations

### Web Application
- All passwords are hashed using Django's password hasher
- CSRF protection enabled for all POST requests
- CSP headers configured for security
- SSL/TLS required for all connections
- Case-insensitive email/username handling to prevent duplicate accounts

### Desktop Application
- Requires valid subscription for access
- Authentication token required for all operations
- API requests only work over HTTPS

## File Structure
```
webapp/
├── core/                 # Django project settings
├── main/                 # Main application
│   ├── models.py        # User and subscription models
│   ├── views.py         # Application views
│   ├── urls.py          # URL routing
│   └── stripe_utils.py  # Stripe integration utilities
├── templates/           # HTML templates
├── static/              # Static files
├── nginx/              # Nginx configuration
└── requirements.txt    # Python dependencies

desktop/
├── app.py             # Desktop application main file
├── index.html         # Desktop UI
├── requirements.txt   # Desktop app dependencies
└── .env              # Desktop environment variables
```

## Common Issues and Solutions

### Subscription Issues
1. **Webhook Failures**: Ensure Stripe webhook URL is correctly configured
2. **Payment Processing**: Check Stripe dashboard for payment logs
3. **Subscription Status**: Verify subscription_end dates in admin panel

### Authentication Issues
1. **Login Failures**: Check case-sensitivity of email/username
2. **Desktop Access**: Verify subscription status and API connectivity
3. **Token Errors**: Check CSRF token configuration

### Server Migration
1. **Database Connection**: Verify DATABASE_URL format and credentials
2. **Static Files**: Run collectstatic after migration
3. **SSL Certificates**: Ensure proper SSL certificate installation

## Support and Maintenance

### Regular Maintenance
1. Keep Django and dependencies updated
2. Monitor Stripe webhook logs
3. Backup database regularly
4. Check SSL certificate expiration

### Monitoring
1. Set up error logging
2. Monitor subscription status changes
3. Track failed login attempts
4. Monitor API endpoint performance

## Development and Testing

### Local Development
1. Set DEBUG=True in .env
2. Use SQLite for local database
3. Use Stripe test keys
4. Run development server:
```bash
python manage.py runserver
```

### Testing
1. Run Django tests:
```bash
python manage.py test
```

2. Test Stripe webhooks locally using Stripe CLI
3. Test desktop app with local API endpoint 