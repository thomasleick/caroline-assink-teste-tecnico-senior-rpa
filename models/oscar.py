from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .base import Base


class OscarFilm(Base):
    __tablename__ = "oscar_films"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    title = Column(String, nullable=False)
    year = Column(String, nullable=False)  # Year can be string like 2015, or range
    nominations = Column(Integer, nullable=False)
    awards = Column(Integer, nullable=False)
    best_picture = Column(Boolean, default=False, nullable=False)
