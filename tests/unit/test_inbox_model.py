import pytest
import uuid
from datetime import datetime, timedelta, timezone
from src.domain.models import Inbox

from src.domain.exceptions import (
    InboxExpiredError,
    TopicChangeNotAllowedError,
    AnonymousMessagesNotAllowedError,
    InvalidSignatureError,
)


@pytest.fixture
def valid_inbox():
    return Inbox(
        id=uuid.uuid4(),
        topic="General Topic",
        owner_signature="owner123",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        allow_anonymous=True,
        messages=[],
    )


@pytest.fixture
def expired_inbox():
    return Inbox(
        id=uuid.uuid4(),
        topic="Old Topic",
        owner_signature="owner123",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        allow_anonymous=True,
        messages=[],
    )


@pytest.fixture
def strict_inbox():
    return Inbox(
        id=uuid.uuid4(),
        topic="Strict Topic",
        owner_signature="owner123",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        allow_anonymous=False,
        messages=[],
    )


def test_is_expired_returns_false_for_future_date(valid_inbox):
    assert valid_inbox.is_expired is False


def test_is_expired_returns_true_for_past_date(expired_inbox):
    assert expired_inbox.is_expired is True


def test_validate_ownership_success(valid_inbox):
    valid_inbox.validate_ownership("owner123")


def test_validate_ownership_raises_error(valid_inbox):
    with pytest.raises(InvalidSignatureError):
        valid_inbox.validate_ownership("wrong_signature")


def test_change_topic_success_when_empty(valid_inbox):
    valid_inbox.change_topic("New Topic", has_messages=False)
    assert valid_inbox.topic == "New Topic"


def test_change_topic_fails_when_messages_exist(valid_inbox):
    valid_inbox.messages.append("Dummy Message")

    with pytest.raises(TopicChangeNotAllowedError):
        valid_inbox.change_topic("New Topic", has_messages=True)

    assert valid_inbox.topic == "General Topic"


def test_validate_new_message_success_anonymous(valid_inbox):
    valid_inbox.validate_new_message(signature=None)


def test_validate_new_message_success_signed(valid_inbox):
    valid_inbox.validate_new_message(signature="some_sig")


def test_validate_new_message_fails_expired(expired_inbox):
    with pytest.raises(InboxExpiredError):
        expired_inbox.validate_new_message(signature="sig")


def test_validate_new_message_fails_anonymous_not_allowed(strict_inbox):
    with pytest.raises(AnonymousMessagesNotAllowedError):
        strict_inbox.validate_new_message(signature=None)


def test_validate_new_message_success_strict_signed(strict_inbox):
    strict_inbox.validate_new_message(signature="some_sig")
