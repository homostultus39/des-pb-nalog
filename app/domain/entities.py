from dataclasses import dataclass


@dataclass
class DomainPerson:
    name: str
    inn: str
    ul_count: str
    kind: str
    token: str

@dataclass
class DomainOrganization:
    name: str
    inn: str
    ogrn: str
    dtogrn: str
    okved2: str
    okved2name: str
    status: str
    region: str

@dataclass
class DomainPersonOrgPair:
    person: DomainPerson
    organization: DomainOrganization