import pytest
from pydantic import ValidationError
import regex

from openLibrary.models.id import (
    OLID,
    LCCN,
    DeweyDecimal,
)
from openLibrary.models.search import (
    Solr,
    OLSearch,
    SupportsRange
)
from tests.mock_data.models import (
    MOCK_LCCN_POST_2K,
    MOCK_LCCN_PRE_2K,
    MOCK_OLID_A,
    MOCK_OLID_M,
    MOCK_OLID_W
)


def test_olid_should_fail():
    with pytest.raises(ValidationError) as exc:
        OLID(olid="gh4356x")
    
    errors = exc.value.errors()

    assert any(
        er['type'] == 'value_error' and 
        "Cannot validate Open Library ID" in er['msg']
        for er in errors
    )

def test_olid_validate_author():
    try:
        olid = OLID(olid=MOCK_OLID_A)
    except ValidationError:
        pytest.fail("OLID failed to validate Author")

    assert olid.is_author()
    assert not olid.is_work()
    assert not olid.is_edition()

def test_olid_validate_work():
    try:
        olid = OLID(olid=MOCK_OLID_W)
    except ValidationError:
        pytest.fail("OLID failed to validate work")

    assert olid.is_work()
    assert not olid.is_author()
    assert not olid.is_edition()

def test_olid_validate_edition():
    try:
        olid = OLID(olid=MOCK_OLID_M)
    except ValidationError:
        pytest.fail("OLID failed to validate edition")

    assert not olid.is_author()
    assert not olid.is_work()
    assert olid.is_edition()

def test_lccn_should_fail():
    with pytest.raises(ValidationError) as exc:
        LCCN(lccn='ashpoisahgo')
    

def test_lccn_should_pass():
    try:
        lccn = LCCN(lccn=MOCK_LCCN_PRE_2K)
    except ValidationError:
        pytest.fail("LCCN failed to validate")
    
    assert lccn.lccn == MOCK_LCCN_PRE_2K
    
def test_lccn_should_pass():
    try:
        lccn = LCCN(lccn=MOCK_LCCN_POST_2K)
    except ValidationError:
        pytest.fail("LCCN failed to validate")
    
    assert lccn.lccn == MOCK_LCCN_POST_2K

def test_dewey_should_fail():
    with pytest.raises(ValidationError) as exc:
        DeweyDecimal(ddn='batman')

def test_solr_expected():
    q = Solr(title="anything",
             subtitle="something",
             authors=['john green', 'hank green'],
             subject=['classics', '', 'fiction'],
             first_publish_year=SupportsRange(start='01-01-2001'))

    assert q

    lucene = q.solr

    assert lucene

    for l in regex.split(r'^{\s|AND|OR}$', lucene):
        assert ':' in l

def test_solr_should_fail():
    with pytest.raises((ValidationError, TypeError)):
        Solr(title=False, authors=False, isbn=False)


