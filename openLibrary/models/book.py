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
from openLibrary.models.ratings import Ratings
from openLibrary.models.editions import Editions
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
    first_publish_date: date
    subject_people: list[str]
    location: OLID
    key: OLID
    authors: list[AuthorDict]
    subject_times: list[str]
    type: Key
    subjects: list[str]
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
    physical_format: str | None = None
    lc_classification: list[str] | None = None
    key: OLID | None = None
    authors: list[str] | None = None # TODO make this class backfill this with authors model
    ocaid: str | None =  None
    publish_places: list[str] | None = None
    languages: str | None = None
    source_records: list[str] | None = None
    title: str | None = None
    notes: str | None = None
    identifiers: dict[str, Any] | None = None
    isbn_13: ISBN | None = None
    edition_name: str | None = None
    subjects: list[str] | None = None
    publish_date: str | None = None
    copyright_date: str | None = None
    works: list[str] | None = None
    type: str = 'edition'
    physical_dimensions: str | None = None
    latest_revision: int | None = None
    revision: int | None = None
    created: datetime | None = None
    last_modified: datetime | None = None


    @classmethod
    def get(cls, id: OLID | ISBN) -> Self | None:
        '''
        search for a book by its isbn or olid
        '''
        match id:
            case OLID():
                book = cls._getBookByOLID(id)
            case ISBN():
                book = cls._getBookByISBN(id).json()
                key = cls.clean_slash(book.get('key'))
                try:
                    book = cls._getBookByOLID(OLID(olid=key))
                except Exception:
                    logger.info(f"failed to validate or fetch book by key {key}, continuing with naive object", exc_info=True)
            case _:
                book = None
        
        if isinstance(book, Response):
            book: dict = book.json()
            return cls.unpack(book)
          
        return None
    
    @classmethod
    def unpack(cls, book: dict):

        return cls(
                publishers=book.get('publishers'),
                number_of_pages=book.get('number_of_pages'),
                description=book.get('description', {}).get('value'),
                weight=book.get('weight'),
                isbn_10=next(iter(book.get('isbn_10', [])), None),
                covers=book.get('covers', []),
                physical_format=book.get('physical_format'),
                lc_classification=book.get('lc_classifications'),
                key=OLID(olid=cls.clean_slash(book.get('key'))),
                authors=[cls.clean_slash(a.get('key')) for a in book.get('authors', [])] or None,
                publish_places=book.get('publish_places'),
                languages=[cls.clean_slash(l.get('key'))  for l in book.get('languages', [])] or None,
                source_records=book.get('source_records'),
                title=book.get('title'),
                notes=book.get('notes', {}).get('value'),
                identifiers=book.get('identifiers'),
                isbn_13=next(iter(book.get('isbn_13', [])), None),
                edition_name=book.get('edition_name'),
                subject=book.get('subjects'),
                subject_places=book.get('subject_places'),
                subject_people=book.get('subject_people'),
                publish_date=book.get('publish_date'),
                copyright_date=book.get('copyright_date'),
                works=[cls.clean_slash(w.get('key')) for w in book.get('works', [])] or None,
                physical_dimensions=book.get('physical_dimensions'),
                latest_revision=book.get('latest_revision'),
                created=book.get('created', {}).get('value'),
                last_modified=book.get('last_modified', {}).get('value')
            )


    @classmethod
    def _getBookByISBN(cls, isbn: ISBN) -> Response:

        if not isbn:
            raise OLClientError("no isbn")
        
        path = f'{_ISBN}/{isbn}.json'
            
        return cls._get(path=path)
    
    @classmethod
    def _getBookByOLID(cls, olid: OLID) -> Response:
        
        if not olid.is_edition():
            raise OLClientError("wrong olid type, should end in M")
        
        path = f'{_BOOKS}/{olid.olid}.json'

        return cls._get(path=path)
    
    
    def get_cover(self,  size: str = coverSize.large) -> bytes | None:
        '''
        gets the cover for the current book, as bytes
        
        Args:
            size (coverSize): ( S, M or L )
        
        Returns:
            bytes:
        '''

        if not self.covers:
            return None

        path = f'b/id/{self.covers[0]}-{size}.jpg'
        
        return bytes(self._get(path=path).content)

