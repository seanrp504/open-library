from pydantic import (
    BaseModel,
    field_validator,
    HttpUrl
)
from openLibrary.common.base import OLBase


class Excerpt(BaseModel):
    excerpt: str

class Key(BaseModel):
    key: str

    @field_validator
    @classmethod
    def unpack(cls, key: str):
        return OLBase.clean_slash(key)

class Link(BaseModel):
    title: str
    url: HttpUrl
    type: Key

class AuthorDict(BaseModel):
    author: Key
    type: Key