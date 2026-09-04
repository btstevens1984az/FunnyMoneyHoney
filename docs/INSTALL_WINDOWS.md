# Install — Windows

## Prerequisites

- Python 3.12+
- Node.js 20+ (22 recommended)
- Optional: Docker Desktop

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.example ..\.env
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Docker

```powershell
copy .env.example .env
docker compose up --build
```

| Surface | URL |
|---------|-----|
| UI | http://localhost:5173 |
| API | http://localhost:8000/docs |
