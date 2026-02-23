from sqlalchemy import Column, Integer, String, Float, ForeignKey
from .base import Base


class HockeyTeam(Base):
    __tablename__ = "hockey_teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    team_name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    wins = Column(Integer, nullable=False)
    losses = Column(Integer, nullable=False)
    ot_losses = Column(
        Integer, nullable=True
    )  # Assuming OT can be None/Optional based on year
    win_percentage = Column(Float, nullable=True)
    goals_for = Column(Integer, nullable=True)
    goals_against = Column(Integer, nullable=True)
    goal_difference = Column(Integer, nullable=True)
