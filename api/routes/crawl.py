from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from core.database import get_db, check_db_health
from core.rabbitmq import publish_message, check_rabbitmq_health
from models.job import Job
from api.schemas import JobCreateResponse

logger = logging.getLogger(__name__)

# Using same queue name implicitly or importing from worker isn't ideal due to circular dependency
QUEUE_NAME = "rpa_jobs_queue"

router = APIRouter()


async def create_job_and_publish(db: AsyncSession, task_type: str) -> str:
    try:
        # 1. Create a job pending in DB
        new_job = Job()
        db.add(new_job)
        await db.commit()
        await db.refresh(new_job)
    except Exception as e:
        logger.error(f"Failed to create job in database: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Please ensure DATABASE_URL is correctly configured.",
        )

    try:
        # 2. Publish message
        message = {"job_id": new_job.id, "task_type": task_type}
        await publish_message(QUEUE_NAME, message)
    except Exception as e:
        logger.error(f"Failed to publish message to RabbitMQ: {e}")
        # If queue fails, we probably should mark the job as failed or just raise
        raise HTTPException(
            status_code=503,
            detail="Queue connection failed. Please ensure RABBITMQ_URL is correctly configured.",
        )

    return new_job.id


@router.get("/health")
async def health_check():
    db_ok = await check_db_health()
    rmq_ok = await check_rabbitmq_health()
    return {
        "status": "ok" if db_ok and rmq_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "rabbitmq": "connected" if rmq_ok else "disconnected",
    }


@router.post("/hockey", response_model=JobCreateResponse)
async def crawl_hockey(db: AsyncSession = Depends(get_db)):
    job_id = await create_job_and_publish(db, "hockey")
    return {"job_id": job_id, "message": "Hockey crawling task scheduled."}


@router.post("/oscar", response_model=JobCreateResponse)
async def crawl_oscar(db: AsyncSession = Depends(get_db)):
    job_id = await create_job_and_publish(db, "oscar")
    return {"job_id": job_id, "message": "Oscar crawling task scheduled."}


@router.post("/all", response_model=JobCreateResponse)
async def crawl_all(db: AsyncSession = Depends(get_db)):
    job_id = await create_job_and_publish(db, "all")
    return {
        "job_id": job_id,
        "message": "Combined hockey and oscar crawling task scheduled.",
    }
