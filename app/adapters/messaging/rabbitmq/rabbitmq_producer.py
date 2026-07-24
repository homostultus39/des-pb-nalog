from aio_pika import Channel, DeliveryMode, Message, RobustConnection

from config.settings import get_settings

settings = get_settings()

class RabbitMQProducer:
    def __init__(self, connection: RobustConnection, routing_key: str = settings.rabbitmq.rabbitmq_status_queue):
        self._connection = connection
        self._routing_key = routing_key
        self._channel: Channel | None = None
        
    async def connect(self) -> None:
        self._channel = await self._connection.channel()
        await self._channel.declare_queue(self._routing_key, durable=True)

    async def publish(self, message: str) -> None:
        await self._channel.default_exchange.publish(
            Message(
                body = message.encode("utf-8"),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT
            ),
            routing_key=self._routing_key
        )