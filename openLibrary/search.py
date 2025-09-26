import httpx
from typing import Optional
from urllib.parse import urlencode 
from pydantic_extra_types.isbn import ISBN

from openLibrary.models.id import (
    coverSize,
    LCCN, 
    OLID
)
from openLibrary.models.search import OLSearch
from openLibrary.common.exceptions import OLClientError

from openLibrary.constants import (
    _ISBN,
    _AUTHORS,
    _COVERS,
    _LCCN,
    _OLID,
    _SEARCH,
    _WORKS
)


class openLibrary:
    """
    Open Library Client

    Python Web Client for Open Library (openlibrary.org) built with httpx and pydantic

    Data Validation with pydantic requires most models must have at least 1 values
    some models accept multiple types of fields but only one value
    """

    def __init__(self, timeout: Optional[httpx.Timeout] = httpx.Timeout(10.0, connect=4.0, read=6.0)):
        if timeout:
            self.TIMEOUT_CONFIG = timeout

        self.client = httpx.Client(timeout=self.TIMEOUT_CONFIG, follow_redirects=True)

    
        



