from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parents[2]

class KafkaSettings(BaseSettings):
    kafka_response_topic: str

class RabbitMQSettings(BaseSettings):
    rabbitmq_task_queue: str
    rabbitmq_status_queue: str

class Settings(BaseSettings):
    kafka: KafkaSettings = KafkaSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()

    development: bool
    pb_nalog_base_url: str
    pb_nalog_search_url: str
    proxy_url: str | None
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "infra" / ".prod.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings():
    return Settings()