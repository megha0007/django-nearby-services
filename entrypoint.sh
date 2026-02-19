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

python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Ensuring default admin user exists..."

python manage.py shell << END
from django.contrib.auth import get_user_model

User = get_user_model()

email = "admin@example.com"
username = "admin"
password = "admin123"

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        username=username,
        password=password,
        role="admin"
    )
    print("Admin user created.")
else:
    print("Admin user already exists.")
END


echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
