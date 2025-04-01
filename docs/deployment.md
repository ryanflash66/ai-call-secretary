# AI Call Secretary Deployment Guide

This guide provides instructions for deploying the AI Call Secretary system in a production environment.

## Prerequisites

- Docker and Docker Compose (v1.29.0+)
- 4GB+ RAM, 2+ CPU cores
- 20GB+ disk space
- Valid SSL certificates for HTTPS
- Domain name (optional but recommended)

## Deployment Options

The AI Call Secretary system can be deployed in several ways:

1. **Docker Compose** (recommended for small-scale deployments)
2. **Kubernetes** (for large-scale or high-availability deployments)
3. **Manual Installation** (for custom environments)

This guide focuses on the Docker Compose deployment method.

## Docker Compose Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-call-secretary.git
cd ai-call-secretary
```

### 2. Create Environment Variables

Create a `.env` file in the root directory:

```bash
# Security
JWT_SECRET=your-strong-secret-key-at-least-32-chars
ENCRYPTION_KEY=your-encryption-key-base64-encoded

# Redis
REDIS_PASSWORD=your-strong-redis-password

# FreeSwitch
FS_HOST=freeswitch
FS_PORT=8021
FS_PASSWORD=ClueCon

# Monitoring
GRAFANA_PASSWORD=your-grafana-admin-password
```

Replace all placeholder values with strong, secure values.

### 3. Prepare SSL Certificates

Create the SSL directory and copy your certificates:

```bash
mkdir -p deployments/ssl
cp /path/to/your/cert.pem deployments/ssl/
cp /path/to/your/key.pem deployments/ssl/
```

For testing purposes, you can generate self-signed certificates:

```bash
mkdir -p deployments/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout deployments/ssl/key.pem \
  -out deployments/ssl/cert.pem
```

### 4. Create Data Directories

```bash
mkdir -p data logs keys
chmod 700 keys
```

### 5. Update Configuration

Review and customize the configuration in `config/production.yml`.

Update at least the following settings:

- `api.cors_origins` - Add your domain name
- `telephony.freeswitch.password` - Set a secure password
- `llm.api_url` - Set the URL of your LLM provider
- `escalation.departments` and `escalation.specific_people` - Set real phone numbers

### 6. Build and Start Services

```bash
docker-compose up -d
```

This will:
- Build the application containers
- Start all services
- Create required networks and volumes

### 7. Create Admin User

```bash
docker-compose exec api python -m scripts.create_admin_user \
  --username admin \
  --password your-secure-password \
  --email admin@example.com
```

### 8. Verify Deployment

Check if all services are running:

```bash
docker-compose ps
```

Access the web interface at `https://your-domain-or-ip`.

Access monitoring dashboards at:
- Grafana: `https://your-domain-or-ip:3000`
- Prometheus: `https://your-domain-or-ip:9090`

## Kubernetes Deployment

For Kubernetes deployment, refer to the Kubernetes manifests in the `k8s/` directory.

## Scaling Considerations

### Horizontal Scaling

To scale the application horizontally, you can increase the number of API service replicas:

```bash
docker-compose up -d --scale api=3
```

### Vertical Scaling

For vertical scaling, adjust the resource limits in the Docker Compose file.

### Database Scaling

For production with high traffic, consider:
1. Using a managed Redis service
2. Implementing Redis clustering
3. Setting up Redis replication for redundancy

## Monitoring and Maintenance

### Monitoring

The deployment includes:
- Prometheus for metrics collection
- Grafana for metrics visualization
- Log files in the `logs/` directory

Access Grafana at `https://your-domain-or-ip:3000` (default login: admin/admin).

### Backup Procedures

Backup these important directories:
- `data/` - Contains application data
- `keys/` - Contains encryption keys
- `logs/` - Contains application logs

```bash
# Example backup script
tar -czf backup-$(date +%Y%m%d).tar.gz data/ keys/ logs/
```

### Updates

To update the application:

1. Pull the latest changes
   ```bash
   git pull
   ```

2. Rebuild and restart the containers
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## Troubleshooting

### Common Issues

1. **Container fails to start**
   - Check logs: `docker-compose logs api`
   - Verify environment variables are set correctly

2. **Cannot access web interface**
   - Check NGINX logs: `docker-compose logs nginx`
   - Verify firewall settings allow traffic to ports 80 and 443

3. **Authentication issues**
   - Check JWT secret is set correctly
   - Verify Redis is running: `docker-compose ps redis`

### Logs

View logs for a specific service:

```bash
docker-compose logs -f api
docker-compose logs -f telephony
docker-compose logs -f nginx
```

### Getting Help

If you encounter issues not covered here, please:
1. Check the GitHub repository issues
2. Contact support at support@example.com

## Security Considerations

### Production Security Checklist

- [ ] Use strong, unique passwords for all services
- [ ] Replace all default secrets in production
- [ ] Set appropriate firewall rules
- [ ] Enable and configure regular backups
- [ ] Set up monitoring and alerting
- [ ] Use valid SSL certificates (not self-signed)
- [ ] Keep all containers updated
- [ ] Run security audits regularly

### Security Features

The AI Call Secretary system includes numerous security features:
- JWT-based authentication
- Encrypted data storage
- Input validation and sanitization
- Request rate limiting
- HTTPS encryption
- Secure HTTP headers
- Audit logging
- Container isolation

Refer to `docs/security.md` for detailed security documentation.

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| JWT_SECRET | Secret key for JWT tokens | None | Yes |
| ENCRYPTION_KEY | Key for data encryption | None | Yes |
| REDIS_PASSWORD | Redis password | "changeme" | Yes |
| FS_HOST | FreeSwitch hostname | "freeswitch" | No |
| FS_PORT | FreeSwitch port | 8021 | No |
| FS_PASSWORD | FreeSwitch password | "ClueCon" | No |
| GRAFANA_PASSWORD | Grafana admin password | "admin" | No |

## Production Checklist

Before going live:

- [ ] Replace all default credentials
- [ ] Test all functionality
- [ ] Set up monitoring and alerting
- [ ] Configure backups
- [ ] Perform load testing
- [ ] Conduct security audit
- [ ] Create disaster recovery plan
- [ ] Document custom configuration

## Conclusion

You have now deployed the AI Call Secretary system. For additional configuration options and advanced features, please refer to the project documentation.