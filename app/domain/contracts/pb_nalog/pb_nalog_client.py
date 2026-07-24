from abc import ABC, abstractmethod

from domain.entities import DomainOrganization, DomainPerson


class PbNalogClientContract(ABC):
    @abstractmethod
    async def search_persons(self, search_string: str) -> list[DomainPerson]:
        pass

    @abstractmethod
    async def get_organizations(self, name, token) -> list[DomainOrganization]:
        pass