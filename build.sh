#!/usr/bin/env bash

# Exit on error.
set -o errexit

# Install project dependencies.
uv sync

# Run Django build steps from the directory that contains manage.py.
cd "$(dirname "$(find . -name manage.py -print -quit)")"

uv run ./manage.py collectstatic --noinput
uv run ./manage.py migrate

if [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    uv run ./manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ['DJANGO_SUPERUSER_PASSWORD']

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
"
else
    echo 'Skipping superuser creation because DJANGO_SUPERUSER_PASSWORD is not set.'
fi
