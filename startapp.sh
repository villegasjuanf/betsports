DJANGO_SUPERUSER_PASSWORD='admin' 
python manage.py collectstatic --noinput
celery -A betsports beat -S django &\
uvicorn betsports.asgi:application --bind=0.0.0.0:8000 --log-level=info --timeout=600