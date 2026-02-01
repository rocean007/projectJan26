#!/usr/bin/env bash
# build.sh
set -o errexit

# Install dependencies using uv (not pip)
uv pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate
