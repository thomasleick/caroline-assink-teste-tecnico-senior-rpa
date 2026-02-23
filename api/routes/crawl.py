from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.rabbitmq import publish_message
from models.job import Job
from api.schemas import JobCreateResponse

# Using same queue name implicitly or importing from worker isn't ideal due to circular dependency
QUEUE_NAME = "rpa_jobs_queue"

router = APIRouter()


async def create_job_and_publish(db: AsyncSession, task_type: str) -> str:
    # 1. Create a job pending in DB
    new_job = Job()
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # 2. Publish message
    message = {"job_id": new_job.id, "task_type": task_type}
    await publish_message(QUEUE_NAME, message)

    return new_job.id


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
