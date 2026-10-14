import logging
import socket
from typing import AsyncGenerator
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def is_database_reachable(url_str: str) -> bool:
    """
    Checks if PostgreSQL host and port are reachable before initializing engine.
    """
    if "sqlite" in url_str:
        return True
    try:
        # Strip asyncpg prefix for urlparse
        clean_url = url_str.replace("+asyncpg", "")
        parsed = urlparse(clean_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            return s.connect_ex((host, port)) == 0
    except Exception as e:
        logger.debug(f"Socket check failed: {e}")
        return False

# Determine initial database URL
chosen_url = settings.DATABASE_URL
if chosen_url.startswith("postgresql://"):
    chosen_url = chosen_url.replace("postgresql://", "postgresql+asyncpg://", 1)

if not is_database_reachable(chosen_url):
    logger.info(f"PostgreSQL at {chosen_url} is not currently running. Using SQLite fallback: {settings.SQLITE_FALLBACK_URL}")
    chosen_url = settings.SQLITE_FALLBACK_URL

engine = create_async_engine(
    chosen_url,
    echo=False,
    future=True,
    pool_pre_ping=True if "sqlite" not in chosen_url else False
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

def get_session():
    """Returns an async session context manager."""
    return async_session_maker()

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Database schema initialized successfully using {chosen_url}")
    except Exception as e:
        logger.error(f"Error during init_db: {e}")
        raise

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
