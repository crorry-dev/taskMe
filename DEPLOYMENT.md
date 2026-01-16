# TaskMe Deployment Guide

This guide provides instructions for deploying TaskMe to production environments.

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 13+
- nginx or similar web server
- SSL certificate
- Domain name

## Environment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.12 python3.12-venv python3-pip postgresql postgresql-contrib nginx git
```

### 2. Database Setup

```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE taskme_db;
CREATE USER taskme_user WITH PASSWORD 'your-secure-password';
ALTER ROLE taskme_user SET client_encoding TO 'utf8';
ALTER ROLE taskme_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE taskme_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE taskme_db TO taskme_user;
\q
```

## Backend Deployment

### 1. Clone Repository

```bash
cd /var/www
sudo git clone https://github.com/crorry-dev/taskMe.git
sudo chown -R $USER:$USER taskMe
cd taskMe/backend
```

### 2. Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 3. Environment Configuration

```bash
cp .env.example .env
nano .env
```

Configure the following in `.env`:

```env
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=taskme_db
DB_USER=taskme_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### 4. Static Files and Database

```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

### 5. Gunicorn Configuration

Create `/etc/systemd/system/taskme.service`:

```ini
[Unit]
Description=TaskMe Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/taskMe/backend
Environment="PATH=/var/www/taskMe/backend/venv/bin"
ExecStart=/var/www/taskMe/backend/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/taskMe/backend/taskme.sock \
          taskme_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl start taskme
sudo systemctl enable taskme
sudo systemctl status taskme
```

## Frontend Deployment

### 1. Build Frontend

```bash
cd /var/www/taskMe/frontend
npm install
```

Create `.env.production`:

```env
REACT_APP_API_URL=https://api.yourdomain.com/api
```

Build the app:

```bash
npm run build
```

## Nginx Configuration

### 1. Create Nginx Config

Create `/etc/nginx/sites-available/taskme`:

```nginx
# API Server
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 50M;

    location /static/ {
        alias /var/www/taskMe/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/taskMe/backend/media/;
    }

    location / {
        proxy_pass http://unix:/var/www/taskMe/backend/taskme.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend Server
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/taskMe/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

### 2. Enable Site and Restart Nginx

```bash
sudo ln -s /etc/nginx/sites-available/taskme /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo certbot --nginx -d api.yourdomain.com
```

## Security Hardening

### 1. Firewall Setup

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### 2. PostgreSQL Security

Edit `/etc/postgresql/13/main/pg_hba.conf`:

```
local   all             postgres                                peer
local   all             all                                     md5
host    taskme_db       taskme_user     127.0.0.1/32           md5
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

### 3. File Permissions

```bash
sudo chown -R www-data:www-data /var/www/taskMe/backend/media
sudo chmod -R 755 /var/www/taskMe/backend/media
```

## Monitoring

### 1. Setup Logging

Create `/var/log/taskme/` directory:

```bash
sudo mkdir -p /var/log/taskme
sudo chown www-data:www-data /var/log/taskme
```

### 2. Log Rotation

Create `/etc/logrotate.d/taskme`:

```
/var/log/taskme/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

## Backup Strategy

### 1. Database Backup Script

Create `/usr/local/bin/backup-taskme-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/taskme"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U taskme_user taskme_db > $BACKUP_DIR/taskme_db_$TIMESTAMP.sql
find $BACKUP_DIR -name "taskme_db_*.sql" -mtime +7 -delete
```

Make executable:

```bash
sudo chmod +x /usr/local/bin/backup-taskme-db.sh
```

### 2. Cron Job

```bash
sudo crontab -e
```

Add:

```
0 2 * * * /usr/local/bin/backup-taskme-db.sh
```

## Performance Optimization

### 1. PostgreSQL Tuning

Edit `/etc/postgresql/13/main/postgresql.conf`:

```
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 8MB
maintenance_work_mem = 128MB
```

### 2. Gunicorn Workers

Adjust workers based on CPU cores: `(2 x $num_cores) + 1`

### 3. Redis Caching (Optional)

```bash
sudo apt install redis-server
pip install django-redis
```

Add to Django settings:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Maintenance

### Update Application

```bash
cd /var/www/taskMe
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart taskme

# Frontend
cd ../frontend
npm install
npm run build
```

### Monitor Logs

```bash
# Gunicorn logs
sudo journalctl -u taskme -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Troubleshooting

### Service Won't Start

```bash
sudo journalctl -u taskme -n 50
```

### Database Connection Issues

```bash
sudo -u postgres psql -d taskme_db -U taskme_user
```

### Static Files Not Loading

```bash
python manage.py collectstatic --noinput
sudo systemctl restart taskme
```

### Frontend Not Loading

Check Nginx error logs and ensure build completed successfully.

## Support

For issues or questions:
- GitHub Issues: https://github.com/crorry-dev/taskMe/issues
- Email: support@yourdomain.com

## License

MIT License - See LICENSE file for details
