import httpx
from openLibrary.models.books import (
    ISBN13, 
    coverSize,
    LCCN, 
    OLID
    )
from openLibrary.models.search import OLSearch
from openLibrary.common.exceptions import OLClientError
from typing import Optional
from urllib.parse import urlencode



class openLibrary:
    """
    Open Library Client

    Python Web Client for Open Library (openlibrary.org) built with httpx and pydantic

    Data Validation with pydantic requires most models must have at least 1 values
    some models accept multiple types of fields but only one value
    """

    BASE_DOMAIN = 'openlibrary.org'
    _ISBN = 'isbn'
    _OLID = 'olid'
    _LCCN = 'lccn'
    _WORKS = 'works'
    _COVERS = 'covers'
    _AUTHORS = 'authors'
    _SEARCH = 'search.json'

    TIMEOUT_CONFIG = httpx.Timeout(10.0, connect=4.0, read=6.0)

    def __init__(self, timeout: Optional[httpx.Timeout] = None):
        if timeout:
            self.TIMEOUT_CONFIG = timeout

        self.client = httpx.Client(timeout=self.TIMEOUT_CONFIG, follow_redirects=True)

    def _get(self, path, subdomain: str =  None, params: dict = {}) -> httpx.Response:

        url = f"https://{subdomain + '.' if subdomain is not None else ''}{self.BASE_DOMAIN}/{path}"

        resp = self.client.get(urlencode(url), params=params)
        resp.raise_for_status()
        return resp
    

    def getBookByISBN(self, isbn: ISBN13) -> httpx.Response:

        if not isbn:
            raise OLClientError("Unable to build open lirbary url -> no isbn")
        
        path = f'{self._ISBN}/{isbn.isbn}.json'
            
        return self._get(path=path)
    
    def getBookByOLID(self, olid: OLID, editions: bool = False) -> httpx.Response:
        
        if not olid:
            raise OLClientError("Unable to build open lirbary url -> no olid")
        
        path = f'{self._WORKS}/{olid.olid}{'/editions' if editions else ''}.json'

        return self._get(path=path)
    
    def getCoverByISBN(self, book: ISBN13, size: coverSize = coverSize(size='L')) -> httpx.Response:

        if not book:
            raise OLClientError("Unable to build open library url -> no isbn")
        
        path = f'{self._ISBN}/b/{book.isbn}-{size.size}.jpg'
        
        return self._get(path=path)
    
    def getAuthor(self, author: OLID):
        
        if not author:
            raise OLClientError("Unable to build open library url -> no author")
        
        path = f'{self._AUTHORS}/{author.olid}.json'

        return self._get(path=path)
    
    def searchAuthor(self, q: str):

        if not q:
            raise OLClientError("Unable to build open library url -> no author")
        
        path = f'{self._SEARCH}/authors.json'

        params = {
            'q': q
        }

        return self._get(path=path, params=params)
    
    
    def getWorksByAuthor(self, author: OLID, limit: int = 100, offset: int = 0):
        
        if not author:
            raise OLClientError("Unable to build open library url -> no author")
        
        path = f'{self._AUTHORS}/{author.olid}/{self._WORKS}.json'

        params = {
            'limit': limit,
            'offset': offset
        }

        return self._get(path=path, params=params)
    
    def search(self, query: OLSearch):
        path = f'/{self._SEARCH}'
        params = {}

        if query.q:
            params.update({'q': query.q.to_solr()})
        
        if query.lang:
            params.update({'lang': query.lang})
        
        if query.sort:
            params.update({'sort': query.sort})
        
        if query.fields:
            params.update({'fields': query.fields})

        return self._get(path=path, params=params)

    
    
        



