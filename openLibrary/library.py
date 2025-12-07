import httpx
from typing import Optional
from urllib.parse import urlencode 
from pydantic_extra_types.isbn import ISBN

from openLibrary.models.id import (
    OLID
)
from models.authors import Author
from models.book import Book, BookEdition
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

MODEL_KEYS = {
    Author: 'author_key',
    Book: 'key',
    BookEdition: ''
}


class OpenLibrary(OLBase):
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

    def _search(self, q: OLSearch) -> dict:
        if not q:
            raise OLClientError("no query given")
        
        path = f'{_SEARCH}.json'

        params = q.model_dump(mode="json", exclude_unset=True)

        return self._get(path=path, params=params).json()
    

    def search(self, q: OLSearch, resource_types: list):
        resp = self._search(q)

        docs = resp.get('docs', [])

        results = []
        for d in docs:
            resource = []
            for r in resource_types:
                resource.append(r.get(d.get(MODEL_KEYS[r])))
            
            results.append(resource)
            
        else:
             self.logger.debug(f"no results found for query: {q.model_dump(mode="json", exclude_unset=True)}")

        return results

