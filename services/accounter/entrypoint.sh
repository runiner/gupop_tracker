#!/bin/bash

set -e

# применяем миграции
poetry run python3 manage.py migrate

exec poetry run "$@"
