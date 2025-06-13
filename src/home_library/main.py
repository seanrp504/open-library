from fastapi import FastAPI
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str
    isbn: int
    publisher: str | None = None
    series_name: str | None = None
    description: str | None = None
    price: float | None = None




app = FastAPI() 

@app.get("/")
def root():
    return {"test": True}

@app.post("/book/", status_code=201)
def add_book(book: Book) -> Book: 
    return Book

