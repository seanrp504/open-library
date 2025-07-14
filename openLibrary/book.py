from httpx import Response
from pydantic import BaseModel, computed_field, field_validator
from pydantic_extra_types.isbn import ISBN
from datetime import datetime
from typing import Any, Self

from openLibrary.models.id import (
    OLID,
    coverSize
)
from openLibrary.ratings import Ratings
from openLibrary.editions import Editions
from openLibrary.common.exceptions import OLClientError
from openLibrary.common.client import OLBase
from openLibrary.constants import (
    _ISBN,
    _BOOKS
)


class Book(BaseModel, OLBase):
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
    ocaid: str | None = None
    publish_places: list[str] | None = None
    languages: str | None = None
    source_records: list[str] | None = None
    title: str | None = None
    notes: str | None = None
    identifiers: dict[str, Any] | None = None
    isbn_13: ISBN | None = None
    edition_name = str | None = None
    subjects: list[str] | None = None
    publish_date: str | None = None
    copyright_date: str | None = None
    works: list[str] | None = None
    physical_dimensions: str | None = None
    latest_revision: int | None = None
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
        return [cls.clean_slash(cls.key_unpack(v)) for v in val]
    
    @field_validator('type', mode="before") 
    @classmethod
    def key_unpack(cls, val: dict):
        return cls.clean_slash(val['key'])
    
    @field_validator('key', mode="before")
    @classmethod
    def clean_string(cls, val: str):
        return cls.clean_slash(val)

    @classmethod
    def search(cls, id: OLID | ISBN) -> Self | None:
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
            raise OLClientError("Unable to build open lirbary url -> no isbn")
        
        path = f'{_ISBN}/{isbn}.json'
            
        return cls._get(path=path)
    
    @classmethod
    def _getBookByOLID(cls, olid: OLID) -> Response:
        
        if not olid:
            raise OLClientError("Unable to build open lirbary url -> no olid")
        
        path = f'{_BOOKS}/{olid.olid}.json'

        return cls._get(path=path)
    
    
    def getCover(self,  size: coverSize = coverSize(size='L')) -> bytes:
        '''
        gets the cover for the current book, as bytes
        
        Args:
            size (coverSize): ( S, M or L )
        
        Returns:
            bytes:
        '''
        
        path = f'{_ISBN}/b/{self.isbn_10}-{size.size}.jpg'
        
        return bytes(self._get(path=path).content)
        

    @computed_field
    @property
    def ratings(self) -> list[Ratings]:
        '''
        ratings object for book
        '''
        return Ratings.get(self.works[0])

    @computed_field
    @property
    def editions(self) -> list[Editions]:
        '''
        list of editions of book
        '''
        return Editions.get_editions(self.works[0])
