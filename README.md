
# Aurea — AI-Powered Interview Preparation Platform

A full-stack platform for structured interview preparation: resume analysis, mock interviews, quizzes, coding practice, an answer library, progress tracking, and an AI career coach.

---

## Features

- **Resume Analysis** — Upload PDF/DOCX, get section detection, role-fit scores, and job-description matching (semantic via embeddings, with a keyword-based fallback when no embedding key is configured).
- **Mock Interviews** — Role and topic-based sessions with per-answer scoring and AI feedback.
- **Technical Quizzes** — MCQs across CS fundamentals with instant feedback.
- **Coding Practice** — Monaco Editor (VS Code engine), test cases, code execution, and AI code review.
- **Answer Library** — Model answers across topics and difficulty levels.
- **Progress Tracking** — Streaks, weekly charts, topic mastery, field performance.
- **AI Career Coach** — Streamed chat via Groq Llama 3.3 70B; history persists client-side across browser sessions.
- **Question Administration** — Manage quiz questions at `/admin/questions`, gated by `ADMIN_EMAILS`.
- **Rate Limiting** — API-level request throttling via SlowAPI.
- **Toast Notifications** — All errors and confirmations shown as non-blocking toasts.
- **Skeleton Loaders** — Loading states on every data-heavy page.
- **Responsive Sidebar** — Hamburger menu, slide-in sidebar with backdrop dismiss on mobile.

---

## Tech Stack

| Area | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Code Editor | Monaco Editor (`@monaco-editor/react`) |
| Charts | Recharts |
| Markdown | react-markdown + rehype-sanitize |
| Notifications | react-hot-toast |
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic 2 |
| Local Database | SQLite (via `aiosqlite`, dev fallback) |
| Production Database | PostgreSQL + pgvector |
| Database Migrations | Alembic |
| AI | Groq API — `llama-3.3-70b-versatile` |
| Code Execution | Judge0 via RapidAPI + local Python fallback |
| Authentication | JWT via PyJWT 2.9.0, `httpOnly` cookies (XSS-safe) |
| Password Hashing | Passlib + bcrypt |
| Rate Limiting | SlowAPI |
| Logging | structlog |
| Error Monitoring | Sentry (optional — set `SENTRY_DSN`) |
| File Parsing | pypdf, python-docx, fpdf2 |
| Production Server | Gunicorn (behind Uvicorn workers) |
| Deployment | Docker, Docker Compose, Nginx |
| CI | GitHub Actions |

---

## Architecture

```text
Upload Resume
     │
     ├── Role Fit Analysis
     ├── JD Matching (semantic embeddings → keyword fallback)
     │
     ▼
Mock Interview ──── AI Feedback (Groq, streamed)
     │
     ▼
Technical Quiz ──── Instant Answer Feedback
     │
     ▼
Coding Practice ─── Monaco Editor + Judge0 / local execution + AI Review
     │
     ▼
Progress Dashboard ─ Recharts weekly trend
     │
     ▼
AI Career Coach ──── Streamed chat, history in browser localStorage
```

All API requests pass through JWT auth (httpOnly cookies) and SlowAPI rate limiting before reaching route handlers. Structured logs (structlog) and optional Sentry capture wrap the request lifecycle for observability.

---

## Project Structure

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
│       ├── tests/                ← pytest suite (async-mode auto)
│       ├── requirements.txt
│       ├── alembic.ini
│       ├── pytest.ini
│       ├── Dockerfile
│       ├── .dockerignore
│       └── .env                  ← never commit this
│
├── frontend/                     ← Next.js frontend
│   ├── src/
│   │   ├── app/                  ← all pages
│   │   │   ├── chat/  coding/  dashboard/  interview/  library/
│   │   │   ├── login/  progress/  quiz/  register/  resume/
│   │   │   ├── sessions/  admin/questions/
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
├── setup.bat                     ← one-time backend venv + dependency setup
├── start.bat                     ← daily launcher (backend + frontend)
└── README.md
```

---

## Local Setup (Windows)

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- PowerShell
- Git

### Step 1 — Backend Setup (run once)

```powershell
cd path\to\aurea-v2\aurea-v2\backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

# If activation is blocked, run this once then activate again
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Copy-Item .env.example .env
```

> A `setup.bat` script is also provided as a shortcut for this step. **Note:** if you use `setup.bat`, check that it creates the virtual environment at `.venv` (not `venv`) — `start.bat` specifically looks for `.venv`, so the two must agree on the folder name.

### Step 2 — Frontend Setup (run once)

```powershell
cd path\to\aurea-v2\frontend
npm install
```

Create `frontend\.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

### Step 3 — Configure Backend Environment

Edit `aurea-v2\backend\.env`:

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

# Optional — enables Sentry error monitoring
SENTRY_DSN=your_sentry_dsn_here
```

> `GROQ_API_KEY` and `JUDGE0_API_KEY` are different services. Groq powers AI. Judge0 powers non-Python code execution.

---

## Running the App

**Two terminals (recommended — clean logs for both servers):**

```powershell
# Terminal 1 — Backend
cd path\to\aurea-v2\aurea-v2\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

```powershell
# Terminal 2 — Frontend
cd path\to\aurea-v2\frontend
npm run dev
```

Open **http://localhost:3000** — API docs at **http://127.0.0.1:8000/docs**.

**Or, one command from the project root:**

```powershell
.\start.bat
```

This checks that `.venv` and `node_modules` exist, then opens two terminal windows automatically.

---

## Application Routes

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

## API Overview

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

All endpoints are rate-limited via SlowAPI. Full interactive docs at `http://127.0.0.1:8000/docs` (development only).

---

## Database Migrations

Run from `backend/`, with `.venv` active. Migration filenames are timestamped (`YYYYMMDD_HHMM_<rev>_<slug>`) and revision timestamps are recorded in UTC.

```powershell
python -m alembic upgrade head          # apply all pending migrations
python -m alembic current               # show current revision
python -m alembic history --verbose     # show full history
python -m alembic downgrade -1          # roll back one migration
python -m alembic revision --autogenerate -m "describe your change"
```

---

## Verification Commands

```powershell
# Backend tests (pytest, async-mode auto)
cd path\to\aurea-v2\aurea-v2\backend
.\.venv\Scripts\python.exe -m pytest -q

# Frontend TypeScript check
cd path\to\aurea-v2\frontend
.\node_modules\.bin\tsc.cmd --noEmit

# Frontend lint (specific files — full lint is slow)
.\node_modules\.bin\eslint.cmd src/app src/components src/lib

# Production build check
npm run build
```

---

## Docker (Production)

```powershell
docker compose up --build -d
```

The stack:
- `pgvector/pgvector:pg16` for PostgreSQL with vector support
- FastAPI backend served via Gunicorn/Uvicorn workers, built from the backend `Dockerfile` (with a `.dockerignore` to keep the build context lean)
- Next.js frontend
- Nginx as reverse proxy on port 80
- Health checks on database and backend services

Before production: set strong secrets, use PostgreSQL (not SQLite), and configure real API keys.

### PostgreSQL + pgvector

The Docker stack enables the `vector` extension automatically. For managed providers (Neon, Supabase), enable it manually:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Then set `EMBEDDING_API_KEY` in the backend `.env` and restart the backend. Re-embed existing resumes using **Resume → Refresh analysis**.

---

## GitHub Actions CI

Runs on every push and pull request to `main` or `master`:

1. Backend pytest suite
2. TypeScript type check
3. ESLint
4. Production Next.js build

No secrets required for CI — live AI services are not called in tests.

---

## Security Notes

- Never commit `.env`, `.env.local`, API keys, or the SQLite database file (`.gitignore` covers `.env*`, `*.db`, `*.sqlite*`).
- Generate a unique `SECRET_KEY` per environment — never reuse across dev/prod.
- **JWT library:** PyJWT 2.9.0 (replaced python-jose, which had CVE-2024-33664).
- **Password storage:** hashed via Passlib + bcrypt — plaintext passwords are never stored.
- **Auth tokens:** stored in `httpOnly` cookies, inaccessible to JavaScript (XSS protection); `secure=True` set automatically in production.
- **Rate limiting:** enforced at the API layer via SlowAPI to reduce brute-force and abuse risk.
- **JD Matching:** keyword analysis by default; set `EMBEDDING_API_KEY` for semantic vector matching. The UI labels which method is active.
- **Error monitoring:** set `SENTRY_DSN` in `backend/.env` to enable Sentry (free tier is sufficient for portfolio use).
- AI prompt injection filtering is a safety layer, not a guarantee.
- Local Python code execution has no sandbox — use Judge0 for any public/production deployment.
- Use PostgreSQL and enforce rate limiting for any public deployment; SQLite is for local development only.

---

## Troubleshooting

**`requirements.txt` not found** — wrong directory; `cd` into `aurea-v2\backend`.

**`No module named uvicorn`**
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Frontend cannot reach backend**
1. Confirm `http://127.0.0.1:8000/health` opens in browser.
2. Confirm `frontend\.env.local` has `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api`.
3. Restart both servers after editing any `.env` file.

**AI chat / resume analysis / code review not working**
1. Set `GROQ_API_KEY=gsk_...` in `aurea-v2\backend\.env`.
2. Restart the backend.
3. Do not put the Groq key in `frontend\.env.local`.

**Java / C++ / JavaScript execution not working** — add `JUDGE0_API_KEY` to the backend `.env`, then restart. Python runs locally without it.

**Monaco Editor not loading** — run `npm install` in `frontend/` to ensure `@monaco-editor/react` is installed.

**Toast notifications not appearing** — ensure `<ToastProvider />` is present in `src/app/layout.tsx` (included by default).

**Chat history not persisting** — history is stored in browser `localStorage`, not the database; clearing browser data removes it. This is expected behavior.

**`setup.bat` succeeds but `start.bat` says the venv is missing** — the two scripts must create/expect the same folder name (`.venv`). If `setup.bat` created a `venv` folder instead, rename it to `.venv` or update the script.

**Port 3000 already in use**
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Disk space errors during `npm install`**
```powershell
npm cache clean --force
Remove-Item -Recurse -Force "path\to\aurea-v2\frontend\.next"
```

---

## License

MIT License
