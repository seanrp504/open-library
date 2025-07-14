from httpx import Response
from pydantic import BaseModel, field_validator
from typing import Self, Any
from datetime import datetime, date

from openLibrary.models.id import (
    OLID
)
from openLibrary.common.exceptions import OLClientError
from openLibrary.common.client import OLBase
from openLibrary.constants import (
    _WORKS
)


class Editions(BaseModel, OLBase):
    type: str | None = None
    authors: OLID
    idenifiers: dict[str, Any]
    local_id: str
    publish_date: date
    publisers: list[str]
    source_records: list[str]
    title: str
    full_title: str
    works: list[OLID]
    key: OLID
    covers: list[int]
    ocaid: str
    languages: list[str]
    number_of_pages: int
    latest_revision: int
    revision: int
    created: datetime
    last_modified: datetime

    @field_validator('local_id', 'publishers', mode="before")
    @classmethod
    def list_unpack(cls, val: list):
        return val[0]
    
    @field_validator('created', 'last_modified', mode="before")
    @classmethod
    def dict_unpack(cls, val: dict):
        return val['value']
    
    @field_validator('authors', 'works', 'languages', mode="before")
    @classmethod
    def nested_unpack(cls, val: list):
        return [cls.clean_slash(cls.key_unpack(v)) for v in val]
    
    @field_validator('type', mode="before")
    @classmethod
    def key_unpack(cls, val: dict):
        return cls.clean_slash(val['key'])
    

    @classmethod
    def get_editions(cls, olid: OLID, offset = 0, limit = 50) -> list[Self]:

        path = f"{_WORKS}/{olid.olid}/editions.json"
        resp = cls._get(path=path, params={"offset": offset, "limit": limit}).json()

        return [cls(**e) for e in resp['entries']]


