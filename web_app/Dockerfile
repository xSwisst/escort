FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY web_app/frontend/package.json web_app/frontend/package-lock.json ./
RUN npm ci

COPY web_app/frontend ./
RUN npm run build

# Python stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library first
COPY shared /app/shared

# Copy backend requirements and install Python dependencies
COPY web_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire backend directory to preserve structure
COPY web_app/backend /app/backend

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

EXPOSE 8004

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8004"]
