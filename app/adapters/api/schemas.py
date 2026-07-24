from datetime import datetime

from pydantic import BaseModel, ConfigDict

from domain.entities import DomainPersonOrgPair


class RequestScheme(BaseModel):
    search_string: str

class ResponseScheme(BaseModel):
    success: bool
    error: str | None
    duration: float
    collect_time: datetime
    total: int
    entities: list[DomainPersonOrgPair]

    model_config = ConfigDict(
        from_attributes=True
    )

class SearchDirectorsResposeScheme(BaseModel):
    request: RequestScheme
    response: ResponseScheme

