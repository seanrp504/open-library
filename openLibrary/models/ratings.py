from httpx import Response
from pydantic import BaseModel
from typing import Self
import logging

from openLibrary.models.id import (
    OLID
)
from openLibrary.common.exceptions import OLClientError
from openLibrary.common.base import OLBase
from openLibrary.constants import (
    _WORKS,
    DEFAULT_LEVEL,
    CONSOLE_HANDLER,
    FILE_HANDLER
)

logger = logging.getLogger(__name__)
logger.setLevel(DEFAULT_LEVEL)
logger.addHandler(CONSOLE_HANDLER)
logger.addHandler(FILE_HANDLER) if FILE_HANDLER else None

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

        