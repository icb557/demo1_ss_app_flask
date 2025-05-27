# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

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

# Copy project files
COPY . .

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["/usr/local/bin/wait-for-db.sh", "db", "flask", "run", "--host=0.0.0.0"] 