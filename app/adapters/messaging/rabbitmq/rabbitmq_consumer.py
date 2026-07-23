import json
from aio_pika import RobustConnection, IncomingMessage

from config.settings import get_settings
from adapters.messaging.logger import logger
from domain.use_cases.search_directors import SearchDirectorsUseCase
from adapters.messaging.rabbitmq.rabbitmq_producer import RabbitMQProducer
from adapters.messaging.kafka.kafka_producer import KafkaProducer
from adapters.messaging.schemas import KafkaResponseDTO, RabbitMQStatusMessage, StatusResponseDTO, RequestDTO, KafkaResponseMessage

settings = get_settings()

class RabbitMQConsumer:
    def __init__(self, connection: RobustConnection, use_case: SearchDirectorsUseCase, rmq_producer: RabbitMQProducer, kafka_producer: KafkaProducer):
        self._connection = connection
        self._use_case = use_case
        self._rmq_producer = rmq_producer
        self._kafka_producer = kafka_producer

    async def start(self):
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(settings.rabbitmq.rabbitmq_task_queue, durable=True)
        await queue.consume(self._on_message)
    
    async def _on_message(self, message: IncomingMessage):
        body = json.loads(message.body)
        search_string = body.get("search_string")

        result = await self._use_case.execute(search_string=search_string)

        await self._rmq_producer.publish(
            message=RabbitMQStatusMessage(
                request=RequestDTO(search_string=search_string),
                response=StatusResponseDTO(
                    success=result.success,
                    error=result.error,
                    duration=result.duration,
                    collect_time=result.collect_time,
                    total=result.total
                )
            ).model_dump_json()
        )
        
        if result.success:
            for entity in result.entities:
                await self._kafka_producer.publish(
                    message=KafkaResponseMessage(
                        request=RequestDTO(search_string=search_string),
                        response=KafkaResponseDTO(
                            success=result.success,
                            error=result.error,
                            duration=result.duration,
                            total=result.total,
                            collect_time=result.collect_time,
                            person=entity.person,
                            organization=entity.organization
                        )
                    ).model_dump_json()
                )
        logger.info(f"Обработка сообщения завершена для search_string={search_string}; success={result.success}")
        await message.ack()