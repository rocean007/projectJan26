#!/usr/bin/env bash
# build.sh
set -o errexit

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt

if [ ! -d "api" ]; then
    python manage.py startapp api
fi

python manage.py collectstatic --noinput

python manage.py migrate

echo "Build completed successfully!"