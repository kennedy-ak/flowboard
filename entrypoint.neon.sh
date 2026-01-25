#!/bin/bash

# Exit on error
set -e

echo "Connecting to Neon PostgreSQL..."
echo "Database: $DATABASE_NAME"
echo "Host: $DATABASE_HOST"

# Wait a bit for network to be ready
sleep 2

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating cache table..."
python manage.py createcachetable

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Clearing old sessions..."
python manage.py clearsessions

echo "Starting Supervisord (Gunicorn + Background Tasks)..."
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/flowboard.conf
