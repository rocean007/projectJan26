#!/usr/bin/env bash
# build.sh
set -o errexit

# Force install with break-system-packages (Vercel allows this)
pip install --break-system-packages -r requirements.txt

# Create api app if it doesn't exist
if [ ! -d "api" ]; then
    python manage.py startapp api
fi

# Run collectstatic (outputs to staticfiles folder)
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

echo "Build completed successfully!"