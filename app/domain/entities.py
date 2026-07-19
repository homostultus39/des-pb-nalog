from pydantic import BaseModel

class Person(BaseModel):
    name: str
    inn: str
    token: str

class Organization(BaseModel):
    name: str
    inn: str
    ogrn: str
    status: str
    region: str

class PersonOrgPair(BaseModel):
    person: Person
    organization: Organization