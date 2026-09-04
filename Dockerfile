FROM python:3.12-slim AS backend

WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend /app/backend

FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEMO_MODE=true \
    DATABASE_URL=sqlite:////data/funnymoneyhoney.db

COPY --from=backend /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=backend /usr/local/bin /usr/local/bin
COPY backend /app/backend
COPY --from=frontend-build /frontend/dist /app/frontend_dist

RUN mkdir -p /data
WORKDIR /app/backend

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
