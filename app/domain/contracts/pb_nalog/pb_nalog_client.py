from typing import List
from abc import abstractmethod, ABC
from domain.entities import Person, Organization


class PbNalogClientContract(ABC):
    @abstractmethod
    async def search_persons(self, search_string: str) -> List[Person]:
        pass

    @abstractmethod
    async def get_organizations(self, name, token) -> List[Organization]:
        pass