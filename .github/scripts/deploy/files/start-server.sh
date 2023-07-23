#!/usr/bin/env sh

# Find the installation location of the backend package
package_location=$(pip show --no-input --no-color backend | awk '/Location:/ {print $2}')

cd "$package_location/backend"
echo "Current directory: $(pwd)"

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# copy media files
echo "Copy media files"
cp -r media/* /data/

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
daphne -b 0.0.0.0 -p 8020 config.asgi:application
