from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parents[2]

class KafkaSettings(BaseSettings):
    pass

class RabbitMQSettings(BaseSettings):
    pass

class Settings(BaseSettings):
    kafka: KafkaSettings = KafkaSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()

    development: bool
    pb_nalog_base_url: str
    pb_nalog_search_url: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "infra" / ".prod.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings():
    return Settings()