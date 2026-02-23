"""
Unit tests for Pydantic API schemas.
Validate that the schema types coerce and validate correctly.
"""
import pytest
from datetime import datetime, timezone
from models.job import JobStatus
from api.schemas import (
    JobCreateResponse,
    JobResponse,
    HockeyTeamResponse,
    OscarFilmResponse,
)


def test_job_create_response_fields():
    resp = JobCreateResponse(job_id="abc-123", message="Scheduled")
    assert resp.job_id == "abc-123"
    assert resp.message == "Scheduled"


def test_job_response_from_orm():
    now = datetime.now(timezone.utc)
    resp = JobResponse(
        id="abc-123",
        status=JobStatus.PENDING,
        created_at=now,
        updated_at=now,
    )
    assert resp.status == JobStatus.PENDING


def test_hockey_team_response_optional_fields():
    resp = HockeyTeamResponse(
        id=1,
        job_id="abc-123",
        team_name="Boston Bruins",
        year=1990,
        wins=44,
        losses=24,
    )
    assert resp.ot_losses is None
    assert resp.win_percentage is None


def test_hockey_team_response_with_all_fields():
    resp = HockeyTeamResponse(
        id=1,
        job_id="abc-123",
        team_name="Boston Bruins",
        year=1990,
        wins=44,
        losses=24,
        ot_losses=12,
        win_percentage=0.563,
        goals_for=299,
        goals_against=264,
        goal_difference=35,
    )
    assert resp.goals_for == 299
    assert abs(resp.win_percentage - 0.563) < 1e-6


def test_oscar_film_response():
    resp = OscarFilmResponse(
        id=1,
        job_id="abc-123",
        title="Parasite",
        year="2019",
        nominations=6,
        awards=4,
        best_picture=True,
    )
    assert resp.best_picture is True
    assert resp.title == "Parasite"


def test_oscar_film_default_best_picture_false():
    resp = OscarFilmResponse(
        id=1,
        job_id="abc-123",
        title="Some Film",
        year="2020",
        nominations=2,
        awards=0,
        best_picture=False,
    )
    assert resp.best_picture is False
