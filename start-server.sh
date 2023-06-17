#!/usr/bin/env sh

# Find the installation location of the backend package
package_location=$(pip show --no-input --no-color backend | awk '/Location:/ {print $2}')

cd "$package_location/backend"
echo "Current directory: $(pwd)"

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Create superuser
# if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
#     python manage.py createsuperuser --no-input
# fi

# Start server
gunicorn config.wsgi --bind=0.0.0.0:8020 --workers 3
