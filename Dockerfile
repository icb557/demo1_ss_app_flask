FROM python:3.11-slim

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
        gcc \
        python3-dev \
        netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script de espera
COPY scripts/wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# Copia la aplicación
COPY . .

# Configura entrypoint para tu estructura
RUN echo '#!/bin/sh\n\
set -e\n\
/wait-for-db.sh db 5432\n\
if [ ! -d "migrations" ]; then\n\
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