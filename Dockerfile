FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=False \
    DJANGO_REQUIRE_DATABASE_URL=True

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
WORKDIR /app/Busiada_Boarding

RUN DJANGO_DEBUG=True DJANGO_REQUIRE_DATABASE_URL=False python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python -m gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --access-logfile - --error-logfile -"]
