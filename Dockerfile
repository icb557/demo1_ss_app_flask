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

# Copiar script wait-for-db
COPY scripts/wait-for-db.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-db.sh && \
    sed -i 's/\r$//' /usr/local/bin/wait-for-db.sh

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
exec "$@"' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Puerto expuesto
EXPOSE 5000

# Comando para ejecutar
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["flask", "run", "--host=0.0.0.0"]