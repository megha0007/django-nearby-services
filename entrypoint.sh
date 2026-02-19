#!/bin/sh

# 1. Exit immediately if a command exits with a non-zero status.
set -e

echo "Checking environment..."

# 2. Only run the 'nc' check if we are NOT on Render. 
# Render handles DB readiness for you.
if [ -z "$RENDER" ]; then
    echo "Local environment detected. Waiting for database..."
    DB_HOST=${POSTGRES_HOST:-db}
    while ! nc -z $DB_HOST 5432; do
      sleep 1
    done
    echo "Database started"
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# ... (rest of your admin user logic)

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
