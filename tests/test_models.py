import pytest
from pydantic import ValidationError
from openLibrary.models.id import (
    ISBN13,
    OLID,
    LCCN,
    DeweyDecimal,
    coverSize,
    bookID
)
from openLibrary.models.search import (
    OLQuery,
    OLSearch
)
from mock_data.models import (
    MOCK_ISBN10,
    MOCK_ISBN13 ,
    MOCK_COVER_SIZE,
    MOCK_DEWEY,
    MOCK_LCCN_POST_2K,
    MOCK_LCCN_PRE_2K,
    MOCK_OLID_A,
    MOCK_OLID_M,
    MOCK_OLID_W
)
@pytest.mark.isbn
@pytest.mark.isbn_model
def test_isbn_should_fail():
    with pytest.raises(ValidationError) as exc:
        ISBN13(isbn='abdefghijklmnop')
    
    errors = exc.value.errors()

    assert any(
        er['type'] == 'value_error'
        for er in errors
    )

@pytest.mark.isbn
@pytest.mark.isbn_model
def test_isbn_13():
    try:
        isbn = ISBN13(isbn=MOCK_ISBN13)
    except ValidationError:
        pytest.fail("ISBN13 failed to validate isbn13")

    assert isbn.isbn == MOCK_ISBN13

@pytest.mark.isbn
@pytest.mark.isbn_model
def test_isbn_13():
    try:
        isbn = ISBN13(isbn=MOCK_ISBN10)
    except ValidationError:
        pytest.fail("ISBN13 failed to validate isbn10")

    assert isbn.isbn == MOCK_ISBN10
    assert len(isbn.isbn) == 13


@pytest.mark.olid
@pytest.mark.olid_model
def test_olid_should_fail():
    with pytest.raises(ValidationError) as exc:
        OLID(olid="gh4356x")
    
    errors = exc.value.errors()

    assert any(
        er['type'] == 'value_error' and 
        "Cannot validate Open Library ID" in er['msg']
        for er in errors
    )

@pytest.mark.olid
@pytest.mark.olid_model
def test_olid_validate_author():
    try:
        olid = OLID(olid=MOCK_OLID_A)
    except ValidationError:
        pytest.fail("OLID failed to validate Author")

    assert olid.is_author()
    assert not olid.is_work()
    assert not olid.is_edition()

@pytest.mark.olid
@pytest.mark.olid_model
def test_olid_validate_work():
    try:
        olid = OLID(olid=MOCK_OLID_W)
    except ValidationError:
        pytest.fail("OLID failed to validate work")

    assert olid.is_author()
    assert not olid.is_work()
    assert not olid.is_edition()

@pytest.mark.olid
@pytest.mark.olid_model
def test_olid_validate_edition():
    try:
        olid = OLID(olid=MOCK_OLID_M)
    except ValidationError:
        pytest.fail("OLID failed to validate edition")

    assert not olid.is_author()
    assert not olid.is_work()
    assert olid.is_edition()

@pytest.mark.lccn
@pytest.mark.lccn_model
def test_lccn_should_fail():
    with pytest.raises(ValidationError) as exc:
        LCCN(lccn='ashpoisahgo')
    
    errors = exc.value.errors()

    assert any(
        er['type'] == 'value_error' and 
        "Cannot validate LCCN Identifier" in er['msg']
        for er in errors
    )

@pytest.mark.lccn
@pytest.mark.lccn_model
def test_lccn_should_pass():
    try:
        lccn = LCCN(lccn=MOCK_LCCN_PRE_2K)
    except ValidationError:
        pytest.fail("LCCN failed to validate")
    
    assert lccn.lccn == MOCK_LCCN_PRE_2K
    assert lccn.is_pre_2k()
    
@pytest.mark.lccn
def test_lccn_should_pass():
    try:
        lccn = LCCN(lccn=MOCK_LCCN_POST_2K)
    except ValidationError:
        pytest.fail("LCCN failed to validate")
    
    assert lccn.lccn == MOCK_LCCN_POST_2K
    assert lccn.is_post_2k()

@pytest.mark.dewey
def test_dewey_should_fail():
    with pytest.raises(ValidationError) as exc:
        DeweyDecimal(ddn='batman')

    errors = exc.value.errors()

    assert any(
        er['type'] == 'value_error' and 
        "Cannot validate Dewey Decimal" in er['msg']
        for er in errors
    )

@pytest.mark.cover
def test_cover_should_fail():
    with pytest.raises(ValidationError) as exc:
        coverSize(size='batman')

    errors = exc.value.errors()

    assert any(
        er['type'] == 'value_error' and 
        "Unkown Size use [S, M, L]" in er['msg']
        for er in errors
    )






