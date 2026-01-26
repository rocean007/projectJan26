#!/usr/bin/env bash
# build.sh
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

python manage.py startapp api
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate
