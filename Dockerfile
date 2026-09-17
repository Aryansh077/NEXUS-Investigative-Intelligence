FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NEXUS_DB_PATH=/app/data/nexus.db \
    NEXUS_FRONTEND_ORIGINS=http://localhost:8000 \
    NEXUS_SERVE_FRONTEND=true
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/app ./backend/app
COPY ml ./ml
COPY scripts ./scripts
COPY data ./data
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
RUN mkdir -p /app/data
EXPOSE 8000
CMD ["sh", "-c", "if [ ! -f /app/data/nexus.db ]; then python scripts/seed_database.py; fi; uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]