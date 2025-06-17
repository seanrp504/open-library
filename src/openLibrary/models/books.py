
from openLibrary.common.exceptions import OLValidationError
from pydantic import BaseModel, model_validator, field_validator
from pydantic_extra_types.isbn import ISBN
from typing import Optional
import re

OLID_PATTERN = re.compile(r'^OL\d+[MW]$')
CLEAN_PATTERN = re.compile(r'[\s-]')
LCCN_PATTERN_A = re.compile(r'^[a-z]{2}(98|99|[0-8][0-9])\d{6}[\da-z]?}$')
LCCN_PATTERN_B = re.compile(r'^[a-z]{2}(20|[0-9][0-9])\d{6}$')
DDS_PATTER = re.compile(r'^\d{3}(\.\d{1,10})?$')


class ISBN13(BaseModel):
    ''' Model to normalize all ISBNs to ISBN13 '''
    isbn: ISBN

    @model_validator(mode="before")
    @classmethod
    def validate(cls, data):
        if isinstance(data, dict):
            if "isbn" in data:
                data["isbn"] = ISBN.convert_isbn10_to_isbn13(data["isbn"])

            else:
                raise OLValidationError("Cannot validate ISBN number")
            
        return data
    
class OLID(BaseModel):
    ''' Model for Open Library IDs '''
    olid: str

    @model_validator(mode="before")
    @classmethod
    def validate(cls, data):
        if isinstance(data, dict):
            if 'olid' in data:
                clean = re.sub(CLEAN_PATTERN, "", data["olid"])

                if not re.fullmatch(OLID_PATTERN, clean):
                    raise ValueError('Cannot validate Open Library ID')
                
                data["olid"] = clean

        return data
    
class LCCN(BaseModel):
    ''' Model for Library of Congress Control Numbers '''
    lccn: str

    @field_validator("lccn", mode="before")
    @classmethod
    def val_lccn(cls, lccn: str) -> str:
        return lccn.lower()

    @model_validator(mode="after")
    @classmethod
    def validate(self):
        clean = re.sub(CLEAN_PATTERN, "", self.lccn)
        if not re.fullmatch(LCCN_PATTERN_A, clean) or re.fullmatch(LCCN_PATTERN_B, clean):
            raise OLValidationError("Cannot validate LCCN Identifier")
        
        return self

class DeweyDecimal(BaseModel):
    """ Simple modael for a dewey decimal number """
    ddn: int | float

    @model_validator(mode='after')
    def validate(self):
        if not re.fullmatch(DDS_PATTER, str(self.ddn)):
            raise OLValidationError("Cannot validate Dewey Decimal")
        return self
    

class coverSize(BaseModel):
    """ 
    size options [S, M, L]
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


class bookID(BaseModel):
    isbn13: Optional[ISBN13] = None
    olid: Optional[OLID] = None
    lccn: Optional[LCCN] = None

    @model_validator(mode="after")
    def validate_min_one(self):
        if not any(getattr(self, field) is not None for field in self.model_fields_set):
            raise OLValidationError('At least one value must be present to create a bookID object')
        return self