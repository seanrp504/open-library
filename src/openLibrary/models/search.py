from pydantic import BaseModel, model_validator, field_validator
from openLibrary.models.books import DeweyDecimal
from pydantic_extra_types.language_code import LanguageAlpha2
from typing import Optional, List
from openLibrary.common.exceptions import OLValidationError
from collections.abc import Iterable

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

class OLQuery(BaseModel):
    title: Optional[str | List[str]] = None
    author: Optional[str | List[str]] = None
    subject: Optional[str | List[str]] = None
    place: Optional[str | List[str]] = None
    person: Optional[str | List[str]] = None
    publisher: Optional[str | List[str]] = None
    first_publish_year: Optional[str | List[str]] = None
    ddn: Optional[DeweyDecimal | List[DeweyDecimal]] = None

    @field_validator("first_publish_year", mode="before")
    @classmethod
    def vaildate_publish_year(cls, years):
        if type(years) == list:
            if len(years) < 2 or len(years) > 3:
                raise OLValidationError("p")
        return years
    
    @model_validator(mode="after")
    def validate_min_one(self):
        if not any(getattr(self, field) is not None for field in self.model_fields_set):
            raise ValueError('At least one value must be present to create a bookID object')
        return self
    
    def to_solr(self) -> str:
        ''' conver the model to a solr query'''
        query = []

        for field_name in self.model_fields_set:
            attr: str = getattr(self, field_name)

            if field_name == 'first_publish_year' and isinstance(attr, Iterable):
                pass

            elif isinstance(attr, Iterable):
                field_values = []
                for i in attr:
                    field_values.append(f'{field_name}:"{i}"')
                
                ored = str.join(" OR ", field_values)
                query.append(f"({ored})")

            else:
                query.append(f'{field_name}:"{i}"')
        
        return str.join(" AND ", query)




class OLSearch(BaseModel):
    """ Model for an Open Library search """
    q: OLQuery
    fields: Optional[str | List[str]]
    sort: Optional[str] = None
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
