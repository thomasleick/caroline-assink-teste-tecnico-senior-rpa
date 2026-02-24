import asyncio
import sys
import os
import logging

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings
from models.base import Base
# Import all models to ensure they are registered with Base metadata
import models.job
import models.hockey
import models.oscar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    logger.info(f"Using DATABASE_URL: {settings.DATABASE_URL}")
    
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        
        async with engine.begin() as conn:
            logger.info("Creating all tables in the database...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("All tables created successfully.")
        
        await engine.dispose()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(init_db())
