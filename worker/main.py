import asyncio
import json
import logging
import aio_pika

from core.config import settings
from core.rabbitmq import get_rabbitmq_connection
from core.database import async_session_maker
from models.job import Job, JobStatus

# Ensure worker package is readable
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

QUEUE_NAME = "rpa_jobs_queue"

async def process_job(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        payload = json.loads(message.body.decode())
        job_id = payload.get("job_id")
        task_type = payload.get("task_type")
        
        logger.info(f"Received job {job_id} of type {task_type}")
        
        # update job status to RUNNING
        async with async_session_maker() as session:
            job = await session.get(Job, job_id)
            if job:
                job.status = JobStatus.RUNNING
                await session.commit()
            else:
                logger.warning(f"Job {job_id} not found in database.")
        
        try:
            # Here we will call the crawlers based on task_type
            logger.info(f"Executing task {task_type} for job {job_id}...")
            
            # Simulate work for now
            await asyncio.sleep(2)
            
            # Update job status to COMPLETED
            async with async_session_maker() as session:
                job = await session.get(Job, job_id)
                if job:
                    job.status = JobStatus.COMPLETED
                    await session.commit()
            logger.info(f"Job {job_id} completed successfully.")
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            # Update job status to FAILED
            async with async_session_maker() as session:
                job = await session.get(Job, job_id)
                if job:
                    job.status = JobStatus.FAILED
                    await session.commit()

async def main():
    logger.info("Connecting to RabbitMQ...")
    connection = await get_rabbitmq_connection()
    async with connection:
        channel = await connection.channel()
        
        # Set prefetch count to 1 so that messages are distributed evenly
        await channel.set_qos(prefetch_count=1)
        
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        
        logger.info(f"Worker started. Listening on {QUEUE_NAME}...")
        
        await queue.consume(process_job)
        
        # Wait forever
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
