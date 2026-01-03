DJANGO_SUPERUSER_PASSWORD='admin' 
source .venv/bin/activate

python manage.py collectstatic --noinput
celery -A betsports multi start 2 -c 3 -l info --range-prefix=worker --max-tasks-per-child=2 &\
gunicorn betsports.wsgi:application --bind=0.0.0.0:8001 --log-level=debug --timeout=600