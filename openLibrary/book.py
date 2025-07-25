from httpx import Response
from pydantic import BaseModel, computed_field, field_validator
from pydantic_extra_types.isbn import ISBN
from datetime import datetime, date
from typing import Any, Self
import logging

from openLibrary.models.id import (
    OLID,
    coverSize
)
from openLibrary.models.data import (
    Link,
    Key,
    Excerpt,
    AuthorDict
)
from openLibrary.models.search import OLSearch
from openLibrary.ratings import Ratings
from openLibrary.editions import Editions
from openLibrary.authors import Author
from openLibrary.common.exceptions import OLClientError
from openLibrary.common.base import OLBase
from openLibrary.constants import (
    _ISBN,
    _BOOKS,
    _SEARCH,
    _WORKS,
    DEFAULT_LEVEL,
    CONSOLE_HANDLER,
    FILE_HANDLER
)

logger = logging.getLogger(__name__)
logger.setLevel(DEFAULT_LEVEL)
logger.addHandler(CONSOLE_HANDLER)
logger.addHandler(FILE_HANDLER) if FILE_HANDLER else None


class Book(BaseModel, OLBase):
    '''
    this model represents works fetched from the open library

    this model conceptualizes the different forms that works data takes from the isbn api and the works api
    '''
    description: str 
    links: list[Link]
    title: str
    covers: list[int]
    first_sentence: str
    subject_places: list[str]
    excerpts: list[Excerpt]
    first_publist_date: date
    subject_people: list[str]
    location: OLID
    key: OLID
    authors: list[AuthorDict]
    subject_times: list[str]
    type: Key
    subjects: list[str]
    lc_classification: list[str]
    latest_revision: int
    revision: int
    created: datetime
    last_modified: datetime


    @field_validator('created', 'last_modified', 'first_sentence', mode="before")
    @classmethod
    def dict_unpack(cls, val: dict):
        return val['value']
    
    
    @field_validator('type', mode="before") 
    @classmethod
    def key_unpack(cls, val: dict):
        return cls.clean_slash(val['key'])
    
    @field_validator('key', 'location', mode="before")
    @classmethod
    def clean_string(cls, val: str):
        return cls.clean_slash(val)
    
    @classmethod
    def get(cls, olid: OLID):
        if not olid.is_work():
            raise OLClientError("Not a work id")
        
        path = f'{_WORKS}/{olid.olid}'

        resp = cls.__get(path=path).json()

        return cls(**resp)
    
    @classmethod
    def search(cls, q: OLSearch) -> tuple[int, list[Self]]:

        if not q:
            raise OLClientError("no search")
        
        params = q.model_dump(mode="json", exclude_unset=True)

        path = f'{_SEARCH}.json'

        resp = cls.__get(path=path, params=params).json()
        hits = resp['numFound']

        return hits,  [cls.get(olid=OLID(cls.clean_slash(r['key']))) for r in resp['docs']]
    

    def get_covers(self,  size: str = coverSize.large) -> list[bytes]:
        '''
        gets the covers for the current book, as bytes
        
        Args:
            size (coverSize): ( S, M or L )
        
        Returns:
            bytes:
        '''
        cov = []
        for c in self.covers:

    
            path = f'b/id/{c}-{size}.jpg'
            
            cov.append(bytes(self.__get(path=path).content))
        
        return cov

    @computed_field
    @property
    def editions(self) -> list[Editions]:
        '''
        list of editions of book
        '''
        eds = Editions.get_editions(self.key)

        return [BookEdition.get(OLID(self.clean_slash(e['key']))) for e in eds]
    
    @computed_field
    @property
    def ratings(self) -> Ratings:
        '''
        list of ratings for the book
        '''

        return Ratings.get(OLID(self.key))



class BookEdition(BaseModel, OLBase):
    '''
    this model represents an edition of a work
    this model contains more data about a specific version of a Work (Book Model). 
    '''
    publishers: list[str] | None = None
    number_of_pages: int | None = None
    description: str | None = None
    weight: str | None = None
    isbn_10: ISBN | None = None
    covers: list[int] | None = None # TODO backfill this with a covers class?
    pyshical_format: str | None = None
    lc_classification: list[str] | None = None
    key: OLID | None = None
    authors: list[str] | None = None # TODO make this class backfill this with authors model
    publish_places: list[str] | None = None
    languages: str | None = None
    source_records: list[str] | None = None
    title: str | None = None
    notes: str | None = None
    identifiers: dict[str, Any] | None = None
    isbn_13: ISBN | None = None
    edition_name = str | None = None
    subjects: list[str] | None = None
    subjects_places: list[str] | None = None
    subject_people: list[str] | None = None
    publish_date: str | None = None
    copyright_date: str | None = None
    works: list[str] | None = None
    physical_dimensions: str | None = None
    latest_revision: int | None = None
    revision: int | None = None
    created: datetime | None = None
    last_modified: datetime | None = None

    @field_validator('isbn_10','covers', 'lc_classifications',\
                     'isbn_13', mode="before")
    @classmethod
    def list_unpack(cls, val: list):
        return val[0]


    @field_validator('description', 'notes', 'created', 'last_modified', mode="before")
    @classmethod
    def dict_unpack(cls, val: dict):
        return val['value']
    
    
    @field_validator('authors', 'languages', 'works', mode="before")
    @classmethod
    def nested_unpack(cls, val: list):
        return [cls.clean_slash(cls.key_unpack(v['author'] if 'author' in v else v)) for v in val]
    
    @field_validator('type', mode="before") 
    @classmethod
    def key_unpack(cls, val: dict):
        return cls.clean_slash(val['key'])
    
    @field_validator('key', mode="before")
    @classmethod
    def clean_string(cls, val: str):
        return cls.clean_slash(val)

    @classmethod
    def get(cls, id: OLID | ISBN) -> Self | None:
        '''
        search for a book by its isbn or olid
        '''
        match id:
            case OLID():
                book = cls._getBookByOLID(id)
            case ISBN():
                book = cls._getBookByISBN(id)
            case _:
                book = None
        
        if book:
            return cls(**book.json())
        
        return None


    @classmethod
    def _getBookByISBN(cls, isbn: ISBN) -> Response:

        if not isbn:
            raise OLClientError("no isbn")
        
        path = f'{_ISBN}/{isbn}.json'
            
        return cls.__get(path=path)
    
    @classmethod
    def _getBookByOLID(cls, olid: OLID) -> Response:
        
        if not olid.is_edition():
            raise OLClientError("wrong olid type, should end in M")
        
        path = f'{_BOOKS}/{olid.olid}.json'

        return cls.__get(path=path)
    
    
    def get_cover(self,  size: str = coverSize.large) -> bytes:
        '''
        gets the cover for the current book, as bytes
        
        Args:
            size (coverSize): ( S, M or L )
        
        Returns:
            bytes:
        '''

        path = f'b/id/{self.covers[0]}-{size}.jpg'
        
        return bytes(self.__get(path=path).content)

