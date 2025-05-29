FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
        gcc \
        python3-dev \
        netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

COPY . .

EXPOSE 5000

# Entrypoint mejorado para migraciones
RUN echo '#!/bin/sh\n\
set -e\n\
/wait-for-db.sh db 5432\n\
if [ ! -d "/app/migrations" ]; then\n\
  echo "Initializing migrations..."\n\
  flask db init\n\
fi\n\
echo "Running migrations..."\n\
flask db migrate\n\
flask db upgrade\n\
exec "$@"' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["flask", "run", "--host=0.0.0.0"]