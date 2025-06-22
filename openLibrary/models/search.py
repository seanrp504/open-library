from pydantic import (
    BaseModel,
    model_validator,
    field_validator,
    computed_field,
    PastDate,
    FutureDate
)
from openLibrary.models.books import ISBN13
from pydantic_extra_types.language_code import LanguageAlpha2
from typing import Optional, List
from openLibrary.common.exceptions import OLValidationError
from collections.abc import Iterable
import re

OL_SORT = {
    'editions',
    'old'
    'new'
    'rating'
    'rating asc'
    'rating desc',
    'readinglog'
    'want_to_read'
    'currently_reading'
    'already_read'
    'title'
    'scans'
    # Classifications
    'lcc_sort'
    'lcc_sort asc'
    'lcc_sort desc'
    'ddc_sort'
    'ddc_sort asc'
    'ddc_sort desc'
    # Ebook access
    'ebook_access'
    'ebook_access asc'
    'ebook_access desc'
    # Key
    'key'
    'key asc'
    'key desc'
    # Random
    'random',
    'random asc'
    'random desc'
    'random.hourly'
    'random.daily'
}

DEWEY_SEARCH_PATTERN = re.compile(r'^\d{1,3}\*?$')

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

class OLQuery(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    authors: Optional[list[str]] = None
    subject: Optional[list[str]] = None
    place: Optional[list[str]] = None
    person: Optional[list[str]] = None
    publisher: Optional[list[str]] = None
    first_publish_year: Optional[SupportsRange] 
    ddc: Optional[DDC] = None
    isbn: Optional[ISBN13] = None
    lcc: Optional[str] = None

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
        if self.publish_start:
            r.update({key: f"[{self.publish_start} TO *]"})
    
        if self.publish_start:
            r.update({key: f"[* TO {self.publish_end}]"})
        
        if self.publish_start and self.publish_end:
            r.update({key: f"[{self.publish_start} TO {self.publish_end}]"})
        
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
                
                ored = str.join(" OR ", field_values)
                query.append(f"({ored})")

            else:
                query.append(f'{f}:"{i}"')
        
        query.append(self.time_range) if self.time_range else None
        
        return " AND ".join(query)




class OLSearch(BaseModel):
    """ Model for an Open Library search """
    q: OLQuery
    fields: Optional[List[str]]
    sort: Optional[str] = "title"
    lang: Optional[LanguageAlpha2] = 'en'

    @field_validator()
    @classmethod
    def val_sort(cls, sort):
        if sort:
            if sort not in OL_SORT:
                raise OLValidationError("Unkown sort value provided")
        return sort
    
    @model_validator(mode="after")
    def validate_search(self):
        if not self.q:
            raise OLValidationError("There must be a search query")
        
        return self
