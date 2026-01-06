from abc import ABC, abstractmethod
import uuid
from typing import Optional, List
from src.domain.models import Inbox
from src.domain.models.message import Message


class InboxRepository(ABC):
    """
    Defines the contract for persisting Inbox aggregates.
    """

    @abstractmethod
    async def save(self, inbox: Inbox) -> Inbox:
        """
        Saves or updates the Inbox aggregate root and its children (messages).
        """
        pass

    @abstractmethod
    async def get_by_id(self, inbox_id: uuid.UUID) -> Optional[Inbox]:
        """
        Retrieves an Inbox aggregate by its unique identifier.
        """
        pass

    @abstractmethod
    async def get_by_signature(
        self, signature: str, limit: int, offset: int
    ) -> List[Inbox]:
        """
        Retrieves all Inboxes owned by the given signature.
        """
        pass

    @abstractmethod
    async def get_messages_for_inbox(
        self, inbox_id: uuid.UUID, limit: int, offset: int
    ) -> List[Message]:
        """
        Retrieves messages for a given Inbox with pagination.
        """
        pass

    @abstractmethod
    async def add_message(self, message: Message) -> Message:
        """
        Saves a single Message entity to the database.
        """
        pass
