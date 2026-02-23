from typing import List, Dict, Any, Union
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database import get_db
from models.job import Job
from models.hockey import HockeyTeam
from models.oscar import OscarFilm
from api.schemas import HockeyTeamResponse, OscarFilmResponse

router = APIRouter()

@router.get("/{job_id}/results", response_model=Dict[str, Union[List[HockeyTeamResponse], List[OscarFilmResponse]]])
async def get_job_results(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Fetch results from both tables associated with this job
    hockey_result = await db.execute(select(HockeyTeam).where(HockeyTeam.job_id == job_id))
    hockey_teams = hockey_result.scalars().all()
    
    oscar_result = await db.execute(select(OscarFilm).where(OscarFilm.job_id == job_id))
    oscar_films = oscar_result.scalars().all()
    
    return {
        "hockey": hockey_teams,
        "oscar": oscar_films
    }

@router.get("/hockey", response_model=List[HockeyTeamResponse])
async def list_hockey_results(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HockeyTeam))
    return result.scalars().all()

@router.get("/oscar", response_model=List[OscarFilmResponse])
async def list_oscar_results(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OscarFilm))
    return result.scalars().all()
