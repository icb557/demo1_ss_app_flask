# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app:create_app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and prepare wait-for-db script
COPY scripts/wait-for-db.sh /usr/local/bin/
RUN sed -i 's/\r$//' /usr/local/bin/wait-for-db.sh && \
    chmod +x /usr/local/bin/wait-for-db.sh

# Copy project files (excluding migrations in development)
COPY . .

# Expose port
EXPOSE 5000

# Create entrypoint script
RUN echo '#!/bin/sh\n\
set -e\n\
export FLASK_APP=app:create_app<\
if [ ! -d "/app/migrations" ]; then\n\
  echo "Initializing migrations..."\n\
  flask db init\n\
  flask db migrate -m "initial migration"\n\
fi\n\
echo "Applying migrations..."\n\
flask db upgrade\n\
echo "Starting application..."\n\
exec "$@"' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Command to run the application
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/usr/local/bin/wait-for-db.sh", "db", "flask", "run", "--host=0.0.0.0"]