import asyncio
from typing import List
from time import monotonic
from datetime import datetime, timezone
from domain.entities import DomainPersonOrgPair, DomainPerson
from domain.contracts.pb_nalog.pb_nalog_client import PbNalogClientContract
from domain.use_cases.models import SearchResult

from config.logger import configure_logger

logger = configure_logger("USECASE")

class SearchDirectorsUseCase:
    def __init__(self, client: PbNalogClientContract):
        self._client = client

    async def execute(self, search_string: str) -> SearchResult:
        start_time = monotonic()
        entities: List[DomainPersonOrgPair] = []
        success, error = True, None
        
        if not search_string:
            success, error = False, "Search string is empty"
        else:
            try:
                entities = await asyncio.wait_for(
                    self._collect(search_string),
                    timeout=60,
                )
            except asyncio.TimeoutError:
                success, error = False, "timeout: exceeded 30s"
            except Exception as e:
                success, error = False, str(e)

        duration = monotonic() - start_time
        collect_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

        return SearchResult(
            success=success,
            error=error,
            duration=duration,
            collect_time=collect_time,
            entities=entities,
        )

    async def _collect(self, search_string: str) -> List[DomainPersonOrgPair]:
        persons = await self._client.search_persons(search_string=search_string)
        sem = asyncio.Semaphore(6)

        async def fetch(person: DomainPerson):
            async with sem:
                organizations = await self._client.get_organizations(
                    name=person.name, token=person.token
                )
                return [
                    DomainPersonOrgPair(person=person, organization=o)
                    for o in organizations
                ]

        results = await asyncio.gather(*(fetch(p) for p in persons), return_exceptions=True)
    
        pairs = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Ошибка при обработке человека: {result}")
                continue
            pairs.extend(result)
        
        return pairs