#!/bin/bash

# Exit on error
set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h db -U flowboard_user; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up and running!"

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
