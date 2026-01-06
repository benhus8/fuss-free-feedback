from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Message:
    """
    Represents a single message within an Inbox.
    """

    inbox_id: uuid.UUID
    body: str
    created_at: datetime  # in UTC format
    signature: Optional[str] = None
    id: Optional[int] = None
