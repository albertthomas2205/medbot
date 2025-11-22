#!/bin/bash

wait_for_postgres() {
  echo "Waiting for PostgreSQL..."
  while ! nc -z postgres 5432; do
    sleep 0.5
  done
  echo "PostgreSQL started"
}

wait_for_worker() {
  echo "Waiting for Celery worker to be ready..."
  until celery -A asgi_uk_medical_bot inspect ping >/dev/null 2>&1; do
    sleep 1
  done
  echo "Celery worker is ready!"
}

# 1. Always wait for PostgreSQL
wait_for_postgres

# 2. If WAIT_FOR_WORKER is set, check Celery worker too
if [ "$WAIT_FOR_WORKER" = "true" ]; then
  wait_for_worker
fi

# 3. Run migrations if RUN_MIGRATIONS is true
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Making migrations..."
  python manage.py makemigrations --noinput

  echo "Applying migrations..."
  python manage.py migrate --noinput
else
  echo "Skipping migrations."
fi

# 4. Execute CMD
exec "$@"

















# #!/bin/bash
# set -e

# # Wait for PostgreSQL to be ready
# echo "Waiting for postgres..."
# while ! nc -z postgres 5432; do
#   sleep 0.5
# done
# echo "PostgreSQL started"

# # Run migrations only if RUN_MIGRATIONS is set to true
# if [ "$RUN_MIGRATIONS" = "true" ]; then
#   echo "Making migrations..."
#   python manage.py makemigrations --noinput

#   echo "Applying migrations..."
#   python manage.py migrate --noinput
# else
#   echo "Skipping migrations."
# fi

# # Extra: Wait until Django is actually importable (important for Celery workers)
# echo "Checking Django readiness..."
# python <<'EOF'
# import sys
# try:
#     import django
#     django.setup()
#     from django.apps import apps
#     apps.check_apps_ready()
#     print("Django is ready.")
# except Exception as e:
#     print("Django not ready:", e)
#     sys.exit(1)
# EOF

# # Execute the command passed from CMD
# exec "$@"




































# #!/bin/bash

# # Wait for PostgreSQL to be ready
# echo "Waiting for postgres..."
# while ! nc -z postgres 5432; do
#   sleep 0.5
# done
# echo "PostgreSQL started"

# # Run migrations only if RUN_MIGRATIONS is set to true
# if [ "$RUN_MIGRATIONS" = "true" ]; then
#   echo "Making migrations..."
#   python manage.py makemigrations --noinput

#   echo "Applying migrations..."
#   python manage.py migrate --noinput
# else
#   echo "Skipping migrations."
# fi

# # Execute the command passed from CMD
# exec "$@"