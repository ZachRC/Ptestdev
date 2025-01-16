# Premium Web Application with Desktop Client

A full-stack subscription-based web application with an integrated desktop client. The system includes user authentication, Stripe subscription management, and a desktop task management application that's accessible only to subscribed users.

## System Components

### Web Application
- Django-based web application
- Custom user model with case-insensitive email/username authentication
- Stripe subscription integration ($5/month)
- Modern UI with Tailwind CSS

### Desktop Application
- PyWebView-based task management app
- Requires active subscription to access
- Real-time task management with priority levels

## Initial Setup

### Web Application (.env)
Create a `.env` file in the webapp directory with these exact variables:
```env
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DATABASE_URL=postgres://user:password@localhost:5432/dbname
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
SUBSCRIPTION_PRICE_AMOUNT=500
SITE_URL=https://yourdomain.com
```

### Desktop Application (.env)
Create a `.env` file in the desktop directory:
```env
API_BASE_URL=https://yourdomain.com
```

## Deployment Process

### First-Time Deployment
1. On your VPS:
```bash
# Clone the repository
git clone your-repo-url
cd your-repo-directory

# Create and set up .env file
nano webapp/.env
# Add the environment variables as shown above

# Run initialization script
./init-letsencrypt.sh

# Deploy the application
./deploy.sh
```

### Updates/Changes Deployment
1. On your local machine:
```bash
# Push changes to GitHub
git add .
git commit -m "your commit message"
git push origin main
```

2. On your VPS:
```bash
# Navigate to project directory
cd your-repo-directory

# Pull latest changes
git pull

# Deploy updates
./deploy.sh
```

## Changing Domain/Server

### 1. Database Backup (Optional - If Moving Servers)
```bash
# On old server
pg_dump -U your_db_user your_db_name > backup.sql

# On new server
psql -U your_db_user your_db_name < backup.sql
```

### 2. Update Web Application
1. Update `.env` file with new domain:
```env
ALLOWED_HOSTS=newdomain.com,www.newdomain.com
CSRF_TRUSTED_ORIGINS=https://newdomain.com,https://www.newdomain.com
SITE_URL=https://newdomain.com
```

2. Update Nginx configuration in `nginx/nginx.conf`:
```nginx
server_name newdomain.com www.newdomain.com;
```

3. Run SSL setup:
```bash
./init-letsencrypt.sh
```

4. Deploy changes:
```bash
./deploy.sh
```

### 3. Update Desktop Application
1. Update `.env` file:
```env
API_BASE_URL=https://newdomain.com
```

## Features and Usage

### User Management
- Case-insensitive email/username login
- Profile management (email, username, password updates)
- Account deletion with automatic subscription cancellation

### Subscription Management
- $5/month subscription using Stripe
- Automatic access management
- Subscription cancellation with remaining time honored

### Desktop Application
- Available only to subscribed users
- Task management with priority levels
- Real-time updates
- Secure authentication with web application

## File Structure
```
webapp/
├── core/                 # Project settings
│   ├── settings.py      # Main settings file
│   └── urls.py          # Main URL routing
├── main/                # Main application
│   ├── models.py        # User and subscription models
│   ├── views.py         # Views and API endpoints
│   ├── urls.py          # App URL routing
│   └── stripe_utils.py  # Stripe integration
├── templates/           # HTML templates
├── static/              # Static files
├── nginx/              # Nginx configuration
├── init-letsencrypt.sh # SSL setup script
├── deploy.sh           # Deployment script
└── requirements.txt    # Python dependencies

desktop/
├── app.py             # Desktop app main file
├── index.html         # Desktop UI
├── requirements.txt   # Dependencies
└── .env              # Configuration
```

## Common Issues

### Deployment Issues
1. **Permission Errors**:
   ```bash
   chmod +x deploy.sh
   chmod +x init-letsencrypt.sh
   ```

2. **Database Connection**:
   - Verify PostgreSQL is running
   - Check DATABASE_URL format
   - Ensure database user permissions

3. **SSL Certificate**:
   - Run `init-letsencrypt.sh` for new domains
   - Check certificate renewal status

### Application Issues
1. **Subscription Not Recognized**:
   - Check Stripe keys in .env
   - Verify subscription_end date in admin panel
   - Ensure subscription_status is correct

2. **Desktop App Connection**:
   - Verify API_BASE_URL in desktop/.env
   - Check subscription status
   - Ensure CORS settings in Django

## Development Setup

### Local Development
1. Set up local environment:
```bash
# Clone repository
git clone your-repo-url
cd your-repo-directory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r webapp/requirements.txt
pip install -r desktop/requirements.txt

# Set up .env files for development
# webapp/.env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_key
STRIPE_SECRET_KEY=sk_test_your_test_key
SITE_URL=http://localhost:8000

# desktop/.env
API_BASE_URL=http://localhost:8000
```

2. Run development servers:
```bash
# Web application
python webapp/manage.py runserver

# Desktop application (in separate terminal)
python desktop/app.py
```

## Security Notes
- All passwords are hashed using Django's password hasher
- Email/username comparisons are case-insensitive
- CSRF protection enabled for all POST requests
- SSL required in production
- Desktop app requires valid subscription token 