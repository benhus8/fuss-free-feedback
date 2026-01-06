import uuid
from datetime import datetime
from typing import List

from src.domain.exceptions import NotFoundError
from src.application.utils import generate_tripcode
from src.domain.models import Inbox, Message
from src.domain.repositories import InboxRepository


class InboxService:
    def __init__(self, repository: InboxRepository):
        self.repository = repository

    def create_inbox(
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

        saved = self.repository.save(new_inbox)
        return saved.id, signature

    def reply_to_inbox(
        self, inbox_id: uuid.UUID, body: str, username: str | None, secret: str | None
    ) -> None:
        inbox = self.repository.get_by_id(inbox_id)
        if not inbox:
            return None

        sender_signature = None
        if username and secret:
            sender_signature = generate_tripcode(username, secret)

        inbox.add_message(body, signature=sender_signature)

        self.repository.save(inbox)

    def change_topic(
        self, inbox_id: uuid.UUID, new_topic: str, username: str, secret: str
    ) -> Inbox | None:
        inbox = self.repository.get_by_id(inbox_id)

        if not inbox:
            raise NotFoundError("Inbox not found.")

        provided_signature = generate_tripcode(username, secret)
        inbox.validate_ownership(provided_signature)

        inbox.change_topic(new_topic)

        self.repository.save(inbox)
        return inbox

    def get_messages(
        self, inbox_id: uuid.UUID, username: str, secret: str, page: int, page_size: int
    ) -> List[Message]:
        inbox = self.repository.get_by_id(inbox_id)
        if not inbox:
            raise NotFoundError("Inbox not found.")

        provided_signature = generate_tripcode(username, secret)
        inbox.validate_ownership(provided_signature)

        messages = self.repository.get_messages_for_inbox(
            inbox_id=inbox_id, limit=page_size, offset=(page - 1) * page_size
        )

        return messages

    def list_user_inboxes(
        self, username: str, secret: str, page: int, page_size: int
    ) -> List[Inbox]:
        owner_signature = generate_tripcode(username, secret)
        return self.repository.get_by_signature(
            owner_signature, limit=page_size, offset=(page - 1) * page_size
        )

    def get_inbox_metadata(self, inbox_id: uuid.UUID) -> Inbox:
        inbox = self.repository.get_by_id(inbox_id)

        if not inbox:
            raise NotFoundError("Inbox not found.")

        return inbox
