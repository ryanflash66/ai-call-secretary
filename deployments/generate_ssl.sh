#!/bin/bash
# Script to generate self-signed SSL certificates for development or testing

# Create directory for SSL files
mkdir -p ssl

# Variables
DOMAIN=${1:-"localhost"}
COUNTRY=${2:-"US"}
STATE=${3:-"California"}
CITY=${4:-"San Francisco"}
ORGANIZATION=${5:-"AI Call Secretary"}
ORGANIZATIONAL_UNIT=${6:-"Development"}
EMAIL=${7:-"admin@example.com"}

echo "Generating SSL certificates for $DOMAIN"
echo "----------------------------------------"

# Generate certificate key
openssl genrsa -out ssl/key.pem 2048

# Generate certificate signing request
openssl req -new -key ssl/key.pem -out ssl/cert.csr -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORGANIZATION/OU=$ORGANIZATIONAL_UNIT/CN=$DOMAIN/emailAddress=$EMAIL"

# Generate self-signed certificate
openssl x509 -req -days 365 -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem

# Remove CSR file
rm ssl/cert.csr

# Set permissions
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "----------------------------------------"
echo "SSL certificate generation complete"
echo "cert.pem and key.pem created in the ssl directory"
echo "----------------------------------------"
echo "Warning: These are self-signed certificates suitable for development only."
echo "For production, use certificates from a trusted certificate authority."