from typing import List
from domain.entities import DomainPerson, DomainOrganization
from domain.contracts.pb_nalog.pb_nalog_client import PbNalogClientContract

# Для тест кейсов буду использовать класс с псевдо клиентом, для тестирования без сети
class FakePbNalogClient(PbNalogClientContract):
    def __init__(self):
        self.persons_by_query: dict[str, List[DomainPerson]] = {}
        self.orgs_by_token: dict[str, List[DomainOrganization]] = {}
        self.raise_on_token: dict[str, Exception] = {}
        self.search_delay: float = 0.0
        self.org_delay: float = 0.0

    async def search_persons(self, search_string: str) -> List[DomainPerson]:
        if self.search_delay:
            import asyncio
            await asyncio.sleep(self.search_delay)
        return self.persons_by_query.get(search_string, [])

    async def get_organizations(self, name: str, token: str) -> List[DomainOrganization]:
        if token in self.raise_on_token:
            raise self.raise_on_token[token]
        if self.org_delay:
            import asyncio
            await asyncio.sleep(self.org_delay)
        return self.orgs_by_token.get(token, [])

def make_person(name: str = "Иванов", inn: str = "123456789000", token: str = "test_token", ul_count: str = "1", kind: str = "upr") -> DomainPerson:
    return DomainPerson(name=name, inn=inn, ul_count=ul_count, kind=kind, token=token)

def make_organization(
        name: str = "ООО ФИНАНС БАДДИ",
        inn: str = "1234567890000",
        ogrn: str = "1234567890",
        dtogrn: str = "01.01.2020",
        okved2: str = "92.2",
        okve2name: str = "Тест",
        status: str = "Действующая организация",
        region: str = "Санкт-Петербург"
        ):
    return DomainOrganization(
        name=name,
        inn=inn,
        ogrn=ogrn,
        dtogrn=dtogrn,
        okved2=okved2,
        okved2name=okve2name,
        status=status,
        region=region
    )
