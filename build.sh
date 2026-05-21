#!/usr/bin/env bash

# Exit on error.
set -o errexit

# Install project dependencies.
uv sync

# Run Django build steps from the directory that contains manage.py.
cd "$(dirname "$(find . -name manage.py -print -quit)")"

uv run ./manage.py collectstatic --noinput
uv run ./manage.py migrate
uv run ./manage.py createsuperuser \
    --username "${DJANGO_SUPERUSER_USERNAME:-admin}" \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" \
    --noinput || true
