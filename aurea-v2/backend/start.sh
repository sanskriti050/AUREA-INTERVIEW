#!/bin/sh
set -e
echo "Running Alembic migrations..."
python -m alembic upgrade head
echo "Starting Gunicorn..."
exec gunicorn app.main:app \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --timeout 120
