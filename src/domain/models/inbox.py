import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from src.domain.models.message import Message
from src.domain.exceptions import (
    InboxExpiredError,
    TopicChangeNotAllowedError,
    AnonymousMessagesNotAllowedError,
    InvalidSignatureError,
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

    def change_topic(self, new_topic: str, messages: List[Message]) -> None:
        """
        Updates topic. Raises error if inbox is not empty.
        """
        if messages:
            raise TopicChangeNotAllowedError("Inbox already has replies.")
        self.topic = new_topic

    def validate_new_message(self, signature: Optional[str]) -> None:
        """
        checks if a new message can be added
        """
        if self.is_expired:
            raise InboxExpiredError("This inbox has expired.")

        if not self.allow_anonymous and signature is None:
            raise AnonymousMessagesNotAllowedError(
                "Anonymous messages are not allowed here."
            )
