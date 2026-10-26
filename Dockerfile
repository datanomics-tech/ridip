# RIDIP: one container that serves the API and the built React map.

# 1. Build the frontend
FROM node:24-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 2. Run the API, which also serves the built frontend
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY data/seed/ /app/data/seed/
COPY --from=frontend /app/frontend/dist /app/frontend/dist

# Do not run as root
RUN useradd --create-home --uid 10001 ridip
USER ridip

EXPOSE 8000
# Render sets PORT; default to 8000 when run locally.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
