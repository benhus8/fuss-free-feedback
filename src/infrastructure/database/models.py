import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, Relationship, Index


class MessageDB(SQLModel, table=True):
    """
    Database model for Messages.
    """

    __tablename__ = "messages"

    __table_args__ = (Index("ix_messages_inbox_created", "inbox_id", "created_at"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    body: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    signature: Optional[str] = None

    inbox_id: uuid.UUID = Field(foreign_key="inboxes.id")

    inbox: Optional["InboxDB"] = Relationship(back_populates="messages")


class InboxDB(SQLModel, table=True):
    """
    Database model for Inboxes.
    """

    __tablename__ = "inboxes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    topic: str
    owner_signature: str
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    allow_anonymous: bool

    messages: List[MessageDB] = Relationship(
        back_populates="inbox", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
