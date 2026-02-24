import json
import logging
import aio_pika
from core.config import settings

logger = logging.getLogger(__name__)


async def get_rabbitmq_connection() -> aio_pika.abc.AbstractRobustConnection:
    try:
        return await aio_pika.connect_robust(settings.RABBITMQ_URL)
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise


async def publish_message(queue_name: str, message: dict):
    try:
        connection = await get_rabbitmq_connection()
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(queue_name, durable=True)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=queue_name,
            )
            logger.info(f"Published message to {queue_name}: {message}")
    except Exception as e:
        logger.error(f"Error publishing message to {queue_name}: {e}")
        raise


async def check_rabbitmq_health() -> bool:
    """Simple check to verify RabbitMQ connectivity."""
    try:
        connection = await aio_pika.connect_robust(
            settings.RABBITMQ_URL, timeout=5
        )
        async with connection:
            return True
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        return False
