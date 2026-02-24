from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Async Engine for operations in FastAPI and asyncio contexts
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

# Async Session Factory
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    """Yields an asynchronous database session."""
    try:
        async with async_session_maker() as session:
            yield session
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise


async def check_db_health() -> bool:
    """Simple check to verify database connectivity."""
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
