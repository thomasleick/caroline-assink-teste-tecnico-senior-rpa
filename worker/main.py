import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
import aio_pika

from core.rabbitmq import get_rabbitmq_connection
from core.database import async_session_maker
from models.job import Job, JobStatus
from models.hockey import HockeyTeam
from models.oscar import OscarFilm
from worker.crawlers.hockey import scrape_hockey_teams
from worker.crawlers.oscar import scrape_oscar_films

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

QUEUE_NAME = "rpa_jobs_queue"

# Thread pool for running sync Selenium scraper without blocking event loop
_executor = ThreadPoolExecutor(max_workers=2)

app = FastAPI(title="RPA Worker Health Check")


async def _update_job_status(job_id: str, status: JobStatus) -> None:
    async with async_session_maker() as session:
        job = await session.get(Job, job_id)
        if job:
            job.status = status
            await session.commit()


async def _run_hockey(job_id: str) -> None:
    logger.info(f"[{job_id}] Starting Hockey scraper...")
    teams = await scrape_hockey_teams()
    async with async_session_maker() as session:
        for team in teams:
            session.add(HockeyTeam(job_id=job_id, **team))
        await session.commit()
    logger.info(f"[{job_id}] Saved {len(teams)} hockey records.")


async def _run_oscar(job_id: str) -> None:
    logger.info(f"[{job_id}] Starting Oscar scraper (Selenium)...")
    # Selenium is synchronous; run in thread pool to avoid blocking event loop
    from typing import cast, List, Dict, Any

    loop = asyncio.get_running_loop()
    films: List[Dict[str, Any]] = cast(
        List[Dict[str, Any]],
        await loop.run_in_executor(_executor, scrape_oscar_films),
    )
    async with async_session_maker() as session:
        for film in films:
            session.add(OscarFilm(job_id=job_id, **film))
        await session.commit()
    logger.info(f"[{job_id}] Saved {len(films)} Oscar records.")


async def process_job(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process():
        payload = json.loads(message.body.decode())
        job_id = payload.get("job_id")
        task_type = payload.get("task_type")

        logger.info(f"Received job {job_id} | type={task_type}")
        await _update_job_status(job_id, JobStatus.RUNNING)

        try:
            if task_type == "hockey":
                await _run_hockey(job_id)
            elif task_type == "oscar":
                await _run_oscar(job_id)
            elif task_type == "all":
                await _run_hockey(job_id)
                await _run_oscar(job_id)
            else:
                raise ValueError(f"Unknown task_type: {task_type}")

            await _update_job_status(job_id, JobStatus.COMPLETED)
            logger.info(f"[{job_id}] Job completed successfully.")

        except Exception as exc:
            logger.exception(f"[{job_id}] Job failed: {exc}")
            await _update_job_status(job_id, JobStatus.FAILED)


@app.get("/")
async def health():
    return {"status": "ok"}


async def run_worker() -> None:
    logger.info("Connecting to RabbitMQ...")
    retry_interval = 5
    while True:
        try:
            connection = await get_rabbitmq_connection()
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=1)
                queue = await channel.declare_queue(QUEUE_NAME, durable=True)
                logger.info(f"Worker started. Listening on queue '{QUEUE_NAME}'...")
                await queue.consume(process_job)
                await asyncio.Future()  # run forever until connection is lost
        except Exception as e:
            logger.error(
                f"Failed to connect to RabbitMQ: {e}. Retrying in {retry_interval}s..."
            )
            await asyncio.sleep(retry_interval)


@app.on_event("startup")
async def startup_event():
    # Start the worker in the background
    asyncio.create_task(run_worker())
