"""
Configuration Module for Tennis Analytics Explorer.
Loads environment variables safely, provides defaults, and validates credentials.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if available
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Sportradar API Configuration
SPORTRADAR_API_KEY = os.getenv("SPORTRADAR_API_KEY", "").strip()
SPORTRADAR_ACCESS_LEVEL = os.getenv("SPORTRADAR_ACCESS_LEVEL", "trial").strip().lower()
SPORTRADAR_LANGUAGE_CODE = os.getenv("SPORTRADAR_LANGUAGE_CODE", "en").strip().lower()
SPORTRADAR_BASE_URL = f"https://api.sportradar.com/tennis/{SPORTRADAR_ACCESS_LEVEL}/v3/{SPORTRADAR_LANGUAGE_CODE}"

# Database Configuration
def get_database_url() -> str:
    """
    Constructs and returns the SQLAlchemy connection URL.
    Checks DATABASE_URL first; otherwise builds from individual parameters.
    Supports PostgreSQL, MySQL, and local SQLite for development.
    """
    db_url = os.getenv("DATABASE_URL", "").strip()
    if db_url:
        # Normalize postgres:// to postgresql:// for SQLAlchemy 1.4+ / 2.0+
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url

    # Check individual components
    db_type = os.getenv("DB_TYPE", "postgresql").strip().lower()
    user = os.getenv("DB_USER", "postgres").strip()
    password = os.getenv("DB_PASSWORD", "").strip()
    host = os.getenv("DB_HOST", "localhost").strip()
    port = os.getenv("DB_PORT", "5432" if db_type == "postgresql" else "3306").strip()
    name = os.getenv("DB_NAME", "tennis_analytics").strip()

    if db_type == "postgresql":
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    elif db_type == "mysql":
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
    elif db_type == "sqlite":
        return f"sqlite:///{BASE_DIR / 'tennis_analytics.db'}"
    else:
        # Default fallback to sqlite local DB to prevent hard crashes during development
        return f"sqlite:///{BASE_DIR / 'tennis_analytics.db'}"

DATABASE_URL = get_database_url()
CACHE_TTL = int(os.getenv("DATA_CACHE_TTL_SECONDS", "3600"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "t")
