#!/bin/bash
# Entrypoint script for Docker container

set -e

# Create necessary directories
mkdir -p /app/data /app/logs /app/keys

# Set correct permissions
chmod -R 755 /app
chmod -R 700 /app/keys

# Check if we should run migrations or other setup tasks
if [ "$1" = "setup" ]; then
    echo "Running setup tasks..."
    
    # Create admin user if specified
    if [ ! -z "$ADMIN_USERNAME" ] && [ ! -z "$ADMIN_PASSWORD" ]; then
        echo "Creating admin user: $ADMIN_USERNAME"
        python -m scripts.create_admin_user \
            --username "$ADMIN_USERNAME" \
            --password "$ADMIN_PASSWORD" \
            --email "${ADMIN_EMAIL:-admin@example.com}" \
            --force
    fi
    
    echo "Setup complete"
    exit 0
fi

# Check if we should run a specific module
if [ "$1" = "api" ]; then
    echo "Starting API server..."
    exec python -m src.main --mode api ${@:2}
elif [ "$1" = "telephony" ]; then
    echo "Starting Telephony server..."
    exec python -m src.main --mode telephony ${@:2}
elif [ "$1" = "security-demo" ]; then
    echo "Running security demo..."
    exec python -m scripts.security_demo ${@:2}
elif [ "$1" = "create-user" ]; then
    echo "Creating user..."
    exec python -m scripts.create_admin_user ${@:2}
else
    # Default: run the main application
    echo "Starting AI Call Secretary..."
    exec python -m src.main ${@}
fi