"""
Integration Tests using Testcontainers.
Spins up real PostgreSQL and RabbitMQ containers for realistic testing.
Tests the full API flow: schedule job -> check status -> verify in DB.
"""

import uuid
import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from testcontainers.postgres import PostgresContainer
from testcontainers.rabbitmq import RabbitMqContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from models.base import Base
from models.job import Job, JobStatus


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as pg:
        yield pg


@pytest.fixture(scope="session")
def rabbitmq_container():
    with RabbitMqContainer("rabbitmq:3-alpine") as rmq:
        yield rmq


@pytest_asyncio.fixture(scope="session")
async def db_engine(postgres_container):
    """Create all tables using the real Postgres container URL."""
    # Convert sync-style URL to asyncpg-compatible
    sync_url = postgres_container.get_connection_url()
    async_url = sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")

    engine = create_async_engine(async_url, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Yield a scoped session for each test, rolling back after."""
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def api_client(postgres_container, rabbitmq_container, db_engine):
    """
    Mount the FastAPI app with overridden dependencies pointing to
    the Testcontainers instances.
    """
    # Patch settings before importing the app so all dependencies use containers
    import os

    sync_url = postgres_container.get_connection_url()
    async_url = sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    rmq_url = f"amqp://guest:guest@{rabbitmq_container.get_container_host_ip()}:{rabbitmq_container.get_exposed_port(5672)}/"

    os.environ["DATABASE_URL"] = async_url
    os.environ["RABBITMQ_URL"] = rmq_url

    from core.config import settings
    settings.DATABASE_URL = async_url
    settings.RABBITMQ_URL = rmq_url

    # Now import the app after env vars are set
    from api.main import app
    from core.database import get_db
    from sqlalchemy.ext.asyncio import async_sessionmaker

    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


# ─────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_endpoint(api_client):
    response = await api_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_post_crawl_hockey_creates_job(api_client, db_session):
    """POST /crawl/hockey should create a Job row in pending state and return job_id."""
    response = await api_client.post("/crawl/hockey")
    assert response.status_code == 200
    data = response.json()

    assert "job_id" in data
    job_id = data["job_id"]

    # Verify the job exists in the database with PENDING status
    job = await db_session.get(Job, job_id)
    assert job is not None
    assert job.status == JobStatus.PENDING


@pytest.mark.asyncio
async def test_get_jobs_returns_list(api_client, db_session):
    """GET /jobs should return the list of all jobs."""
    # Create a job first
    await api_client.post("/crawl/oscar")
    response = await api_client.get("/jobs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_job_by_id(api_client, db_session):
    """GET /jobs/{job_id} should return the correct job."""
    create_resp = await api_client.post("/crawl/hockey")
    job_id = create_resp.json()["job_id"]

    response = await api_client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["id"] == job_id
    assert response.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_get_job_not_found(api_client):
    """GET /jobs/{unknown_id} should return 404."""
    response = await api_client.get(f"/jobs/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_results_hockey_empty(api_client):
    """GET /results/hockey should return empty list when no crawl has run."""
    response = await api_client.get("/results/hockey")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_results_oscar_empty(api_client):
    """GET /results/oscar should return empty list when no crawl has run."""
    response = await api_client.get("/results/oscar")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_job_results_returns_structure(api_client, db_session):
    """GET /jobs/{job_id}/results should return correct dict structure."""
    create_resp = await api_client.post("/crawl/all")
    job_id = create_resp.json()["job_id"]

    response = await api_client.get(f"/results/{job_id}/results")
    assert response.status_code == 200
    data = response.json()
    assert "hockey" in data
    assert "oscar" in data
