from pydantic import BaseModel, field_validator, computed_field
from datetime import datetime
from typing import Self, Tuple

from openLibrary.models.id import (
    OLID
)
from openLibrary.models.search import (
    OLSearch
)
from openLibrary.models.data import (
    Links
)
from openLibrary.common.base import OLBase
from openLibrary.common.exceptions import OLClientError
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
    links: list[dict] | None
    type: str = 'author'
    key: OLID
    bio: str
    death_date: str | None = None
    latest_revision: int
    revision: int
    created: datetime
    last_modified: datetime

    @classmethod
    def unpack(cls, author: dict) -> Self:
        return cls(
            photos=author.get('photos'),
            alternate_names=author.get('alternate_names'),
            personal_name=author.get('personal_name'),
            remote_ids=author.get('remote_ids'),
            key=cls.clean_slash(author.get('key')),
            name=author.get('name'),
            birth_date=author.get('birth_date'),
            links=[l.get('url') for l in author.get('links', [])] or None,
            bio=author.get('bio', {}).get('value'),
            death_date=author.get('death_date'),
            latest_revision=author.get('latest_revision'),
            revision=author.get('revision'),
            created=author.get('created', {}).get('value'),
            last_modified=author.get('last_modified', {}).get('value')
        )

    @classmethod
    def getAuthor(cls, author: OLID):
        '''
        get an author by their id
        '''
        if not author.is_author():
            raise OLClientError("no author")
        
        path = f'{_AUTHORS}/{author.olid}.json'

        return cls.unpack(cls._get(path=path).json())
    
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

        resp = cls._get(path=path, params=params).json()
        count = resp['numFound']

        auth = []
        for d in resp.get('docs', []):
            auth.extend([cls.getAuthor(a) for a in d.get('author_key', [])])

        else:
            logger.debug(f"no results found for query: {params}")

        return count, [cls.unpack(a) for a in auth]
    

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

        resp =  cls._get(path=path, params=params).json()
        count = resp['size']


        return count, [a for a in resp['docs']]

