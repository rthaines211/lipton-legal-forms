# Multi-stage Dockerfile for Railway Deployment
# Uses SERVICE_TYPE env var to determine which service to build
ARG SERVICE_TYPE=backend

# ============================================
# Backend Service (Node.js)
# ============================================
FROM node:20-alpine AS backend

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Build production assets
RUN npm run build:prod

EXPOSE 3000

CMD ["npm", "start"]


# ============================================
# Pipeline Service (Python)
# ============================================
FROM python:3.11-slim AS pipeline

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY database/ ./database/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]


# ============================================
# Final Stage - Choose based on SERVICE_TYPE
# ============================================
FROM ${SERVICE_TYPE} AS final
