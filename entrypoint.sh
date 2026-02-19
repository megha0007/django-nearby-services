#!/bin/sh
set -e

echo "--- Starting Entrypoint Script ---"

# 1. FIND MANAGE.PY AUTOMATICALLY
# This looks for manage.py and sets the folder it's in as MANAGE_DIR
MANAGE_PATH=$(find . -name "manage.py" | head -n 1)

if [ -z "$MANAGE_PATH" ]; then
    echo "ERROR: Could not find manage.py anywhere in /app!"
    exit 1
fi

MANAGE_DIR=$(dirname "$MANAGE_PATH")
echo "Found manage.py at: $MANAGE_PATH"

# 2. DATABASE WAIT (Local Docker only)
if [ -z "$RENDER" ]; then
    echo "Local environment: Waiting for database..."
    DB_HOST=${POSTGRES_HOST:-db}
    while ! nc -z $DB_HOST 5432; do
      sleep 1
    done
    echo "Database is up!"
fi

# 3. RUN COMMANDS
echo "Running migrations..."
python "$MANAGE_PATH" migrate --noinput

echo "Collecting static files..."
python "$MANAGE_PATH" collectstatic --noinput

# 4. ADMIN USER (Using the discovered path)
echo "Ensuring admin user exists..."
python "$MANAGE_PATH" shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin123", role="admin")
    print("Admin created.")
END

echo "Starting Gunicorn..."
# We use the MANAGE_DIR to tell Gunicorn where to look for the 'config' folder
cd "$MANAGE_DIR"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
