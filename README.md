# Aurea — AI-Powered Interview Preparation Platform

A full-stack platform for structured interview preparation: resume analysis, mock interviews, quizzes, coding practice, answer guides, progress tracking, and an AI career coach.

## What you can do

- Upload a PDF or DOCX resume and get section detection, role-fit analysis, and job-description matching.
- Take role and topic-based mock interviews with feedback and saved session history.
- Practise MCQ quizzes across core CS topics.
- Solve coding problems, run Python locally without a Judge0 key, and get AI-assisted code reviews.
- Browse model answer guides across interview topics and difficulties.
- Track attempts, scores, streaks, weekly activity, and topic performance.
- Chat with the Aurea AI coach when Groq is configured.
- Manage quiz questions from `/admin/questions` for configured admin emails.

## Tech stack

| Area | Technology |
| --- | --- |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Local database | SQLite |
| Production database | PostgreSQL (Docker configuration included) |
| AI | Groq API |
| Code execution | Judge0 via RapidAPI, with local Python fallback |
| Auth | JWT access and refresh tokens |
| Deployment files | Docker, Docker Compose, Nginx |

## Project structure

> Important: the actual backend is inside the nested `aurea-v2\backend` folder. Do **not** use the separate root-level `backend` folder.

```text
aurea-v2/                         # project root
├── aurea-v2/
│   └── backend/                   # FastAPI backend — use this folder
│       ├── app/
│       ├── tests/
│       ├── requirements.txt
│       └── .env                   # create this locally; never commit it
├── frontend/                      # Next.js frontend
│   └── .env.local                 # create this locally
├── nginx/                         # production reverse-proxy config
├── docker-compose.yml
└── start.bat                      # starts backend + frontend on Windows
```

## Run locally on Windows

### First-time setup

Open **PowerShell** in the project root:

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2"
```

### 1. Set up the backend once

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, run this once for the current terminal, then repeat the activation command:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2. Set up the frontend once

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\frontend"
npm install
```

Create `frontend\.env.local` with this one line:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

### 3. Configure backend environment variables

Open this exact file:

```text
C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend\.env
```

Use a local-development configuration like this. Never share or commit real keys.

```env
DATABASE_URL=sqlite:///./aurea_v2.db
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_ENV=development
FRONTEND_URL=http://localhost:3000

# Required for chat, resume semantic analysis, interview feedback, and AI code review
GROQ_API_KEY=gsk_your_key_here

# Optional: enables Java, JavaScript, C++ and other Judge0-supported executions
JUDGE0_API_KEY=your_rapidapi_key_here

# Optional: comma-separated emails allowed to manage questions at /admin/questions
ADMIN_EMAILS=you@example.com
```

`GROQ_API_KEY` and `JUDGE0_API_KEY` are different keys:

- Groq powers the AI features.
- Judge0 powers cloud code execution for non-Python languages.
- Without Judge0, Python can still run using the local fallback; other languages show a clear configuration message.

## Start the project every day

### Easiest: one command

From the **project root**, run:

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2"
.\start.bat
```

This opens two terminal windows:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:3000`

Keep both windows open while using Aurea. Stop the app by pressing `Ctrl + C` in each window.

You may also double-click `start.bat` in File Explorer. In VS Code, use **Terminal → New Terminal** and run the command above; the Explorer right-click menu does not include a reliable “Run batch file” option.

### Manual: two terminals

Use this if you want to see backend and frontend logs separately.

**Terminal 1 — backend**

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — frontend**

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\frontend"
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000). API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Useful verification commands

Run these after setup or before submitting the project.

```powershell
# Backend tests
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"
.\.venv\Scripts\python.exe -m pytest -q

# Frontend type check
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\frontend"
.\node_modules\.bin\tsc.cmd --noEmit

# Frontend lint
npm run lint

# Production frontend build
npm run build
```

## Main routes

| Page | Route |
| --- | --- |
| Dashboard | `/dashboard` |
| Resume analysis | `/resume` |
| Mock interview | `/interview` |
| Quiz | `/quiz` |
| Coding practice | `/coding` |
| Answer library | `/library` |
| AI coach chat | `/chat` |
| Progress | `/progress` |
| Session history | `/sessions` |
| Question admin | `/admin/questions` |

## API overview

| Module | Base path | Examples |
| --- | --- | --- |
| Auth | `/api/auth` | register, login, refresh, current user |
| Resume | `/api/resume` | upload/analyze, refresh analysis, job-description match |
| Interview | `/api/interview` | questions, answer evaluation, session saving |
| Quiz | `/api/quiz` | topics, questions, answer submission |
| Coding | `/api/coding` | problems, execution, AI review |
| Progress | `/api/progress` | activity summary and weekly metrics |
| Chat | `/api/chat` | AI coach streaming responses |
| Admin | `/api/admin/questions` | question CRUD for admin emails |

Browse the full interactive API at `http://127.0.0.1:8000/docs` while the backend is running.

## Production notes

Docker, Compose, Nginx, and PostgreSQL configuration are included for deployment:

```powershell
docker compose up --build -d
```

Before production, set strong non-default secrets, use PostgreSQL, set the production frontend URL, and configure real Groq/Judge0 keys. SQLite is suitable for local development only; it is not intended for concurrent production traffic.

## Troubleshooting

### `requirements.txt` not found

You are in the wrong directory. The correct command is:

```powershell
Set-Location -LiteralPath "C:\Users\sanskriti\OneDrive\Desktop\aurea-v2\aurea-v2\backend"
```

### `No module named uvicorn`

The virtual environment is missing dependencies. In the correct backend folder run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Frontend says it cannot reach the backend

1. Confirm `http://127.0.0.1:8000/health` opens in the browser.
2. Confirm the frontend environment file contains `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api`.
3. Restart both servers after editing any `.env` file.

### AI chat, resume semantic analysis, or AI review does not work

1. Put `GROQ_API_KEY=gsk_...` in the **inner** `aurea-v2\backend\.env` file.
2. Restart the backend.
3. Do not put the Groq key in the frontend `.env.local` file.

### Java or C++ code execution does not work

Add a valid `JUDGE0_API_KEY` to the inner backend `.env`, then restart the backend. This is a separate RapidAPI/Judge0 credential from Groq.

### Port 3000 is already in use

Use the existing frontend at `http://localhost:3000`, or stop the old process:

```powershell
taskkill /PID <PID_SHOWN_BY_NEXT> /F
```

### Pip says there is no disk space

Free some C: drive space, then optionally clear the pip download cache:

```powershell
python -m pip cache purge
```

## Security reminders

- Never commit `.env`, `.env.local`, API keys, or the local SQLite database.
- Generate a unique `SECRET_KEY` for every production environment.
- Treat AI prompt filtering as a safety layer, not a complete guarantee against prompt injection.
- Apply rate limits and use PostgreSQL for an actual public deployment.
