from pydantic import BaseModel, field_validator, computed_field
from datetime import datetime
from typing import Self, Tuple

from openLibrary.models.id import (
    OLID
)
from openLibrary.models.search import (
    OLSearch
)
from openLibrary.common.base import OLBase
from openLibrary.common.exceptions import OLClientError
from openLibrary.book import Book
from openLibrary.constants import (
    _ISBN,
    _AUTHORS,
    _SEARCH,
    _WORKS,
    DEFAULT_LEVEL,
    CONSOLE_HANDLER,
    FILE_HANDLER
)

import logging

logger = logging.getLogger(__name__)
logger
logger.setLevel(DEFAULT_LEVEL)
logger.addHandler(CONSOLE_HANDLER)
logger.addHandler(FILE_HANDLER) if FILE_HANDLER else None


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
        get an author by their id
        '''
        if not author.is_author():
            raise OLClientError("no author")
        
        path = f'{_AUTHORS}/{author.olid}.json'

        return cls(**cls.__get(path=path).json())
    
    @classmethod
    def search(cls, q: OLSearch) -> tuple[int, list[Self]]:

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
            raise OLClientError("no query")
        
        path = f'{_SEARCH}.json'

        params = q.model_dump(mode="json", exclude_unset=True)

        resp = cls.__get(path=path, params=params).json()
        count = resp['numFound']

        auth = []
        for d in resp.get('docs', []):
            auth.extend([cls.getAuthor(a) for a in d.get('author_key', [])])

        else:
            logger.debug(f"no results found for query: {params}")

        return count, [cls(**a) for a in auth]
    

    @classmethod
    def getWorksByAuthor(cls, author: OLID, limit: int = 100, offset: int = 0):

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

