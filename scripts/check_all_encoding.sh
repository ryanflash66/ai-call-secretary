#!/bin/bash

# Script to check and fix encoding issues in all relevant directories
# This is used by the CI/CD pipeline and can also be run locally

# Set to fail on errors
set -e

echo "Checking and fixing encoding issues in all project directories..."

# Check main source code
echo "Checking src/ directory..."
python scripts/fix_encoding.py src

# Check tests
echo "Checking tests/ directory..."
python scripts/fix_encoding.py tests

# Check web assets
echo "Checking web/ directory..."
python scripts/fix_encoding.py web

# Check configuration files
echo "Checking config/ directory..."
python scripts/fix_encoding.py config

# Check scripts
echo "Checking scripts/ directory..."
python scripts/fix_encoding.py scripts

# Check docs
echo "Checking docs/ directory..."
python scripts/fix_encoding.py docs

echo "Encoding check complete. All files should now be in UTF-8 format."