import uuid
from datetime import datetime
from typing import List
import logging
from src.domain.exceptions import NotFoundError
from src.application.utils import generate_tripcode
from src.domain.models import Inbox, Message
from src.domain.repositories import InboxRepository
from datetime import timezone

logger = logging.getLogger(__name__)


class InboxService:
    def __init__(self, repository: InboxRepository):
        self.repository = repository

    async def create_inbox(
        self,
        topic: str,
        username: str,
        secret: str,
        expires_at: datetime,
        allow_anonymous: bool,
    ) -> tuple[uuid.UUID, str]:
        logger.info(
            "Creating inbox topic='%s' exp=%s allow_anonymous=%s",
            topic,
            expires_at,
            allow_anonymous,
        )
        signature = generate_tripcode(username, secret)

        new_inbox = Inbox(
            id=uuid.uuid4(),
            topic=topic,
            owner_signature=signature,
            expires_at=expires_at,
            allow_anonymous=allow_anonymous,
        )

        saved = await self.repository.save(new_inbox)
        logger.info("Inbox created id=%s", saved.id)
        return saved.id, signature

    async def reply_to_inbox(
        self, inbox_id: uuid.UUID, body: str, username: str, secret: str
    ) -> None:
        logger.debug("Fetching inbox id=%s for reply", inbox_id)
        inbox = await self._get_inbox_or_fail(inbox_id)

        if username and secret:
            signature = generate_tripcode(username, secret)
        else:
            signature = None

        logger.debug("Validating new message for inbox id=%s", inbox.id)
        inbox.validate_new_message(signature)

        new_message = Message(
            inbox_id=inbox.id,
            body=body,
            signature=signature,
            created_at=datetime.now(timezone.utc),
        )

        await self.repository.add_message(new_message)
        logger.info("Message appended to inbox id=%s", inbox.id)

    async def change_topic(
        self, inbox_id: uuid.UUID, new_topic: str, username: str, secret: str
    ) -> Inbox | None:
        logger.debug("Fetching inbox id=%s to change topic", inbox_id)
        inbox = await self._get_inbox_or_fail(inbox_id)
        self._validate_owner(inbox, username, secret)

        inbox_message = await self.repository.get_messages_for_inbox(
            inbox_id=inbox.id, limit=1, offset=0
        )
        inbox.change_topic(new_topic, inbox_message)

        await self.repository.save(inbox)
        logger.info("Inbox topic changed id=%s", inbox.id)
        return inbox

    async def get_messages(
        self, inbox_id: uuid.UUID, username: str, secret: str, page: int, page_size: int
    ) -> List[Message]:
        logger.debug(
            "Fetching messages inbox_id=%s page=%d size=%d",
            inbox_id,
            page,
            page_size,
        )
        inbox = await self._get_inbox_or_fail(inbox_id)

        self._validate_owner(inbox, username, secret)

        messages = await self.repository.get_messages_for_inbox(
            inbox_id=inbox_id, limit=page_size, offset=(page - 1) * page_size
        )
        logger.info(
            "Fetched %d messages inbox_id=%s page=%d size=%d",
            len(messages),
            inbox_id,
            page,
            page_size,
        )
        return messages

    async def list_user_inboxes(
        self, username: str, secret: str, page: int, page_size: int
    ) -> List[Inbox]:
        owner_signature = generate_tripcode(username, secret)
        logger.info("Listing inboxes page=%d size=%d", page, page_size)
        return await self.repository.get_by_signature(
            owner_signature, limit=page_size, offset=(page - 1) * page_size
        )

    async def get_inbox_metadata(self, inbox_id: uuid.UUID) -> Inbox:
        logger.debug("Fetching inbox metadata id=%s", inbox_id)
        inbox = await self._get_inbox_or_fail(inbox_id)

        logger.info("Fetched inbox metadata id=%s", inbox.id)
        return inbox

    async def _get_inbox_or_fail(self, inbox_id: uuid.UUID) -> Inbox:
        logger.debug("Fetching inbox id=%s", inbox_id)
        inbox = await self.repository.get_by_id(inbox_id)
        if not inbox:
            logger.warning("Inbox not found id=%s", inbox_id)
            raise NotFoundError("Inbox not found.")
        return inbox

    def _validate_owner(self, inbox: Inbox, username: str, secret: str) -> None:
        signature = generate_tripcode(username, secret)
        logger.debug("Validating ownership for inbox id=%s", inbox.id)
        inbox.validate_ownership(signature)
