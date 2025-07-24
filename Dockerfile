FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=0
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    libgirepository-1.0-1 \
    libgirepository1.0-dev \
    libcairo2-dev \
    libcairo-gobject2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    pkg-config \
    python3-dev \
    gir1.2-glib-2.0 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root \
    && rm -rf $POETRY_CACHE_DIR

# Copy project
COPY . /app/

# Create static files directory
RUN mkdir -p /app/staticfiles

# Expose port
EXPOSE 8000

# Run the application with proper initialization
CMD ["sh", "-c", "while ! nc -z $DB_HOST $DB_PORT; do sleep 1; done && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application"]
