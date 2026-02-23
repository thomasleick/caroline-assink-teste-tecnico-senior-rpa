from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import settings

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
    async with async_session_maker() as session:
        yield session
