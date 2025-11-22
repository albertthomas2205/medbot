# Start from official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /ASGI_UK_MEDICAL_BOT

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint and wait-for-postgres scripts
COPY entrypoint.sh wait-for-postgres.sh ./
RUN chmod +x entrypoint.sh wait-for-postgres.sh

# Copy entrypoint and make executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy rest of the project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose default ASGI port
EXPOSE 8000

# Default command (overridden by docker-compose)
# CMD ["uvicorn", "asgi_uk_medical_bot.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
CMD ["gunicorn", "asgi_uk_medical_bot.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]
