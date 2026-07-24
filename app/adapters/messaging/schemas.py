from datetime import datetime

from pydantic import BaseModel, ConfigDict

from domain.entities import DomainOrganization, DomainPerson


class RequestDTO(BaseModel):
    search_string: str

class StatusResponseDTO(BaseModel):
    success: bool
    error: str | None
    duration: float
    collect_time: datetime
    total: int

class RabbitMQStatusMessage(BaseModel):
    request: RequestDTO
    response: StatusResponseDTO

class KafkaResponseDTO(BaseModel):
    success: bool
    error: str | None
    duration: float
    total: int
    collect_time: datetime
    person: DomainPerson
    organization: DomainOrganization

    model_config = ConfigDict(
        from_attributes=True
    )

class KafkaResponseMessage(BaseModel):
    request: RequestDTO
    response: KafkaResponseDTO