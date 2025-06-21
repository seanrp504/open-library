
from openLibrary.common.exceptions import OLValidationError
from pydantic import (
    BaseModel,
    model_validator,
    field_validator,
    computed_field,
    ValidationError,
    PositiveFloat,
    UUID4
)
from pydantic_extra_types.isbn import ISBN
from typing import Optional, Any, List
from datetime import datetime
from uuid import (
    uuid4 as v4,
    
)
import re


OLID_PATTERN = re.compile( r'^OL\d+[MWA]$' )
CLEAN_PATTERN = re.compile( r'[\s-]' )
LCCN_PATTERN = re.compile( r'^([n]{1}[bro]{1})?([s]{1}[hjp]{1})?(\d{2}|\d{4})?\d{6}(AK|AM|ACN|AK|F|HE|M|MAP|MN|MP|NE|PP|R)?$' )
DDS_PATTER = re.compile( r'^\d{3}(\.\d{1,10})?$' )


class ISBN13(BaseModel):
    ''' 
    Model to normalize all ISBNs to ISBN13 
    must pass pydantic-extra-types ISBN validation

    Args:
        isbn (int | str): an isbn 10 or 13 number 

    Return:
        ISBN13: An ISBN13 object
    
    Raises: 
        ValidationError: If ISBN is invalid
    
    '''
    isbn: ISBN

    @field_validator("isbn", mode="before")
    @classmethod
    def convert_to_isbn13(cls, isbn: ISBN):
        return isbn.convert_isbn10_to_isbn13()
    

class OLID(BaseModel):
    ''' 
    Model for Open Library IDs 

    Args:
        olid (str): an open library id \n
            normalized to uppercase \n
            validated by -> r'OL\d+(WMA)'
    
    Returns: 
        OLID: An OLID object

    Raises: 
        ValidationError: If fails regex
    
    '''
    olid: str

    @field_validator("olid", mode="before")
    @classmethod
    def normalize(cls, v: Any):
        return str(v).strip().upper()

    @model_validator(mode="before")
    @classmethod
    def validate(cls, data):
        if isinstance(data, dict):
            if 'olid' in data:
                clean = re.sub(CLEAN_PATTERN, "", data["olid"])

                if not re.fullmatch(OLID_PATTERN, clean):
                    raise OLValidationError('Cannot validate Open Library ID')
                
                data["olid"] = clean

        return data
    
    def is_work(self) -> bool:
        """
        Checks if OLID is for a work

        Returns:
            bool:
        """
        return self.olid.endswith('W')
    
    def is_author(self) -> bool:
        """
        Checks if OLID is for an author

        Returns:
            bool:
        """
        return self.olid.endswith('A')
    
    def is_edition(self) -> bool:
        """
        Checks if OLID is for an edition

        Returns:
            bool:
        """
        return self.olid.endswith('M')
    
    @classmethod
    def is_olid(cls, olid: str) -> bool:
        try: 
            cls(olid=olid)
            return True
        except ValidationError:
            return False
    
class LCCN(BaseModel):
    ''' 
    Model for Library of Congress Control Numbers 
    
    Args:
        lccn (str): validated by
    
    Returns:
        LCCN: an lCCN object
    
    Raises:
        ValidationError:
    '''
    lccn: str

    @field_validator("lccn", mode="before")
    @classmethod
    def _val_lccn(cls, lccn: str) -> str:
        return str(lccn).strip().lower()
    
    @model_validator(mode="after")
    def validate(self):
        clean = re.sub(CLEAN_PATTERN, "", self.lccn)
        if not re.fullmatch(LCCN_PATTERN, clean):
            raise OLValidationError("Cannot validate LCCN Identifier")
        
        return self
    
    @classmethod
    def is_lccn(cls, val):
        """Test validating an LCCN without creating an object"""
        try:
            cls(lccn=val)
            return True
        except ValidationError:
            return False


class DeweyDecimal(BaseModel):
    """ Simple model for a dewey decimal number """
    ddn: PositiveFloat 


    @model_validator(mode='after')
    def validate(self):
        if not re.fullmatch(DDS_PATTER, str(self.ddn)):
            raise OLValidationError("Cannot validate Dewey Decimal")
        return self
    

class coverSize(BaseModel):
    """ 
    size options [S, M, L]
    Best used via classmethods to create sizes 
    """
    size: str

    @field_validator("size", mode="before")
    @classmethod
    def validate_size(cls, size: str) -> str:
        return size.capitalize()
    
    @model_validator(mode="after")
    def validate_model(self):
        if self.size != 'L' or self.size != 'M' or self.size != 'S':
                raise OLValidationError("Unkown Size use [S, M, L]")
        return self
    
    @classmethod
    def small(cls):
        return cls(size="S")
    
    @classmethod
    def medium(cls):
        return cls(size="M")
    
    @classmethod
    def large(cls):
        return cls(size="L")


class Author(BaseModel):
    prefix: Optional[str] 
    first: Optional[str] 
    middle: Optional[str]
    last: Optional[str]
    suffix: Optional[str]

    @field_validator("prefix", "first", "middle", "last", "suffix", mode="before")
    @classmethod
    def normalize(cls, v):
        if v:
            return str(v).strip().capitalize()
    
    @computed_field
    @property
    def full(self) -> str:
        self.model_dump
        parts = [self.prefix, self.first, self.middle, self.last, self.suffix]
        return " ".join(p if p else '' for p in parts if parts)


class book(BaseModel):
    id: UUID4 = v4()
    isbn13: Optional[ISBN13] = None
    olid: Optional[OLID] = None
    lccn: Optional[LCCN] = None
    dewey: Optional[DeweyDecimal] = None
    author: Author
    title: str
    description: Optional[str] = None
    pub_date: datetime | str = None
    publisher: str = None
    genre: str | List[str]
    type: str | List[str] = None
