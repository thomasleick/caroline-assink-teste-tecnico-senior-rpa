import json
import logging
import aio_pika
from core.config import settings

logger = logging.getLogger(__name__)


async def get_rabbitmq_connection() -> aio_pika.abc.AbstractRobustConnection:
    return await aio_pika.connect_robust(settings.RABBITMQ_URL)


async def publish_message(queue_name: str, message: dict):
    connection = await get_rabbitmq_connection()
    async with connection:
        channel = await connection.channel()
        _queue = await channel.declare_queue(queue_name, durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue_name,
        )
        logger.info(f"Published message to {queue_name}: {message}")
