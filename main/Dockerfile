FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared libraries and modules
COPY shared /app/shared
COPY repository /app/repository
COPY services /app/services

# Copy requirements
COPY main/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main /app

# Expose port
EXPOSE 8001

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
