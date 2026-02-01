#!/usr/bin/env bash
# build.sh
set -o errexit

# Use uv to install dependencies (correct for Vercel's environment)
uv pip install --system -r requirements.txt

# If api directory doesn't exist, create it
if [ ! -d "api" ]; then
    python manage.py startapp api
fi

python manage.py collectstatic --noinput
python manage.py migrate