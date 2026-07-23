from typing import Annotated
from fastapi import Depends, Request

from config.settings import get_settings
from domain.use_cases.search_directors import SearchDirectorsUseCase


settings = get_settings()

async def get_use_case(request: Request) -> SearchDirectorsUseCase:
    client = request.app.state.http_client
    return SearchDirectorsUseCase(client=client)

UseCase = Annotated[SearchDirectorsUseCase, Depends(get_use_case)]