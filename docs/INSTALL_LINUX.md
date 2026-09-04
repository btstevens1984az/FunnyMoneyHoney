# Install — Linux

## Prerequisites

- Python 3.12+
- Node.js 20+ (22 recommended)
- Optional: Docker + Docker Compose

## Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
export $(grep -v '^#' ../.env | xargs)
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Docker

```bash
cp .env.example .env
docker compose up --build
```

| Surface | URL |
|---------|-----|
| UI | http://localhost:5173 |
| API | http://localhost:8000/docs |
