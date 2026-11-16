FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library
COPY shared /app/shared

# Copy requirements
COPY admin/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY admin /app

# Expose port
EXPOSE 8003

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
