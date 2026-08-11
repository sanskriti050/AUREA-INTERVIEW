# Aurea — AI-Powered Interview Preparation Platform

Aurea is a full-stack platform for structured interview preparation. It brings resume analysis, mock interviews, technical quizzes, coding practice, answer guides, progress tracking, and an AI career coach into one application.

## ✨ Features

* **Resume Analysis** — Upload a PDF or DOCX resume for section detection, role-fit analysis, and job-description matching.
* **Mock Interviews** — Take role- and topic-based mock interviews, receive feedback, and save interview sessions.
* **Technical Quizzes** — Practice MCQs across core Computer Science topics.
* **Coding Practice** — Solve coding problems, run Python locally without a Judge0 key, and receive AI-assisted code reviews.
* **Answer Library** — Browse model interview answers across different topics and difficulty levels.
* **Progress Tracking** — Track attempts, scores, streaks, weekly activity, and topic performance.
* **AI Career Coach** — Chat with the Aurea AI coach when Groq is configured.
* **Question Administration** — Manage quiz questions through `/admin/questions` for configured admin emails.

---

## 🛠️ Tech Stack

| Area                | Technology                                     |
| ------------------- | ---------------------------------------------- |
| Frontend            | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend             | FastAPI, SQLAlchemy, Pydantic                  |
| Local Database      | SQLite                                         |
| Production Database | PostgreSQL + pgvector                          |
| AI                  | Groq API                                       |
| Code Execution      | Judge0 via RapidAPI + local Python fallback    |
| Authentication      | JWT Access & Refresh Tokens                    |
| Database Migrations | Alembic                                        |
| Deployment          | Docker, Docker Compose, Nginx                  |
| CI                  | GitHub Actions                                 |

---

## 🏗️ Project Structure

```text
aurea-v2/
│
├── aurea-v2/
│   └── backend/
│       ├── app/
│       ├── alembic/
│       │   ├── env.py
│       │   ├── script.py.mako
│       │   └── versions/
│       ├── tests/
│       ├── alembic.ini
│       ├── requirements.txt
│       └── .env
│
├── frontend/
│   └── .env.local
│
├── nginx/
├── docker-compose.yml
├── start.bat
└── README.md
```

---

# 🚀 Running Locally on Windows

## Prerequisites

Make sure you have:

* Python
* Node.js and npm
* PowerShell
* Git

---

## 1. Backend Setup

Open PowerShell in the project root:

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2"
```

Move to the backend:

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create the environment file:

```powershell
Copy-Item .env.example .env
```

If PowerShell blocks virtual-environment activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

---

## 2. Frontend Setup

Move to the frontend:

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\frontend"
```

Install dependencies:

```powershell
npm install
```

Create:

```text
frontend\.env.local
```

Add:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

---

## 3. Backend Environment Variables

Create/open:

```text
aurea-v2\backend\.env
```

Example local configuration:

```env
DATABASE_URL=sqlite:///./aurea_v2.db

SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

APP_ENV=development
FRONTEND_URL=http://localhost:3000

GROQ_API_KEY=gsk_your_key_here

EMBEDDING_API_KEY=your_embedding_provider_key_here
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

JUDGE0_API_KEY=your_rapidapi_key_here

ADMIN_EMAILS=you@example.com
```

### API Keys

The project uses separate credentials for different services:

* **Groq** — AI-powered features.
* **Embedding API** — embedding-based semantic resume/JD matching.
* **Judge0** — cloud code execution for supported languages.

Without Judge0, Python can still use the local fallback.

Never commit real API keys or secrets.

---

# ▶️ Start Aurea

## Option 1 — `start.bat`

From the project root:

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2"
.\start.bat
```

This starts:

```text
Backend  → http://127.0.0.1:8000
Frontend → http://localhost:3000
```

Keep both terminal windows open while using the application.

---

## Option 2 — Start Manually

### Backend

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"

.\.venv\Scripts\Activate.ps1

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

Open another terminal:

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\frontend"

npm run dev
```

Open:

```text
http://localhost:3000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🧭 Application Routes

| Page            | Route              |
| --------------- | ------------------ |
| Dashboard       | `/dashboard`       |
| Resume Analysis | `/resume`          |
| Mock Interview  | `/interview`       |
| Quiz            | `/quiz`            |
| Coding Practice | `/coding`          |
| Answer Library  | `/library`         |
| AI Coach Chat   | `/chat`            |
| Progress        | `/progress`        |
| Session History | `/sessions`        |
| Question Admin  | `/admin/questions` |

---

# 🔌 API Overview

| Module    | Base Path              | Examples                                      |
| --------- | ---------------------- | --------------------------------------------- |
| Auth      | `/api/auth`            | Register, login, refresh, current user        |
| Resume    | `/api/resume`          | Upload/analyze, refresh analysis, JD matching |
| Interview | `/api/interview`       | Questions, answer evaluation, session saving  |
| Quiz      | `/api/quiz`            | Topics, questions, answer submission          |
| Coding    | `/api/coding`          | Problems, execution, AI review                |
| Progress  | `/api/progress`        | Activity summary and weekly metrics           |
| Chat      | `/api/chat`            | AI coach responses                            |
| Admin     | `/api/admin/questions` | Question CRUD                                 |

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🗄️ Database & Migrations

Aurea uses **Alembic** for database migrations across SQLite and PostgreSQL.

From the backend directory with the virtual environment active:

### Apply migrations

```powershell
python -m alembic upgrade head
```

### Show current revision

```powershell
python -m alembic current
```

### Show migration history

```powershell
python -m alembic history --verbose
```

### Roll back the last migration

```powershell
python -m alembic downgrade -1
```

### Create a migration

```powershell
python -m alembic revision --autogenerate -m "describe your change"
```

The initial migration creates the required tables and supports vector storage through PostgreSQL `pgvector`.

---

# 🧠 Resume Semantic Matching

Aurea supports embedding-based semantic matching between resumes and job descriptions.

For PostgreSQL deployments, resume embeddings use a native vector column.

The embedding configuration is optional. When it is not available, the job-description matcher can use the deterministic keyword-based fallback.

---

# 🧪 Verification

### Backend tests

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"

.\.venv\Scripts\python.exe -m pytest -q
```

### Frontend TypeScript check

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\frontend"

.\node_modules\.bin\tsc.cmd --noEmit
```

### Frontend lint

```powershell
npm run lint
```

### Production build

```powershell
npm run build
```

---

# 🐳 Docker

Docker, Docker Compose, Nginx, and PostgreSQL configuration are included.

To start the Docker stack:

```powershell
docker compose up --build -d
```

The production configuration uses PostgreSQL with `pgvector`.

SQLite is intended for local development.

---

# 🔄 GitHub Actions

The project includes a GitHub Actions workflow that runs on pushes and pull requests to `main` or `master`.

The CI workflow checks:

* FastAPI backend tests
* TypeScript type checking
* ESLint
* Production Next.js build

The current checks do not require live AI service credentials.

---

# 🔐 Security

* Never commit `.env` or `.env.local`.
* Never commit API keys or secrets.
* Never commit the local SQLite database.
* Use a unique `SECRET_KEY` for production.
* AI prompt filtering is treated as a safety layer, not a complete protection against prompt injection.
* Use PostgreSQL and appropriate rate limiting for a public deployment.

The repository's `.gitignore` already excludes environment files, database files, virtual environments, `node_modules`, and `.next`.

---

## 📌 Aurea at a Glance

```text
Resume Analysis
       │
       ├── Job Description Matching
       │
       ▼
Mock Interviews ───► AI Feedback
       │
       ▼
Technical Quizzes
       │
       ▼
Coding Practice ───► AI Code Review
       │
       ▼
Progress Tracking
       │
       ▼
AI Career Coach
```

Aurea brings these interview-preparation workflows together in a single full-stack application.

cmd /c start.bat