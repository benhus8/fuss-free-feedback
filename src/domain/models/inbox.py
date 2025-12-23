import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from domain.models.message import Message
from domain.exceptions import (
    InboxExpiredError,
    TopicChangeNotAllowedError,
    AnonymousMessagesNotAllowedError,
    InvalidSignatureError
)


@dataclass
class Inbox:
    id: uuid.UUID
    topic: str
    owner_signature: str
    expires_at: datetime
    allow_anonymous: bool
    messages: List[Message] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    def validate_ownership(self, provided_signature: str) -> None:
        if self.owner_signature != provided_signature:
            raise InvalidSignatureError("ACCESS_DENIED")

    def change_topic(self, new_topic: str) -> None:
        """
        Updates topic. Raises error if inbox is not empty.
        """
        if self.messages:
            raise TopicChangeNotAllowedError("Inbox already has replies.")
        self.topic = new_topic

    def add_message(self, body: str, signature: Optional[str] = None) -> Message:
        """
        Adds a reply enforcing expiration and anonymity rules.
        """
        if self.is_expired:
            raise InboxExpiredError("Inbox expired.")

        if not self.allow_anonymous and signature is None:
            raise AnonymousMessagesNotAllowedError("Signature required.")

        new_msg = Message(
            body=body,
            timestamp=datetime.now(timezone.utc),
            signature=signature
        )
        self.messages.append(new_msg)
        return new_msg