from abc import ABC, abstractmethod
import uuid
from typing import Optional
from src.domain.models import Inbox


class InboxRepository(ABC):
    """
    Defines the contract for persisting Inbox aggregates.
    """

    @abstractmethod
    def save(self, inbox: Inbox) -> None:
        """
        Saves or updates the Inbox aggregate root and its children (messages).
        """
        pass

    @abstractmethod
    def get_by_id(self, inbox_id: uuid.UUID) -> Optional[Inbox]:
        """
        Retrieves an Inbox aggregate by its unique identifier.
        """
        pass

    @abstractmethod
    def get_by_signature(self, signature: str, limit: int, offset: int) -> list[Inbox]:
        """
        Retrieves all Inboxes owned by the given signature.
        """
        pass

    @abstractmethod
    def get_messages_for_inbox(
        self, inbox_id: uuid.UUID, limit: int, offset: int
    ) -> list:
        """
        Retrieves messages for a given Inbox with pagination.
        """
        pass
