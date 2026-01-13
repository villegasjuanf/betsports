source .venv/bin/activate

python manage.py makemigrations --noinput &\
python manage.py migrate --noinput &\
python manage.py collectstatic --noinput &\
celery -A betsports beat -S django &\
gunicorn betsports.wsgi:application --bind=0.0.0.0:8000 --log-level=info --timeout=60