#!/usr/bin/env bash
# Render build script

set -o errexit   # exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations (creates SQLite tables for events, meetings, timetable, work assignments)
python manage.py migrate --run-syncdb

# Initialize HOD account (Naveen/Naveen@2006) — skips if already exists
python manage.py initdata
