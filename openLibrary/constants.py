import httpx

_ISBN = 'isbn'
_OLID = 'olid'
_LCCN = 'lccn'
_WORKS = 'works'
_BOOKS = 'books'
_COVERS = 'covers'
_AUTHORS = 'authors'
_SEARCH = 'search.json'
BASE_DOMAIN = 'openlibrary.org'
SLASH = '/'

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

TIMEOUT_CONFIG = httpx.Timeout(10.0, connect=4.0, read=6.0)