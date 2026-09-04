#!/bin/sh
set -e

echo "==> Waiting for database at ${DB_HOST:-localhost}:${DB_PORT:-5432}..."

# Wait for PostgreSQL to be ready using python socket check
python - <<'EOF'
import os
import socket
import time
import sys

host = os.getenv('DB_HOST', 'localhost')
port = int(os.getenv('DB_PORT', 5432))
timeout = 60
start = time.time()

while time.time() - start < timeout:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"==> Database at {host}:{port} is reachable!")
            sys.exit(0)
    except (socket.error, ConnectionRefusedError):
        time.sleep(1)

print(f"==> ERROR: Timed out waiting for database at {host}:{port}")
sys.exit(1)
EOF

echo "==> Applying database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear || true

if [ "$SEED_DEMO_DATA" = "True" ] || [ "$SEED_DEMO_DATA" = "true" ] || [ "$SEED_DEMO_DATA" = "1" ]; then
    echo "==> Seeding demo database records..."
    python manage.py seed_demo_data
fi

echo "==> Starting application: $@"
exec "$@"
