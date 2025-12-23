from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Message:
    """
    Represents a single message within an Inbox.
    """
    body: str
    created_at: datetime # in UTC format
    signature: Optional[str] = None
    id: Optional[int] = None