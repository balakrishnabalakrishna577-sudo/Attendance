#!/usr/bin/env bash
# Render build script

set -o errexit   # exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run ALL database migrations (events, meetings, timetable, work assignments, official documents)
python manage.py migrate

# Initialize HOD account (Naveen/Naveen@2006) — skips if already exists
python manage.py initdata
