import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

from src.application.services.inbox import InboxService
from src.domain.exceptions import (
    NotFoundError,
    InboxExpiredError,
    InvalidSignatureError,
)
from src.domain.models import Inbox, Message

INBOX_ID = uuid.uuid4()
USERNAME = "alice"
SECRET = "secret123"
MOCKED_SIGNATURE = "tripcode_sig"


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return InboxService(repository=mock_repo)


@pytest.fixture
def mock_inbox_entity():
    inbox = MagicMock(spec=Inbox)
    inbox.id = INBOX_ID
    inbox.topic = "Old Topic"
    inbox.validate_new_message.return_value = None
    inbox.validate_ownership.return_value = None
    return inbox


@pytest.mark.asyncio
async def test_create_inbox_success(service, mock_repo):
    with patch(
        "src.application.services.inbox.generate_tripcode",
        return_value=MOCKED_SIGNATURE,
    ):
        saved_inbox = MagicMock()
        saved_inbox.id = INBOX_ID
        mock_repo.save.return_value = saved_inbox
        expires = datetime.now(timezone.utc) + timedelta(days=1)
        result_id, result_sig = await service.create_inbox(
            topic="New Topic",
            username=USERNAME,
            secret=SECRET,
            expires_at=expires,
            allow_anonymous=True,
        )
        assert result_id == INBOX_ID
        assert result_sig == MOCKED_SIGNATURE
        mock_repo.save.assert_called_once()
        args, _ = mock_repo.save.call_args
        inbox_arg = args[0]
        assert isinstance(inbox_arg, Inbox)
        assert inbox_arg.topic == "New Topic"
        assert inbox_arg.owner_signature == MOCKED_SIGNATURE


@pytest.mark.asyncio
async def test_reply_to_inbox_success(service, mock_repo, mock_inbox_entity):
    mock_repo.get_by_id.return_value = mock_inbox_entity

    with patch(
        "src.application.services.inbox.generate_tripcode",
        return_value=MOCKED_SIGNATURE,
    ):
        await service.reply_to_inbox(INBOX_ID, "Hello Body", USERNAME, SECRET)

    mock_repo.get_by_id.assert_called_with(INBOX_ID)

    mock_inbox_entity.validate_new_message.assert_called_with(MOCKED_SIGNATURE)

    mock_repo.add_message.assert_called_once()
    args, kwargs = mock_repo.add_message.call_args
    message_arg = args[0]

    assert isinstance(message_arg, Message)
    assert message_arg.inbox_id == INBOX_ID
    assert message_arg.body == "Hello Body"
    assert message_arg.signature == MOCKED_SIGNATURE


@pytest.mark.asyncio
async def test_reply_to_inbox_not_found(service, mock_repo):
    mock_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        await service.reply_to_inbox(INBOX_ID, "Body", USERNAME, SECRET)
    mock_repo.add_message.assert_not_called()


@pytest.mark.asyncio
async def test_reply_to_inbox_validation_fails(service, mock_repo, mock_inbox_entity):
    mock_repo.get_by_id.return_value = mock_inbox_entity
    mock_inbox_entity.validate_new_message.side_effect = InboxExpiredError("Expired")
    with pytest.raises(InboxExpiredError):
        await service.reply_to_inbox(INBOX_ID, "Body", USERNAME, SECRET)
    mock_repo.add_message.assert_not_called()


@pytest.mark.asyncio
async def test_change_topic_success(service, mock_repo, mock_inbox_entity):
    mock_repo.get_by_id.return_value = mock_inbox_entity

    mock_repo.get_messages_for_inbox.return_value = []

    with patch(
        "src.application.services.inbox.generate_tripcode",
        return_value=MOCKED_SIGNATURE,
    ):
        result = await service.change_topic(
            INBOX_ID, "Brand New Topic", USERNAME, SECRET
        )

    mock_inbox_entity.validate_ownership.assert_called_with(MOCKED_SIGNATURE)

    mock_repo.get_messages_for_inbox.assert_called_with(
        inbox_id=INBOX_ID, limit=1, offset=0
    )

    mock_inbox_entity.change_topic.assert_called_with(
        "Brand New Topic", has_messages=False
    )

    mock_repo.save.assert_called_with(mock_inbox_entity)
    assert result == mock_inbox_entity


@pytest.mark.asyncio
async def test_change_topic_unauthorized(service, mock_repo, mock_inbox_entity):
    mock_repo.get_by_id.return_value = mock_inbox_entity
    mock_inbox_entity.validate_ownership.side_effect = InvalidSignatureError(
        "Bad signature"
    )
    with pytest.raises(InvalidSignatureError):
        await service.change_topic(INBOX_ID, "New Topic", "hacker", "wrong")
    mock_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_get_messages_success(service, mock_repo, mock_inbox_entity):
    mock_repo.get_by_id.return_value = mock_inbox_entity
    expected_messages = [MagicMock(spec=Message), MagicMock(spec=Message)]
    mock_repo.get_messages_for_inbox.return_value = expected_messages
    with patch(
        "src.application.services.inbox.generate_tripcode",
        return_value=MOCKED_SIGNATURE,
    ):
        result = await service.get_messages(
            INBOX_ID, USERNAME, SECRET, page=2, page_size=10
        )
    mock_inbox_entity.validate_ownership.assert_called_with(MOCKED_SIGNATURE)
    mock_repo.get_messages_for_inbox.assert_called_with(
        inbox_id=INBOX_ID, limit=10, offset=10
    )
    assert result == expected_messages


@pytest.mark.asyncio
async def test_get_messages_not_found(service, mock_repo):
    mock_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        await service.get_messages(INBOX_ID, USERNAME, SECRET, 1, 20)


@pytest.mark.asyncio
async def test_list_user_inboxes(service, mock_repo):
    expected_inboxes = [MagicMock(spec=Inbox)]
    mock_repo.get_by_signature.return_value = expected_inboxes
    with patch(
        "src.application.services.inbox.generate_tripcode",
        return_value=MOCKED_SIGNATURE,
    ):
        result = await service.list_user_inboxes(USERNAME, SECRET, page=1, page_size=50)
    mock_repo.get_by_signature.assert_called_with(MOCKED_SIGNATURE, limit=50, offset=0)
    assert result == expected_inboxes


@pytest.mark.asyncio
async def test_get_inbox_metadata_success(service, mock_repo, mock_inbox_entity):
    mock_repo.get_by_id.return_value = mock_inbox_entity
    result = await service.get_inbox_metadata(INBOX_ID)
    assert result == mock_inbox_entity


@pytest.mark.asyncio
async def test_get_inbox_metadata_not_found(service, mock_repo):
    mock_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        await service.get_inbox_metadata(INBOX_ID)
