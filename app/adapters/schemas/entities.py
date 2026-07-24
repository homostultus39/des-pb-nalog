from pydantic import BaseModel, Field


class Person(BaseModel):
    name: str
    inn: str
    ul_count: str = Field(validation_alias="ul_cnt")
    kind: str
    token: str

class Organization(BaseModel):
    name: str = Field(validation_alias="namep")
    inn: str
    ogrn: str
    dtogrn: str
    okved2: str = Field(validation_alias="okved2main")
    okved2name: str = Field(validation_alias="okved2mainname")
    status: str = Field(validation_alias="sulst_name_ex")
    region: str = Field(validation_alias="regionname")