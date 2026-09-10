import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.database import Base, engine
import app.models  # Ensure every model, including pgvector tables, is registered before create_all.
from app.routers import auth, resume, interview, quiz, coding, progress, chat, library, admin

# ── Sentry error monitoring (optional — set SENTRY_DSN in .env to enable) ────
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=0.2,   # 20% of requests tracked for performance
        send_default_pii=False,   # never send user PII to Sentry
    )

# ── Structured logging ────────────────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer() if not settings.is_production else structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

# ── Database tables ───────────────────────────────────────────────────────────
if not settings.is_sqlite:
    # The pgvector Docker image includes this extension. Managed PostgreSQL users
    # should enable the `vector` extension once in their database dashboard.
    from sqlalchemy import text
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
Base.metadata.create_all(bind=engine)
log.info("database_ready", url=settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "sqlite")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Auréa V2 API",
    description="AI-powered interview preparation platform",
    version="2.0.0",
    docs_url="/docs" if not settings.is_production else None,   # hide docs in prod
    redoc_url="/redoc" if not settings.is_production else None,
)

# Rate limiter middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request logging middleware ────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    log.info("request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        ip=get_remote_address(request),
    )
    return response

# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(interview.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")
app.include_router(coding.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(library.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Auréa V2 API", "version": "2.0.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV, "db": "sqlite" if settings.is_sqlite else "postgresql"}
