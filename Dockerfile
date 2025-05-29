# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

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

# Copy project files first (before scripts)
COPY . .

# Copy and prepare wait-for-db script
COPY scripts/wait-for-db.sh /usr/local/bin/
RUN sed -i 's/\r$//' /usr/local/bin/wait-for-db.sh && \
    chmod +x /usr/local/bin/wait-for-db.sh

# Expose port
EXPOSE 5000

# Create improved entrypoint script for Jenkins
RUN echo '#!/bin/sh\n\
set -e\n\
\n\
echo "=== Starting Flask Application Setup ==="\n\
echo "Current user: $(whoami)"\n\
echo "Current directory: $(pwd)"\n\
echo "Directory contents:"\n\
ls -la\n\
\n\
echo "=== Testing Flask app import ==="\n\
python -c "import app; print(\"✓ App imported successfully\")" || {\n\
  echo "✗ Error: Cannot import app.py"\n\
  echo "Python version: $(python --version)"\n\
  echo "Python path:"\n\
  python -c "import sys; [print(p) for p in sys.path]"\n\
  exit 1\n\
}\n\
\n\
echo "=== Waiting for database ==="\n\
/usr/local/bin/wait-for-db.sh db\n\
\n\
echo "=== Setting up database migrations ==="\n\
if [ ! -d "/app/migrations" ]; then\n\
  echo "Initializing migrations..."\n\
  flask db init\n\
  flask db migrate -m "initial migration"\n\
else\n\
  echo "Migrations directory exists, running upgrade..."\n\
fi\n\
\n\
flask db upgrade\n\
\n\
echo "=== Starting Flask application ==="\n\
exec "$@"' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Command to run the application
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]