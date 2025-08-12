# Deployment Guide for Artha AI

This guide provides step-by-step instructions for deploying Artha AI securely in different environments.

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL 12+
- Git
- SSL certificate (for production)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd Artha-Agent-New
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Generate secure keys
python -c "import secrets, base64; print('ENCRYPTION_KEY=' + base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
python -c "import secrets, base64; print('JWT_SECRET_KEY=' + base64.urlsafe_b64encode(secrets.token_bytes(64)).decode())"

# Update .env with generated keys and your configuration
```

### 3. Database Setup
```bash
# Install PostgreSQL and create database
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
# or
brew install postgresql  # macOS

# Run setup script
cd backend
python setup_postgresql.py
python create_tables.py
```

### 4. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python setup_complete_system.py
```

### 5. Frontend Setup
```bash
cd frontend
npm install
npm run build
```

## 🌍 Environment-Specific Deployments

### Development Environment

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Environment Variables (.env)
```env
NODE_ENV=development
DEBUG=true
FORCE_HTTPS=false
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002
```

### Production Environment

#### Using Docker (Recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: artha_ai
      POSTGRES_USER: artha_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - artha_network

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://artha_user:${DB_PASSWORD}@postgres:5432/artha_ai
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
      - FORCE_HTTPS=true
      - DEBUG=false
    depends_on:
      - postgres
    networks:
      - artha_network

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - backend
    networks:
      - artha_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - artha_network

volumes:
  postgres_data:

networks:
  artha_network:
    driver: bridge
```

#### Manual Production Setup

1. **Server Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip nodejs npm postgresql nginx certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash artha
sudo usermod -aG sudo artha
```

2. **Database Setup**
```bash
# Configure PostgreSQL
sudo -u postgres createuser artha_user
sudo -u postgres createdb artha_ai
sudo -u postgres psql -c "ALTER USER artha_user WITH PASSWORD 'your-secure-password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE artha_ai TO artha_user;"
```

3. **Application Deployment**
```bash
# Switch to application user
sudo su - artha

# Clone repository
git clone <your-repo-url> /home/artha/artha-ai
cd /home/artha/artha-ai

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
npm run build

# Configure environment
cp .env.example .env
# Edit .env with production values
```

4. **Process Management (systemd)**

Create `/etc/systemd/system/artha-backend.service`:
```ini
[Unit]
Description=Artha AI Backend
After=network.target

[Service]
Type=simple
User=artha
WorkingDirectory=/home/artha/artha-ai/backend
Environment=PATH=/home/artha/artha-ai/backend/venv/bin
ExecStart=/home/artha/artha-ai/backend/venv/bin/uvicorn api_server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/artha-frontend.service`:
```ini
[Unit]
Description=Artha AI Frontend
After=network.target

[Service]
Type=simple
User=artha
WorkingDirectory=/home/artha/artha-ai/frontend
ExecStart=/usr/bin/npm start
Restart=always
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

5. **Nginx Configuration**

Create `/etc/nginx/sites-available/artha-ai`:
```nginx
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

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

6. **SSL Certificate**
```bash
# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

7. **Start Services**
```bash
# Enable and start services
sudo systemctl enable artha-backend artha-frontend nginx
sudo systemctl start artha-backend artha-frontend nginx

# Check status
sudo systemctl status artha-backend artha-frontend nginx
```

## 🔧 Configuration Management

### Environment Variables by Environment

#### Development
```env
NODE_ENV=development
DEBUG=true
FORCE_HTTPS=false
LOG_LEVEL=DEBUG
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002
```

#### Staging
```env
NODE_ENV=staging
DEBUG=false
FORCE_HTTPS=true
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://staging.yourdomain.com
```

#### Production
```env
NODE_ENV=production
DEBUG=false
FORCE_HTTPS=true
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🔍 Health Checks and Monitoring

### Health Check Endpoints
- Backend: `GET /health`
- Frontend: `GET /api/health`

### Monitoring Setup
```bash
# Install monitoring tools
pip install prometheus-client
npm install @prometheus/client

# Setup log rotation
sudo logrotate -d /etc/logrotate.d/artha-ai
```

### Log Monitoring
```bash
# View logs
sudo journalctl -u artha-backend -f
sudo journalctl -u artha-frontend -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U artha_user -d artha_ai
```

2. **Permission Denied**
```bash
# Fix file permissions
sudo chown -R artha:artha /home/artha/artha-ai
sudo chmod +x /home/artha/artha-ai/backend/venv/bin/uvicorn
```

3. **SSL Certificate Issues**
```bash
# Renew certificate
sudo certbot renew

# Check certificate
sudo certbot certificates
```

4. **Service Won't Start**
```bash
# Check service logs
sudo journalctl -u artha-backend -n 50
sudo journalctl -u artha-frontend -n 50

# Restart services
sudo systemctl restart artha-backend artha-frontend nginx
```

## 🔄 Updates and Maintenance

### Application Updates
```bash
# Backup database
pg_dump -h localhost -U artha_user artha_ai > backup_$(date +%Y%m%d).sql

# Pull latest code
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend
cd ../frontend
npm install
npm run build

# Restart services
sudo systemctl restart artha-backend artha-frontend
```

### Database Migrations
```bash
# Run migration scripts
cd backend
python migrate_database.py
```

## 📊 Performance Optimization

### Backend Optimization
- Use Gunicorn with multiple workers
- Enable database connection pooling
- Implement Redis for caching
- Use CDN for static assets

### Frontend Optimization
- Enable Next.js static generation
- Optimize images and assets
- Use service workers for caching
- Implement lazy loading

## 🔐 Security Checklist

- [ ] SSL/TLS certificates installed and auto-renewing
- [ ] Firewall configured (only necessary ports open)
- [ ] Database access restricted to application servers
- [ ] Environment variables secured
- [ ] Regular security updates scheduled
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery procedures tested

## 📞 Support

For deployment issues:
- Check logs first: `sudo journalctl -u artha-backend -f`
- Review configuration files
- Verify environment variables
- Test database connectivity
- Check network connectivity

For additional help, refer to the [SECURITY.md](./SECURITY.md) file or contact the development team.