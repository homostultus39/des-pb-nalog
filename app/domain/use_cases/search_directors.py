from typing import List
from domain.entities import PersonOrgPair
from domain.contracts.pb_nalog.pb_nalog_client import PbNalogClientContract
from domain.use_cases.exceptions import CaptchaRequiredError

class SearchDirectorsUseCase:
    def __init__(self, client: PbNalogClientContract):
        self._client = client

    async def execute(self, search_string: str) -> List[PersonOrgPair]:
        persons = await self._client.search_persons(search_string=search_string)
        pairs = []
        for person in persons:
            organizations = await self._client.get_organizations(
                name = person.name,
                token = person.token
            )

            for organization in organizations:
                pairs.append(PersonOrgPair(person=person, organization=organization))

        return pairs