import httpx
from pydantic import BaseModel, model_validator, field_validator
from pydantic_extra_types.isbn import ISBN
from typing import Optional
import re

olwid_pattern = re.compile(r'^OL\d+[MW]$')
oleid_pattern = re.compile(r'')

class bookID(BaseModel):
    isbn10: Optional[ISBN]
    isbn13: Optional[ISBN]
    olid: Optional[str]
    lccn: Optional[str]

    @field_validator("olid")
    @classmethod
    def validate_olwid(cls, olid: str) -> str:
        clean = re.sub(r'[\s-]', "", olid)
        if not re.fullmatch(olwid_pattern, clean):
            raise ValueError('Invalid OLID')
        return olid


    @model_validator(mode="after")
    @classmethod
    def validate_min_one(cls, values):
        if not any(values.values()):
            raise ValueError('At least one value must be present to create a bookID object')
        return values

class bookISBN(BaseModel):
    isbn: ISBN

    @model_validator(mode="before")
    @classmethod
    def validate(cls, values):
        if values.isbn == 10:
            values.isbn = ISBN.convert_isbn10_to_isbn13(values.isbn)
        return values
    
class bookOLID(BaseModel):
    olid: str

    @model_validator(mode="before")
    @classmethod
    def validate(cls, value):
        clean = re.sub(r'[\s-]', "", value.olid)
        if not re.fullmatch(olwid_pattern, clean):
            raise ValueError('Invalid OLID')
        return clean


class coverSize(BaseModel):
    """ 
    size options [S, M, L]
    """
    size: str

    @field_validator("size")
    @classmethod
    def validate_size(cls, size):
        if size != 'L' or size != 'M' or size != 'S':
            raise ValueError("Unkown Size")
        return size
    


class OLError(Exception):
    """ Generic OL Client Error"""
    pass
        



class openLibrary:
    """
    Open Library Client

    Python Web Client for Open Library (openlibrary.org) built with httpx and pydantic

    Data Validation with pydantic requires most models must have at least 1 values
    some models accept multiple types of fields but only one value
    """

    base_url = 'openlibrary.org'
    isbn = 'isbn'
    olid = 'olid'
    lccn = 'lccn'
    works = 'works'
    covers = 'covers'

    TIMEOUT_CONFIG = httpx.Timeout(10.0, connect=4.0, read=6.0)

    def __init__(self, timeout: Optional[httpx.Timeout] = None):
        if timeout:
            self.TIMEOUT_CONFIG = timeout

        self.client = httpx.Client(timeout=self.TIMEOUT_CONFIG, follow_redirects=True)
    

    def getBookByISBN(self, book: bookISBN = None):
        resp = None
        url = f'https://{self.base_url}/{self.isbn}'
        
        if book:
            url = f"{url}/{book.isbn}.json"
            

        if not url.endswith('.json'):
            raise OLError("Unable to build open lirbary url")

        resp = self.client.get(url)
        resp.raise_for_status() 
        return resp
    

        
    def getCoverByISBN(self, book: bookISBN, size: coverSize):
        resp = None
        url = f'https://{self.covers}.{self.base_url}/'

        if book and size:
            url = f"{url}/{self.isbn}/{book.isbn}-{size.size}.jpg"

        if not url.endswith('.jpg'):
            raise OLError("Unable to build open library url")
        
        resp = self.client.get(url)
        resp.raise_for_status()
        return resp
    
    
        



