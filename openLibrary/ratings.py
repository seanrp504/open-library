from httpx import Response
from pydantic import BaseModel
from typing import Self

from openLibrary.models.id import (
    OLID
)
from openLibrary.common.exceptions import OLClientError
from openLibrary.common.base import OLBase
from openLibrary.constants import (
    _WORKS
)

class Ratings(BaseModel, OLBase):
    average: float
    count: int
    sortable: float
    star_counts: dict[str, int] 

    @classmethod
    def get(cls, olid: OLID) -> Self:
        if not olid.is_work():
           OLClientError("OLID provided is not a work id")

        path = f"/{_WORKS}/{olid.olid}/ratings.json"
        resp: Response = cls.__get(path=path)

        body = resp.json()

        summary = body['summary']

        return cls(star_counts=body['counts'], **summary)

        