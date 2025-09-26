from openLibrary.models.book import BookEdition
from pydantic_extra_types.isbn import ISBN
from faker import Faker
import json

from tests.mock_data.models import MOCK_ISBN10, MOCK_ISBN13
mock = Faker()

def test_book_by_isbn():
    ed = BookEdition.get(ISBN(MOCK_ISBN13))

    assert ed
    assert ed.authors
    

def test_book_from_static():
    with open('tests/mock_data/OL9242848M.json', 'r') as f:
        edition = json.load(f)

    assert BookEdition.unpack(edition)

   
