from fastapi import APIRouter

from adapters.api.dependencies import UseCase
from adapters.api.schemas import (
    RequestScheme,
    ResponseScheme,
    SearchDirectorsResposeScheme,
)
from config.settings import get_settings

settings = get_settings()
router = APIRouter()


@router.post("/search", response_model=SearchDirectorsResposeScheme)
async def search_directors(use_case: UseCase, search_string: str):
    """
    Найти директора и связанные с ним компании
    """
    result = await use_case.execute(search_string=search_string)

    return SearchDirectorsResposeScheme(
        request=RequestScheme(search_string=search_string),
        response=ResponseScheme(
            success=result.success,
            error=result.error,
            duration=result.duration,
            collect_time=result.collect_time,
            total=result.total,
            entities=result.entities
        )
    )