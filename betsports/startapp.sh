DJANGO_SUPERUSER_PASSWORD='admin' 
python manage.py collectstatic --noinput
celery -A betsports beat -S django &\
gunicorn betsports.wsgi:application --bind=0.0.0.0:8000 --log-level=debug --timeout=600