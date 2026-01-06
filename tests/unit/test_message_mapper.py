import pytest
import uuid
from datetime import datetime, timezone
from src.infrastructure.mappers.message_mapper import MessageMapper

from src.domain.models import Message
from src.infrastructure.database.models import MessageDB


@pytest.fixture
def mapper():
    return MessageMapper()


def test_to_domain_maps_fields_correctly(mapper):
    inbox_id = uuid.uuid4()
    now_utc = datetime.now(timezone.utc)

    db_entity = MessageDB(
        id=123,
        inbox_id=inbox_id,
        body="Test Message",
        created_at=now_utc,
        signature="test-sig",
    )

    domain_entity = mapper.to_domain(db_entity)

    assert domain_entity.id == 123
    assert domain_entity.inbox_id == inbox_id
    assert domain_entity.body == "Test Message"
    assert domain_entity.created_at == now_utc
    assert domain_entity.signature == "test-sig"


def test_to_domain_adds_utc_timezone_if_naive(mapper):
    inbox_id = uuid.uuid4()
    naive_datetime = datetime(2024, 1, 1, 12, 0, 0)

    db_entity = MessageDB(
        id=1,
        inbox_id=inbox_id,
        body="Naive date test",
        created_at=naive_datetime,
        signature=None,
    )

    domain_entity = mapper.to_domain(db_entity)

    assert domain_entity.created_at.tzinfo == timezone.utc
    assert domain_entity.created_at.year == 2024
    assert domain_entity.created_at.hour == 12


def test_to_domain_returns_none_for_none_input(mapper):
    result = mapper.to_domain(None)
    assert result is None


def test_to_db_maps_fields_correctly(mapper):
    inbox_id = uuid.uuid4()
    now_utc = datetime.now(timezone.utc)

    domain_entity = Message(
        inbox_id=inbox_id,
        body="Domain to DB",
        created_at=now_utc,
        signature="sig-domain",
        id=999,
    )

    db_entity = mapper.to_db(domain_entity)

    assert db_entity.id == 999
    assert db_entity.inbox_id == inbox_id
    assert db_entity.body == "Domain to DB"
    assert db_entity.created_at == now_utc
    assert db_entity.signature == "sig-domain"
