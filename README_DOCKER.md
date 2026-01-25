# FlowBoard Docker Deployment Guide

## Quick Start (VPS Deployment)

### 1. Prerequisites
Make sure Docker and Docker Compose are installed on your VPS:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

### 2. Clone/Upload Your Project
```bash
cd /path/to/your/project
# Or upload your project files to the VPS
```

### 3. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.docker.example .env.docker

# Edit with your actual credentials
nano .env.docker
```

**Important:** Update these values in `.env.docker`:
- `SECRET_KEY` - Generate a strong secret key
- `ALLOWED_HOSTS` - Add your domain/IP
- `SITE_URL` - Your actual domain URL
- `EMAIL_HOST_USER` & `EMAIL_HOST_PASSWORD` - Your SMTP credentials
- `MNOTIFY_API_KEY` - Your SMS API key (if using SMS)
- `CSRF_TRUSTED_ORIGINS` - Add your domain

### 4. Run the Application
```bash
# Build and start all services
docker-compose --env-file .env.docker up -d --build

# Check if containers are running
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Access Your Application
Open your browser and go to: `http://your-server-ip:8009`

---

## Useful Commands

### Start/Stop Services
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Stop and remove all containers, volumes, and images
docker-compose down -v --rmi all
```

### View Logs
```bash
# View all logs
docker-compose logs -f

# View web service logs only
docker-compose logs -f web

# View database logs
docker-compose logs -f db

# View last 100 lines
docker-compose logs --tail=100
```

### Database Management
```bash
# Create a superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations manually
docker-compose exec web python manage.py migrate

# Access Django shell
docker-compose exec web python manage.py shell

# Access PostgreSQL shell
docker-compose exec db psql -U flowboard_user -d flowboard
```

### Monitor Background Tasks
```bash
# Check background task worker logs
docker-compose exec web tail -f /var/log/flowboard/background-tasks.log

# Check Gunicorn logs
docker-compose exec web tail -f /var/log/flowboard/gunicorn.log

# Check supervisor status
docker-compose exec web supervisorctl status
```

### Backup Database
```bash
# Backup PostgreSQL database
docker-compose exec db pg_dump -U flowboard_user flowboard > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker-compose exec -T db psql -U flowboard_user flowboard < backup_20260125_120000.sql
```

### Update Application
```bash
# Pull latest changes (if using git)
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Run new migrations
docker-compose exec web python manage.py migrate
```

---

## Production Deployment Checklist

- [ ] Set strong `SECRET_KEY` in `.env.docker`
- [ ] Set `DEBUG=False` in `.env.docker`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Update `SITE_URL` with your domain (https://yourdomain.com)
- [ ] Configure email SMTP settings
- [ ] Update `CSRF_TRUSTED_ORIGINS` with your domain
- [ ] Change default PostgreSQL password in `docker-compose.yml`
- [ ] Set up SSL/TLS with nginx reverse proxy (see below)
- [ ] Configure firewall to allow port 8009
- [ ] Set up automatic backups

---

## Using with Nginx Reverse Proxy (Recommended for Production)

### 1. Install Nginx
```bash
sudo apt-get update
sudo apt-get install nginx
```

### 2. Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/flowboard
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:8009;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/flowboard/staticfiles/;
    }

    location /media/ {
        alias /var/www/flowboard/media/;
    }
}
```

### 3. Enable Site and Restart Nginx
```bash
sudo ln -s /etc/nginx/sites-available/flowboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Set Up SSL with Let's Encrypt
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs web

# Check if port 8009 is already in use
sudo lsof -i :8009

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Database connection errors
```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Background tasks not running
```bash
# Check supervisor status
docker-compose exec web supervisorctl status

# Restart background tasks
docker-compose exec web supervisorctl restart background-tasks

# Check background task logs
docker-compose exec web tail -f /var/log/flowboard/background-tasks.log
```

### Static files not loading
```bash
# Collect static files again
docker-compose exec web python manage.py collectstatic --noinput

# Check static files volume
docker volume ls
docker volume inspect flowboard_static_volume
```

---

## Performance Monitoring

```bash
# View container resource usage
docker stats

# View specific container stats
docker stats flowboard_web

# Check disk usage
docker system df
```

---

## Security Best Practices

1. **Never commit** `.env.docker` to version control
2. **Change default passwords** in `docker-compose.yml`
3. **Use strong SECRET_KEY** (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
4. **Set DEBUG=False** in production
5. **Use HTTPS** in production (nginx + Let's Encrypt)
6. **Regularly update** Docker images and dependencies
7. **Set up backups** for PostgreSQL database
8. **Restrict port access** using firewall rules

---

## Support

For issues or questions, check the logs first:
```bash
docker-compose logs -f
```

Common log locations inside container:
- Gunicorn: `/var/log/flowboard/gunicorn.log`
- Background Tasks: `/var/log/flowboard/background-tasks.log`
- Supervisor: `/var/log/flowboard/supervisord.log`
