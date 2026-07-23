from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):
    kafka_response_topic: str
    kafka_host: str
    kafka_port: int

    @property
    def kafka_bootstrap_servers(self):
        return f"{self.kafka_host}:{self.kafka_port}"

class RabbitMQSettings(BaseSettings):
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_default_user: str
    rabbitmq_default_password: str

    rabbitmq_task_queue: str
    rabbitmq_status_queue: str

    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_default_user}:{self.rabbitmq_default_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/"

class Settings(BaseSettings):
    kafka: KafkaSettings = KafkaSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()

    development: bool
    pb_nalog_base_url: str
    pb_nalog_search_url: str
    
    proxy_urls: Optional[str] = None

    @property
    def proxy_url_list(self) -> list[str]:
        if not self.proxy_urls:
            return []
        return [url.strip() for url in self.proxy_urls.split(",")]

@lru_cache
def get_settings():
    return Settings()