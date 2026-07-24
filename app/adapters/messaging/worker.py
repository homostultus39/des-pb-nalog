import asyncio

from aio_pika import connect_robust
from aiokafka import AIOKafkaProducer

from adapters.messaging.kafka.kafka_producer import KafkaProducer
from adapters.messaging.logger import logger
from adapters.messaging.rabbitmq.rabbitmq_consumer import RabbitMQConsumer
from adapters.messaging.rabbitmq.rabbitmq_producer import RabbitMQProducer
from adapters.pb_nalog.http_client.client_instance import HTTPClient
from config.settings import get_settings
from domain.use_cases.search_directors import SearchDirectorsUseCase

settings = get_settings()

async def worker_start_polling(client: HTTPClient) -> None:
    connection = await connect_robust(url=settings.rabbitmq.rabbitmq_url)
    
    rmq_producer = RabbitMQProducer(connection=connection)
    await rmq_producer.connect()

    kafka_conn = AIOKafkaProducer(bootstrap_servers=settings.kafka.kafka_bootstrap_servers)
    await kafka_conn.start()
    kafka_producer = KafkaProducer(producer=kafka_conn)

    use_case = SearchDirectorsUseCase(client=client)

    rmq_consumer = RabbitMQConsumer(
        connection=connection,
        use_case=use_case,
        rmq_producer=rmq_producer,
        kafka_producer=kafka_producer
    )
    
    await rmq_consumer.start()

    logger.info(f"Воркер запущен, слушает очередь {settings.rabbitmq.rabbitmq_task_queue}")
    
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        logger.info("Воркер получил сигнал остановы")
    finally:
        await connection.close()
        await kafka_conn.stop()