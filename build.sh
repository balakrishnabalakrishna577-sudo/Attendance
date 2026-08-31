#!/usr/bin/env bash
# Render build script

set -o errexit   # exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Initialize data files and default HOD account
python manage.py initdata
