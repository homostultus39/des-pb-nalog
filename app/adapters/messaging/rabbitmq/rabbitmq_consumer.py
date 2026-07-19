import json
from aio_pika import RobustConnection, IncomingMessage

from config.settings import get_settings
from domain.use_cases.search_directors import SearchDirectorsUseCase
from adapters.messaging.rabbitmq.rabbitmq_producer import RabbitMQProducer
from adapters.messaging.kafka.kafka_producer import KafkaProducer


settings = get_settings()

class RabbitMQConsumer:
    def __init__(self, connection: RobustConnection, use_case: SearchDirectorsUseCase, rmq_producer: RabbitMQProducer, kafka_producer: KafkaProducer):
        self._connection = connection
        self._use_case = use_case
        self._rmq_producer = rmq_producer
        self._kafka_producer = kafka_producer

    async def start(self):
        channel = await self._connection.channel()
        queue = await channel.declare_queue(settings.rabbitmq.rabbitmq_task_queue, durable=True, auto_delete=True)

        await queue.consume(self._on_message)
    
    async def _on_message(self, message: IncomingMessage):
        async with message.process():
            body = json.loads(message.body)
            search_string = body["search_string"]

            try:
                entities = await self._use_case.execute(search_string=search_string)
            except Exception as e:
                pass

            for entity in entities:
                # Распаковываем сущности, валидируем в 

                await self._rmq_producer.publish(message=entity.model_dump_json())