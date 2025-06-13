import httpx
from pydantic import BaseModel, model_validator
from pydantic_extra_types.isbn import ISBN
from typing import Optional

class bookID(BaseModel):
    isbn10: ISBN
    isbn13: ISBN
    ol_work_id: Optional[str]

    @model_validator
    def validate(cls, values):
        if not any(values.values()):
            raise ValueError('At least one value must be present to create a bookID object')
        return values
    

class coverSize(BaseModel):
    small: Optional[bool]
    medium: Optional[bool]
    large: Optional[bool]

    @model_validator
    def validate(cls, model):
        if not any(model.values()):
            raise ValueError('At least one value must be present for a coverSize')
        
        if sum(model.values()) > 1:
            raise ValueError('Only 1 values can be set for a vocerSize')

        

TIMEOUT_CONFIG = httpx.Timeout(10.0, connect=4.0, read=6.0)

class openLibrary:
    base_url = 'https://openlibrary.org/'
    isbn = 'isbn'
    works = 'works'

    def __init__(self):
        self.client = httpx.Client(timeout=TIMEOUT_CONFIG, follow_redirects=True)
    

    def get_book(self, book: bookID, by_isbn: True, by_work_id: False):
        resp = None
        if by_isbn:

            url = f"{self.base_url}/{self.isbn}/{book.isbn13 if book.isbn13 else book.isbn10}.json"
            resp = self.client.get(url)

        elif by_work_id:
            url = f"{self.base_url}/{self.works}/{book.ol_work_id}.json"
            resp = self.client.get(url)

        
        resp.raise_for_status() if resp else None
        return resp
        
    def get_book_cover(self, book: bookID, size: coverSize):
        None


        
        


