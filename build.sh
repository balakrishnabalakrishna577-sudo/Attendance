#!/usr/bin/env bash
# Render build script

set -o errexit   # exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Clear all data and recreate only HOD account
python manage.py initdata --reset
