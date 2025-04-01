# GitHub Actions Secrets Configuration

This document explains the secrets needed for the CI/CD workflows.

## Required Secrets

### For Docker Hub Publishing

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token (not your password)

### For Staging Deployment

- `STAGING_HOST`: Hostname or IP of the staging server
- `STAGING_USERNAME`: SSH username for the staging server
- `STAGING_SSH_KEY`: SSH private key for accessing the staging server
- `STAGING_PORT`: SSH port (usually 22)

### For Production Deployment

- `PRODUCTION_HOST`: Hostname or IP of the production server
- `PRODUCTION_USERNAME`: SSH username for the production server
- `PRODUCTION_SSH_KEY`: SSH private key for accessing the production server
- `PRODUCTION_PORT`: SSH port (usually 22)

### Environment Variables for Deployments

- `JWT_SECRET`: Secret key for JWT token generation
- `ENCRYPTION_KEY`: Key used for sensitive data encryption
- `REDIS_PASSWORD`: Password for Redis authentication
- `FS_PASSWORD`: Password for FreeSwitch authentication
- `GRAFANA_PASSWORD`: Admin password for Grafana dashboard

## Setting Up Secrets

1. Navigate to your repository on GitHub
2. Go to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Enter the name and value of the secret
5. Click "Add secret"

## Testing Secrets Locally

To test your configuration locally before pushing:

```bash
# Install act to run GitHub Actions locally
brew install act  # Mac
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Run the workflow locally (requires Docker)
act -s DOCKERHUB_USERNAME=yourusername -s DOCKERHUB_TOKEN=yourtoken
```
