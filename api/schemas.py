from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from models.job import JobStatus


class JobCreateResponse(BaseModel):
    job_id: str
    message: str


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class HockeyTeamResponse(BaseModel):
    id: int
    job_id: str
    team_name: str
    year: int
    wins: int
    losses: int
    ot_losses: Optional[int] = None
    win_percentage: Optional[float] = None
    goals_for: Optional[int] = None
    goals_against: Optional[int] = None
    goal_difference: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class OscarFilmResponse(BaseModel):
    id: int
    job_id: str
    title: str
    year: str
    nominations: int
    awards: int
    best_picture: bool
    model_config = ConfigDict(from_attributes=True)
