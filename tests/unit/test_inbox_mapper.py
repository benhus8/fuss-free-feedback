import pytest
import uuid
from datetime import datetime, timezone
from src.infrastructure.mappers.inbox_mapper import InboxMapper

from src.domain.models import Inbox
from src.infrastructure.database.models import InboxDB


@pytest.fixture
def mapper():
    return InboxMapper()


def test_to_domain_maps_fields_correctly(mapper):
    inbox_id = uuid.uuid4()
    expires_at = datetime(2030, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    db_entity = InboxDB(
        id=inbox_id,
        topic="Unit Test Topic",
        owner_signature="sig-123",
        expires_at=expires_at,
        allow_anonymous=True,
    )

    domain_entity = mapper.to_domain(db_entity)

    assert domain_entity.id == inbox_id
    assert domain_entity.topic == "Unit Test Topic"
    assert domain_entity.owner_signature == "sig-123"
    assert domain_entity.expires_at == expires_at
    assert domain_entity.allow_anonymous is True


def test_to_domain_adds_utc_timezone_if_naive(mapper):
    naive_expires = datetime(2025, 5, 20, 15, 30, 0)

    db_entity = InboxDB(
        id=uuid.uuid4(),
        topic="Naive Date Test",
        owner_signature="sig-naive",
        expires_at=naive_expires,
        allow_anonymous=False,
    )

    domain_entity = mapper.to_domain(db_entity)

    assert domain_entity.expires_at.tzinfo == timezone.utc
    assert domain_entity.expires_at.year == 2025
    assert domain_entity.expires_at.hour == 15


def test_to_domain_returns_none_for_none_input(mapper):
    result = mapper.to_domain(None)
    assert result is None


def test_to_db_maps_fields_correctly(mapper):
    inbox_id = uuid.uuid4()
    expires_at = datetime.now(timezone.utc)

    domain_entity = Inbox(
        id=inbox_id,
        topic="Domain to DB",
        owner_signature="owner-sig",
        expires_at=expires_at,
        allow_anonymous=True,
    )

    db_entity = mapper.to_db(domain_entity)

    assert db_entity.id == inbox_id
    assert db_entity.topic == "Domain to DB"
    assert db_entity.owner_signature == "owner-sig"
    assert db_entity.expires_at == expires_at
    assert db_entity.allow_anonymous is True
