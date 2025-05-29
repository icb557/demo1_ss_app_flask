FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar script de espera para PostgreSQL
COPY scripts/wait-for-db.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-db.sh

# Copiar aplicación
COPY . .

# Comando de inicio integrado (sin entrypoint separado)
CMD /bin/sh -c '\
    echo "=== Esperando a PostgreSQL ===" && \
    until pg_isready -h db -p 5432 -U postgres; do \
        echo "PostgreSQL is unavailable - sleeping"; \
        sleep 2; \
    done && \
    echo "=== PostgreSQL está listo ===" && \
    echo "=== Configurando migraciones ===" && \
    if [ ! -d "migrations" ]; then \
        flask db init && \
        flask db migrate -m "Initial migration"; \
    fi && \
    flask db upgrade && \
    echo "=== Iniciando aplicación ===" && \
    flask run --host=0.0.0.0'