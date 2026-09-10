from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from typing import Optional
import secrets


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./aurea_v2.db"

    # JWT — must be set in production
    SECRET_KEY: str = secrets.token_hex(32)  # auto-generated fallback for dev only
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI
    GROQ_API_KEY: Optional[str] = None
    # Groq retired llama-3.3-70b-versatile for developer-tier accounts in August 2026.
    # Keep this configurable so deployments can select a model available to their account.
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    # OpenAI-compatible embeddings endpoint. Keep this separate from GROQ_API_KEY:
    # chat models and embedding models are different services.
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_BASE_URL: str = "https://api.openai.com/v1"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Code execution
    JUDGE0_API_KEY: Optional[str] = None
    JUDGE0_BASE_URL: str = "https://judge0-ce.p.rapidapi.com"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10
    AI_RATE_LIMIT_PER_MINUTE: int = 20
    ADMIN_EMAILS: str = ""

    # App
    APP_ENV: str = "development"
    # Comma-separated list of allowed CORS origins, e.g. "https://aurea.vercel.app"
    FRONTEND_URL: str = "http://localhost:3000"

    @property
    def allowed_origins(self) -> list[str]:
        origins = [u.strip() for u in self.FRONTEND_URL.split(",") if u.strip()]
        if "http://localhost:3000" not in origins:
            origins.append("http://localhost:3000")
        return origins

    # Monitoring — optional, set to enable Sentry error tracking
    SENTRY_DSN: Optional[str] = None

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        if v not in ("development", "staging", "production"):
            raise ValueError("APP_ENV must be development, staging, or production")
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def admin_emails(self) -> set[str]:
        return {email.strip().lower() for email in self.ADMIN_EMAILS.split(",") if email.strip()}

    @model_validator(mode="after")
    def production_safety_checks(self):
        """Reject insecure or demo-only settings before a production server starts."""
        if not self.is_production:
            return self

        insecure_values = {
            "aurea-dev-secret-key-change-in-production-2024",
            "CHANGE_THIS_GENERATE_WITH_SECRETS_TOKEN_HEX_32",
        }
        if self.SECRET_KEY in insecure_values:
            raise ValueError("Set a unique SECRET_KEY for production; do not use the example value.")
        if self.is_sqlite:
            raise ValueError("Production requires PostgreSQL. Set DATABASE_URL to a postgresql:// URL.")
        # Render emits postgres:// — fix it for SQLAlchemy
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        if not self.DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://")):
            raise ValueError("Production DATABASE_URL must use PostgreSQL.")
        return self

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
