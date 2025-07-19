from pydantic import (
    BaseModel,
    model_validator,
    field_validator,
    computed_field,
    PastDate,
    FutureDate
)
from enum import Enum
from pydantic_extra_types.language_code import LanguageAlpha2
from pydantic_extra_types.isbn import ISBN
from typing import Optional, List
from openLibrary.common.exceptions import OLValidationError
from openLibrary.constants import OL_SORT
from collections.abc import Iterable
import re



DEWEY_SEARCH_PATTERN = re.compile(r'^\d{1,3}\*?$')

class Sort(Enum):
    editions = "editions"
    old = "old"
    new = "new"
    rating = "rating"
    rating_asc = "rating asc"
    rating_desc = "rating desc"
    # readinglog = "readinglog"
    # want_to_read = "want_to_read"
    title = "title"
    scans = "scans"

    lcc_sort = "lcc_sort"
    lcc_sort_asc = "lcc_sort asc"
    lcc_sort_desc = "lcc_sort desc"
    ddc_sort = "ddc_sort"
    ddc_sort_asc = "ddc_sort asc"
    ddc_sort_desc = "ddc_sort desc"
    ebook_access = "ebook_access"
    ebook_access_asc = "ebook_access asc"
    ebook_access_desc = "ebook_access desc"
    key = "key"
    key_asc = "key asc"
    key_desc = "key desc"
    random = "random"
    random_asc = "random asc"
    random_desc = "random desc"
    random_hourly = "random.hourly"
    random_daily = "random.daily"


class SupportsRange(BaseModel):
    start: str | PastDate
    end: str | FutureDate = None

    @computed_field
    @property
    def from_start(self):
        return f"[{self.start} TO *]"
    
    @computed_field
    @property
    def from_end(self):
        return f"[* TO {self.end}]"
    
    @computed_field
    @property
    def from_start_to_end(self):
        return f"[{self.start} TO {self.end}]"

class DDC(BaseModel):
    dewey: str | SupportsRange

    @field_validator('dewey')
    @classmethod
    def is_dewey(cls, d):
        if not re.fullmatch(DEWEY_SEARCH_PATTERN, d):
            raise OLValidationError("Not a valid Dewey Search")
        return d
    

class LCC(BaseModel):
    None

class Solr(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    authors: list[str] | None = None
    subject: list[str] | None = None
    place: list[str] | None = None
    person: list[str] | None = None
    publisher: list[str] | None = None
    first_publish_year: SupportsRange | None = None
    ddc: DDC | None = None
    isbn: ISBN | None = None
    lcc: str | None = None

    @model_validator(mode="after")
    def validate_min_one(self):
        if not any(f for f, _ in self.model_dump(exclude_unset=True)):
            raise ValueError('At least one value must be present to create a Query object')
        return self
    
    @computed_field
    @property
    def time_range(self):
        key = "first_publish_year"
        r = {}

        if self.first_publish_year.start and self.first_publish_year.end:
            r.update({key: f"[{self.first_publish_year.start} TO {self.first_publish_year.end}]"})
        
        elif self.first_publish_year.start:
            r.update({key: f"[{self.first_publish_year.start} TO *]"})
    
        elif self.first_publish_year.end:
            r.update({key: f"[* TO {self.first_publish_year.end}]"})
        
        return r

    @computed_field
    @property
    def solr(self) -> str:
        ''' conver the model to a solr query'''
        query = []

        fields = self.model_dump(exclude_unset=True)

        for f, v in fields:
            

            if f.startswith("publish_"):
                pass

            elif isinstance(v, Iterable):
                field_values = []
                for i in v:
                    field_values.append(f'{f}:"{i}"')
                
                ored = " OR ".join(field_values)
                query.append(f"({ored})")

            else:
                query.append(f'{f}:"{v}"')
        
        query.append(self.time_range) if self.time_range else None
        
        return " AND ".join(query)




class OLSearch(BaseModel):
    """ Model for an Open Library search """
    q: Solr
    fields: List = []
    sort: str = Sort.title
    lang: LanguageAlpha2 = 'en'

    @field_validator('sort', mode="before")
    @classmethod
    def val_sort(cls, sort: str):
        if sort:
            if sort not in OL_SORT:
                raise OLValidationError("Unkown sort value provided")
        return sort
    
    @model_validator(mode="after")
    def validate_search(self):
        if not self.q:
            raise OLValidationError("There must be a search query")
        
        return self
    
    @model_validator("q", mode="before")
    @classmethod
    def q_to_solr(cls, q: Solr):
        return q.solr

