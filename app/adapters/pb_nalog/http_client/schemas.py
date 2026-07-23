from pydantic import BaseModel


class SearchPersonsRequestPayload(BaseModel):
    mode: str = "search-upr-uchr"
    queryUpr: str
    uprType1: str = "1"
    page: str = "1"
    pageSize: str = "100"

class GetOrganizationsRequestPayload(BaseModel):
    mode: str = "search-ul"
    queryUl: str
    token: str
    page: str = "1"
    pageSize: str = "100"