import httpx
import logging
import os

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


TRACE = os.getenv("TRACE")

DEFAULT_LEVEL = logging.INFO

if TRACE:
    DEFAULT_LEVEL = logging.DEBUG

FORMATTER = logging.Formatter(
    fmt=" {asctime}.{msecs} - {name} - {funcName} - {levelname} - {message} :: {args}",
    style='{',
    datefmt="%Y-%m-%d %H:%M:%S"
)

CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)

FILE_HANDLER = None
if os.getenv("FILE_LOGGING"):
    FILE_HANDLER = logging.FileHandler(
        f"{os.getcwd()}/open-library.log",
        encoding="utf-8"
    )
    FILE_HANDLER.setFormatter(FORMATTER)

