# 🐳 Docker Deployment Guide

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo>
   cd super-vote-secret
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your secure passwords
   ```

3. **Deploy**
   ```bash
   ./deploy.sh
   ```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGO_ROOT_USER` | MongoDB root username | `admin` | Yes |
| `MONGO_ROOT_PASSWORD` | MongoDB root password | `securepassword123` | Yes |
| `MONGO_DB` | Database name | `vote_secret` | Yes |
| `DOMAIN` | Your domain name | `vote.super-csn.ca` | Yes |
| `ADMIN_EMAIL` | Email for SSL certificates | `admin@super-csn.ca` | Yes |
| `JWT_SECRET` | JWT signing key | - | Yes |
| `ENCRYPTION_KEY` | Data encryption key (32 chars) | - | Yes |

## Services

| Service | Container Name | Port | Description |
|---------|---------------|------|-------------|
| MongoDB | `vote-secret-mongodb` | `27017` | Database |
| Backend | `vote-secret-backend` | `8001` | FastAPI API |
| Frontend | `vote-secret-frontend` | `3000` | React App |
| Nginx | `vote-secret-nginx` | `80/443` | Reverse Proxy |
| Certbot | `vote-secret-certbot` | - | SSL Certificates |

## Management Commands

```bash
# View all services status
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb

# Restart specific service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes all data)
docker-compose down -v

# Update application
git pull
docker-compose up -d --build

# Force rebuild
docker-compose build --no-cache
docker-compose up -d
```

## Health Checks

All services include health checks:

```bash
# Check if services are healthy
docker-compose ps

# Manual health check
curl -f http://localhost/health
curl -f http://localhost/api/health
```

## Backup & Restore

### Backup Database
```bash
# Create backup directory
mkdir -p ./backups

# Backup database
docker exec vote-secret-mongodb mongodump --out /tmp/backup
docker cp vote-secret-mongodb:/tmp/backup ./backups/$(date +%Y%m%d_%H%M%S)
```

### Restore Database
```bash
# Restore from backup
docker cp ./backups/[backup-folder] vote-secret-mongodb:/tmp/restore
docker exec vote-secret-mongodb mongorestore /tmp/restore
```

## SSL Configuration

SSL certificates are automatically handled by Certbot:

- Certificates are stored in `letsencrypt_data` volume
- Automatic renewal every 12 hours
- HTTP automatically redirects to HTTPS

### Manual SSL renewal
```bash
docker-compose exec certbot certbot renew
docker-compose restart nginx
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo netstat -tulpn | grep :443
   # Stop conflicting services
   ```

2. **SSL certificate failed**
   ```bash
   # Check DNS is pointing to server
   nslookup vote.super-csn.ca
   
   # Check Certbot logs
   docker-compose logs certbot
   ```

3. **Database connection failed**
   ```bash
   # Check MongoDB logs
   docker-compose logs mongodb
   
   # Verify credentials in .env
   cat .env
   ```

4. **Application not loading**
   ```bash
   # Check all services
   docker-compose ps
   
   # Check backend health
   curl http://localhost/api/health
   ```

### Debug Mode

Run services with debug output:

```bash
# Stop services
docker-compose down

# Start with debug
docker-compose up --build
```

## Development

For local development without Docker:

```bash
# Setup development environment
./dev-setup.sh

# Start development servers
npm run dev
```

## Security

### Production Security Checklist

- [ ] Change default passwords in `.env`
- [ ] Use strong JWT_SECRET (32+ characters)
- [ ] Use strong ENCRYPTION_KEY (exactly 32 characters)
- [ ] Configure firewall to only allow ports 80 and 443
- [ ] Enable fail2ban for SSH protection
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

### Network Security

The application uses:
- HTTPS/TLS encryption
- Secure headers (HSTS, CSP, etc.)
- Rate limiting
- CORS protection
- Input validation

## Monitoring

### Log Files

```bash
# Application logs
docker-compose logs -f --tail=100

# Nginx access logs
docker-compose exec nginx tail -f /var/log/nginx/access.log

# Nginx error logs
docker-compose exec nginx tail -f /var/log/nginx/error.log
```

### Resource Usage

```bash
# Check resource usage
docker stats

# Check disk usage
docker system df

# Clean up unused resources
docker system prune
```