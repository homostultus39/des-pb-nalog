import json
from aiokafka import AIOKafkaProducer

from config.settings import get_settings


settings = get_settings()

class KafkaProducer:
    def __init__(self, producer: AIOKafkaProducer, topic: str = settings.kafka.kafka_response_topic):
        self._producer = producer
        self._topic = topic

    async def publish(self, message: str) -> None:
        await self._producer.send_and_wait(self._topic, message.encode("utf-8"))