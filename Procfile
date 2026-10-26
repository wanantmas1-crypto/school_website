web: cd Busiada_Boarding && python manage.py migrate --noinput && python manage.py collectstatic --noinput && python -m gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
