import httpx
from typing import Optional
from urllib.parse import urlencode 
from pydantic_extra_types.isbn import ISBN

from openLibrary.models.id import (
    OLID
)
from models.authors import Author
from openLibrary.models.search import OLSearch
from openLibrary.common.exceptions import OLClientError
from openLibrary.common.base import OLBase
from openLibrary.constants import (
    _ISBN,
    _AUTHORS,
    _COVERS,
    _LCCN,
    _OLID,
    _SEARCH,
    _WORKS,
    TIMEOUT_CONFIG
)


class openLibrary(OLBase):
    """
    Open Library Client

    Python Web Client for Open Library (openlibrary.org) built with httpx and pydantic

    Data Validation with pydantic requires most models must have at least 1 values
    some models accept multiple types of fields but only one value

    This object strives to get data in 2 ways:
        search functions: 
            allow you to get a resource type by searching for various attributes supported by open library
            naming conventions -> search_{resource_type}
        
        get functions:
            retrieve a resource by some unique ID, ID types differ for each resource but most will have a OLID (open library ID)
            naming conventions -> get_{resource_type}


    """

    def __init__(self, timeout: Optional[httpx.Timeout] = httpx.Timeout(10.0, connect=4.0, read=6.0)):
        
        self.TIMEOUT_CONFIG = timeout if timeout else TIMEOUT_CONFIG

        # TODO: implement account/ login here

        super.__init__(self.TIMEOUT_CONFIG)
    
        
    def work():
        None

    def edition():
        None
    
    def cover():
        None
    
    def search_author(self, q: OLSearch) -> tuple[int, list[Author]]:

        '''
        search for an author using OLSearch

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

        resp: dict = self._get(path=path, params=params).json()
        count = resp['numFound']

        auth = []
        for d in resp.get('docs', []):
            auth.extend([self.get_author(a) for a in d.get('author_key', [])])

        else:
            self.logger.debug(f"no results found for query: {params}")

        return count, auth
    
    def get_author(self, author: OLID):
        '''
        get an author by their id
        '''
        if not author.is_author():
            raise OLClientError("no author ID given")
        
        path = f'{_AUTHORS}/{author.olid}.json'

        return Author.unpack(self._get(path=path).json())

    def rating():
        None



