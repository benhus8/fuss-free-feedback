import uuid
from datetime import datetime

from src.config import settings
from application.utils import generate_tripcode
from src.domain.models import Inbox
from src.infrastructure.repositories.inbox_repository import SqlAlchemyInboxRepository

class InboxService:
    def __init__(self, repository: SqlAlchemyInboxRepository):
        self.repository = repository

    def create_inbox(self, topic: str, username: str, secret: str, expires_at: datetime, allow_anonymous: bool) -> tuple[uuid.UUID, str]:
        signature = generate_tripcode(username, secret)
        
        new_inbox = Inbox(
            id=uuid.uuid4(),
            topic=topic,
            owner_signature=signature,
            expires_at=expires_at,
            allow_anonymous=allow_anonymous
        )
        
        self.repository.save(new_inbox)
        return new_inbox.id, signature

    def get_inbox(self, inbox_id: uuid.UUID) -> Inbox | None:
        return self.repository.get_by_id(inbox_id)

    def reply_to_inbox(self, inbox_id: uuid.UUID, body: str, username: str | None, secret: str | None) -> None:
        inbox = self.repository.get_by_id(inbox_id)
        if not inbox:
            return None

        sender_sig = None
        if username and secret:
            sender_sig = generate_tripcode(username, secret)

        inbox.add_message(body, signature=sender_sig)
        
        self.repository.save(inbox)
        return inbox

    def change_topic(self, inbox_id: uuid.UUID, new_topic: str, username: str, secret: str) -> Inbox | None:
        inbox = self.repository.get_by_id(inbox_id)
        if not inbox:
            return None

        provided_sig = generate_tripcode(username, secret)
        
        inbox.validate_ownership(provided_sig)
        inbox.change_topic(new_topic)
        
        self.repository.save(inbox)
        return inbox
    
