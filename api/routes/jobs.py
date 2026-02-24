from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging

from core.database import get_db
from models.job import Job
from api.schemas import JobResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[JobResponse])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Job).order_by(Job.created_at.desc()))
        jobs = result.scalars().all()
        return jobs
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Please ensure DATABASE_URL is correctly configured."
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    try:
        job = await db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Please ensure DATABASE_URL is correctly configured."
        )
