from pydantic import BaseModel, field_validator, computed_field
from datetime import datetime
from typing import Self, Tuple

from openLibrary.models.id import (
    OLID
)
from openLibrary.common.base import OLBase
from openLibrary.common.exceptions import OLClientError
from openLibrary.book import Book
from openLibrary.constants import (
    _ISBN,
    _AUTHORS,
    _COVERS,
    _LCCN,
    _OLID,
    _SEARCH,
    _WORKS
)



class Author(BaseModel, OLBase):
    photos: list[int]
    alternate_names: list[str]
    personal_name: str
    remote_ids: dict[str, str]
    source_records: list[str]
    name: str
    birth_date: str
    links: list[dict]
    type: str
    key: OLID
    bio: str
    death_date: str | None = None
    latest_revision: int
    revision: int
    created: datetime
    last_modified: datetime

    @field_validator('created', 'last_modified', 'bio', mode="before")
    @classmethod
    def dict_unpack(cls, val: dict):
        return val['value']

    @field_validator('type', 'key', mode="before")
    @classmethod
    def key_unpack(cls, val: dict):
        return cls.clean_slash(val['key'])

    @classmethod
    def getAuthor(cls, author: OLID):
        '''
        get info about an author
        '''
        if not author:
            raise OLClientError("no author")
        
        path = f'{_AUTHORS}/{author.olid}.json'

        return cls(**cls.__get(path=path).json())
    
    @classmethod
    def _searchAuthor(cls, q: str) -> Tuple[int, Self]:

        '''
        search for an author by name

        Args:
            q (str): a query string
        
        Raises:
            OLClientError:
        
        Returns:
            (int, list[authors]):


        '''

        if not q:
            raise OLClientError("no author")
        
        path = f'{_SEARCH}/authors.json'

        params = {
            'q': q
        }

        resp = cls.__get(path=path, params=params).json()
        count = resp['numFound']


        return count, [cls(**a) for a in resp['docs']]
    

    @classmethod
    def _getWorksByAuthor(cls, author: OLID, limit: int = 100, offset: int = 0):

        '''
        get works by an other, by searching their open library id

        Returns:
            (int, list[authors]):
        '''
        
        if not author:
            raise OLClientError("no author")
        
        path = f'{_AUTHORS}/{author.olid}/{_WORKS}.json'

        params = {
            'limit': limit,
            'offset': offset
        }

        resp =  cls.__get(path=path, params=params).json()
        count = resp['size']


        return count, [Book(**a) for a in resp['docs']]

