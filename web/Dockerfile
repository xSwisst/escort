FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY web/frontend/package*.json ./
RUN npm ci

COPY web/frontend ./
RUN npm run build

# Python stage
FROM python:3.11-slim

WORKDIR /app

# Copy shared library
COPY shared /app/shared

# Copy backend requirements and install Python dependencies
COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY web/backend /app/backend

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

EXPOSE 8007

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8007"]
