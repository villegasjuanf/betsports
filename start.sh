DJANGO_SUPERUSER_PASSWORD='admin'
source .venv/bin/activate

celery -A betsports beat -S django &\
python manage.py makemigrations --noinput &\
python manage.py migrate --noinput &\
python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email &\
gunicorn betsports.wsgi:application --bind=0.0.0.0:8000 --log-level=debug --timeout=60