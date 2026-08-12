# Aurea — AI-Powered Interview Preparation Platform

A full-stack platform for structured interview preparation: resume analysis, mock interviews, quizzes, coding practice, answer guides, progress tracking, and an AI career coach.

---

## ✨ Features

- **Resume Analysis** — Upload PDF/DOCX, get section detection, role-fit scores, and job-description matching.
- **Mock Interviews** — Role and topic-based sessions with per-answer scoring and AI feedback.
- **Technical Quizzes** — MCQs across CS fundamentals with instant feedback.
- **Coding Practice** — Monaco Editor (VS Code engine), test cases, run code, and AI code review.
- **Answer Library** — Model answers across topics and difficulty levels.
- **Progress Tracking** — Streaks, weekly charts, topic mastery, field performance.
- **AI Career Coach** — Chat with Groq-powered Llama 3.3 70B. History persists across sessions.
- **Question Administration** — Manage quiz questions at `/admin/questions`.
- **Toast Notifications** — All errors and confirmations shown as non-blocking toasts.
- **Skeleton Loaders** — Smooth loading states on every data-heavy page.
- **Mobile Sidebar** — Hamburger menu, slide-in sidebar with backdrop dismiss.

---

## 🛠️ Tech Stack

| Area | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Code Editor | Monaco Editor (`@monaco-editor/react`) |
| Charts | Recharts |
| Markdown | react-markdown + rehype-sanitize |
| Notifications | react-hot-toast |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Local Database | SQLite |
| Production Database | PostgreSQL + pgvector |
| AI | Groq API — `llama-3.3-70b-versatile` |
| Code Execution | Judge0 via RapidAPI + local Python fallback |
| Authentication | JWT via PyJWT 2.9.0 — httpOnly cookies (XSS-safe) |
| Database Migrations | Alembic |
| Deployment | Docker, Docker Compose, Nginx |
| CI | GitHub Actions |
| Error Monitoring | Sentry (optional — set `SENTRY_DSN`) |

---

## 🏗️ Project Structure

```text
aurea-v2/                         ← project root
├── aurea-v2/
│   └── backend/                  ← FastAPI backend
│       ├── app/
│       │   ├── core/             ← config, database, security, dependencies
│       │   ├── models/           ← SQLAlchemy models
│       │   ├── routers/          ← API route handlers
│       │   ├── schemas/          ← Pydantic schemas
│       │   ├── services/         ← AI, resume, coding, quiz services
│       │   └── main.py
│       ├── alembic/              ← database migrations
│       │   └── versions/
│       ├── tests/                ← pytest test suite
│       ├── requirements.txt
│       ├── alembic.ini
│       └── .env                  ← never commit this
│
├── frontend/                     ← Next.js frontend
│   ├── src/
│   │   ├── app/                  ← all pages
│   │   │   ├── chat/
│   │   │   ├── coding/
│   │   │   ├── dashboard/
│   │   │   ├── interview/
│   │   │   ├── library/
│   │   │   ├── login/
│   │   │   ├── progress/
│   │   │   ├── quiz/
│   │   │   ├── register/
│   │   │   ├── resume/
│   │   │   ├── sessions/
│   │   │   └── admin/questions/
│   │   ├── components/
│   │   │   ├── AppLayout.tsx     ← auth guard + mobile top bar
│   │   │   ├── Sidebar.tsx       ← responsive sidebar with hamburger
│   │   │   ├── Skeleton.tsx      ← loading skeleton components
│   │   │   └── Toast.tsx         ← toast notification provider
│   │   └── lib/
│   │       ├── api.ts            ← axios instance + all API calls
│   │       └── auth-context.tsx  ← JWT auth context
│   └── .env.local                ← never commit this
│
├── nginx/                        ← production reverse proxy config
├── docker-compose.yml
├── start.bat                     ← Windows one-click launcher
└── README.md
```

---

## 🚀 Local Setup (Windows)

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- PowerShell
- Git

---

### Step 1 — Backend Setup (run once)

Open **PowerShell** and run these commands:

```powershell
# Go to backend
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"

# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# If activation is blocked, run this once then activate again
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Create env file from example
Copy-Item .env.example .env
```

---

### Step 2 — Frontend Setup (run once)

```powershell
# Go to frontend
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\frontend"

# Install all dependencies (including Monaco, Recharts, react-markdown, react-hot-toast)
npm install
```

Create `frontend\.env.local` with this content:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

---

### Step 3 — Configure Backend Environment

Open `aurea-v2\backend\.env` and fill in your keys:

```env
# Database
DATABASE_URL=sqlite:///./aurea_v2.db

# Security — generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# App
APP_ENV=development
FRONTEND_URL=http://localhost:3000

# Required — powers AI chat, interview feedback, code review, resume analysis
GROQ_API_KEY=gsk_your_key_here

# Optional — enables embedding-based semantic JD matching (keyword fallback works without it)
EMBEDDING_API_KEY=your_embedding_provider_key_here
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

# Optional — enables Java, JavaScript, C++ cloud execution (Python runs locally without this)
JUDGE0_API_KEY=your_rapidapi_key_here

# Optional — comma-separated emails for /admin/questions access
ADMIN_EMAILS=you@example.com
```

> **Note:** `GROQ_API_KEY` and `JUDGE0_API_KEY` are different services. Groq powers AI. Judge0 powers non-Python code execution.

---

## ▶️ Running the App (Every Day)

### Recommended — Two separate terminals

This gives you clean logs for both servers.

**Terminal 1 — Backend:**

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Wait for: `Application startup complete.`

**Terminal 2 — Frontend:**

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\frontend"
npm run dev
```

Wait for: `Ready in Xms`

Then open: **http://localhost:3000**

API docs: **http://127.0.0.1:8000/docs**

---

### Alternative — `start.bat` (one command)

From the project root:

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2"
.\start.bat
```

This opens two separate terminal windows automatically. Keep both open while using the app.

> `start.bat` checks that `.venv` and `node_modules` exist before starting. If either is missing, it prints setup instructions.

---

## 🧭 Application Routes

| Page | Route |
|---|---|
| Landing | `/` |
| Login | `/login` |
| Register | `/register` |
| Dashboard | `/dashboard` |
| Resume Analysis | `/resume` |
| Mock Interview | `/interview` |
| Quiz | `/quiz` |
| Coding Practice | `/coding` |
| Answer Library | `/library` |
| AI Coach Chat | `/chat` |
| Progress | `/progress` |
| Session History | `/sessions` |
| Question Admin | `/admin/questions` |

---

## 🔌 API Overview

| Module | Base Path | Key Endpoints |
|---|---|---|
| Auth | `/api/auth` | `register`, `login`, `refresh`, `me` |
| Resume | `/api/resume` | `analyze`, `me`, `reanalyze`, `match-jd` |
| Interview | `/api/interview` | `questions`, `evaluate`, `ai-feedback/stream`, `sessions` |
| Quiz | `/api/quiz` | `topics`, `questions/{topic}/{diff}`, `submit/{topic}/{diff}` |
| Coding | `/api/coding` | `problems`, `starter`, `execute`, `review` |
| Progress | `/api/progress` | `summary` |
| Chat | `/api/chat` | `stream` (Server-Sent Events) |
| Admin | `/api/admin/questions` | CRUD — requires `ADMIN_EMAILS` |

Full interactive docs at `http://127.0.0.1:8000/docs` (development only).

---

## 🗄️ Database Migrations

Always run from the backend directory with `.venv` active.

```powershell
# Apply all pending migrations
python -m alembic upgrade head

# Show current revision
python -m alembic current

# Show full history
python -m alembic history --verbose

# Roll back one migration
python -m alembic downgrade -1

# Generate a new migration after changing a model
python -m alembic revision --autogenerate -m "describe your change"
```

---

## 🧪 Verification Commands

Run these to confirm everything is working correctly.

```powershell
# Backend tests (41 tests)
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"
.\.venv\Scripts\python.exe -m pytest -q

# Frontend TypeScript check
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\frontend"
.\node_modules\.bin\tsc.cmd --noEmit

# Frontend lint (specific files — full lint is slow)
.\node_modules\.bin\eslint.cmd src/app src/components src/lib

# Production build check
npm run build
```

---

## 🐳 Docker (Production)

```powershell
docker compose up --build -d
```

The Docker stack uses:
- `pgvector/pgvector:pg16` for PostgreSQL with vector support
- Nginx as reverse proxy
- Health checks on all services

Before production: set strong secrets, use PostgreSQL, configure real API keys. SQLite is for local development only.

### PostgreSQL + pgvector

The Docker stack enables the `vector` extension automatically. For managed providers (Neon, Supabase), enable it manually:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Then set `EMBEDDING_API_KEY` in backend `.env` and restart the backend. Re-embed existing resumes using **Resume → Refresh analysis**.

---

## 🔄 GitHub Actions CI

Runs automatically on every push and pull request to `main` or `master`:

1. Backend pytest (41 tests)
2. TypeScript type check
3. ESLint
4. Production Next.js build

No secrets required for CI — live AI services are not called in tests.

---

## 🔐 Security Notes

- Never commit `.env`, `.env.local`, API keys, or the SQLite database file
- Generate a unique `SECRET_KEY` for every environment — never reuse
- **JWT library:** PyJWT 2.9.0 (replaced python-jose which had CVE-2024-33664)
- **Auth tokens:** Stored in `httpOnly` cookies — not accessible to JavaScript (XSS protection). Backend sets `secure=True` in production automatically
- **JD Matching:** Uses keyword analysis by default. Set `EMBEDDING_API_KEY` for true semantic vector matching. The UI clearly labels which method is active
- **Error monitoring:** Set `SENTRY_DSN` in `backend/.env` to enable Sentry. Free tier at sentry.io is sufficient for portfolio use
- AI prompt injection filtering is a safety layer, not a guarantee
- Local Python code execution has no sandbox — use Judge0 for production
- Use PostgreSQL and rate limiting for any public deployment

---

## 🐛 Troubleshooting

### `requirements.txt` not found
You are in the wrong directory. Navigate to:
```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"
```

### `No module named uvicorn`
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Frontend cannot reach backend
1. Confirm `http://127.0.0.1:8000/health` opens in browser
2. Confirm `frontend\.env.local` contains `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api`
3. Restart both servers after editing any `.env` file

### AI chat / resume analysis / code review not working
1. Set `GROQ_API_KEY=gsk_...` in `aurea-v2\backend\.env`
2. Restart the backend
3. Do not put the Groq key in `frontend\.env.local`

### Java / C++ / JavaScript execution not working
Add `JUDGE0_API_KEY` to `aurea-v2\backend\.env`, then restart the backend. Python runs locally without this key.

### Monaco Editor not loading
Run `npm install` in the `frontend` directory to ensure `@monaco-editor/react` is installed.

### Toast notifications not appearing
Ensure `<ToastProvider />` is present in `src/app/layout.tsx`. It is included by default.

### Chat history not persisting
Chat history is stored in browser `localStorage`. Clearing browser data will remove it. This is expected behaviour.

### Port 3000 already in use
```powershell
# Find and kill the process
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Disk space errors during npm install
```powershell
# Clear npm cache
npm cache clean --force

# Remove Next.js build cache
Remove-Item -Recurse -Force "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\frontend\.next"
```

---

## 📌 Aurea at a Glance

```text
Upload Resume
     │
     ├── Role Fit Analysis
     ├── JD Matching (keyword or semantic)
     │
     ▼
Mock Interview ──── AI Feedback (Groq)
     │
     ▼
Technical Quiz ──── Instant Answer Feedback
     │
     ▼
Coding Practice ─── Monaco Editor + AI Review
     │
     ▼
Progress Dashboard ─ Recharts Weekly Trend
     │
     ▼
AI Career Coach ──── Chat with History (localStorage)
```
