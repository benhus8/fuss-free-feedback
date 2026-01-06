import uuid
from datetime import datetime
from typing import List

from src.domain.exceptions import NotFoundError
from src.application.utils import generate_tripcode
from src.domain.models import Inbox, Message
from src.domain.repositories import InboxRepository
from datetime import timezone


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
        signature = generate_tripcode(username, secret)

        new_inbox = Inbox(
            id=uuid.uuid4(),
            topic=topic,
            owner_signature=signature,
            expires_at=expires_at,
            allow_anonymous=allow_anonymous,
        )

        saved = await self.repository.save(new_inbox)
        return saved.id, signature

    async def reply_to_inbox(
        self, inbox_id: uuid.UUID, body: str, username: str = None, secret: str = None
    ) -> None:
        inbox = await self.repository.get_by_id(inbox_id)
        if not inbox:
            raise NotFoundError("Inbox not found.")

        signature = generate_tripcode(username, secret)

        inbox.validate_new_message(signature)

        new_message = Message(
            inbox_id=inbox.id,
            body=body,
            signature=signature,
            created_at=datetime.now(timezone.utc),
        )

        await self.repository.add_message(new_message)

    async def change_topic(
        self, inbox_id: uuid.UUID, new_topic: str, username: str, secret: str
    ) -> Inbox | None:
        inbox = await self.repository.get_by_id(inbox_id)

        if not inbox:
            raise NotFoundError("Inbox not found.")

        provided_signature = generate_tripcode(username, secret)
        inbox.validate_ownership(provided_signature)

        inbox.change_topic(new_topic)

        await self.repository.save(inbox)
        return inbox

    async def get_messages(
        self, inbox_id: uuid.UUID, username: str, secret: str, page: int, page_size: int
    ) -> List[Message]:
        inbox = await self.repository.get_by_id(inbox_id)
        if not inbox:
            raise NotFoundError("Inbox not found.")

        provided_signature = generate_tripcode(username, secret)
        inbox.validate_ownership(provided_signature)

        messages = await self.repository.get_messages_for_inbox(
            inbox_id=inbox_id, limit=page_size, offset=(page - 1) * page_size
        )

        return messages

    async def list_user_inboxes(
        self, username: str, secret: str, page: int, page_size: int
    ) -> List[Inbox]:
        owner_signature = generate_tripcode(username, secret)
        return await self.repository.get_by_signature(
            owner_signature, limit=page_size, offset=(page - 1) * page_size
        )

    async def get_inbox_metadata(self, inbox_id: uuid.UUID) -> Inbox:
        inbox = await self.repository.get_by_id(inbox_id)

        if not inbox:
            raise NotFoundError("Inbox not found.")

        return inbox
