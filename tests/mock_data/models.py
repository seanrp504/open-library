import faker
import random

mock = faker.Faker()

MOCK_ISBN10 = mock.isbn10()
MOCK_ISBN13 = isbn=mock.isbn13()
MOCK_OLID_W = olid="OL45804W"
MOCK_OLID_M = olid="OL7353617M"
MOCK_OLID_A = olid="OL23919A"

MOCK_LCCN_POST_2K = "2003045631"
MOCK_LCCN_PRE_2K = "75061201"


MOCK_DEWEY = "523.1"
MOCK_COVER_SIZE = random.choices(['S', 's', 'M', 'm', 'L', 'l'])


