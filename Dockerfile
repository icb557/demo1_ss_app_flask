# Usar imagen Python 3.11 slim
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

<<<<<<< HEAD
# Copiar script wait-for-db
=======
# Copy project files first (before scripts)
COPY . .

# Copy and prepare wait-for-db script
>>>>>>> 8c4cabd2f89a75f07d51d75f914c6b4161ea8ea2
COPY scripts/wait-for-db.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-db.sh && \
    sed -i 's/\r$//' /usr/local/bin/wait-for-db.sh

<<<<<<< HEAD
# Entrypoint mejorado
RUN echo '#!/bin/sh\n\
set -e\n\
\n\
# Esperar a PostgreSQL\n\
echo "Esperando a la base de datos..."\n\
/usr/local/bin/wait-for-db.sh db\n\
\n\
# Configurar URL de la base de datos\n\
export DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}\n\
\n\
# Inicializar migraciones solo si no existen\n\
if [ ! -f "migrations/alembic.ini" ]; then\n\
  echo "Inicializando migraciones..."\n\
  flask db init\n\
fi\n\
\n\
# Verificar estado de migraciones\n\
echo "Estado actual de migraciones:"\n\
flask db current\n\
\n\
# Generar y aplicar migraciones\n\
echo "Generando migraciones..."\n\
flask db migrate\n\
\n\
echo "Aplicando migraciones..."\n\
flask db upgrade\n\
\n\
# Iniciar aplicación\n\
echo "Iniciando servidor Flask..."\n\
=======
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
>>>>>>> 8c4cabd2f89a75f07d51d75f914c6b4161ea8ea2
exec "$@"' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Puerto expuesto
EXPOSE 5000

# Comando para ejecutar
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
<<<<<<< HEAD
CMD ["flask", "run", "--host=0.0.0.0"]
=======
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
>>>>>>> 8c4cabd2f89a75f07d51d75f914c6b4161ea8ea2
