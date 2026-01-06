import uuid
from typing import Optional
from sqlmodel import Session, select
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories import InboxRepository
from src.domain.models import Inbox, Message
from src.infrastructure.mappers.message_mapper import MessageMapper

from src.infrastructure.database.models import InboxDB, MessageDB

from src.infrastructure.mappers.inbox_mapper import InboxMapper


class SqlAlchemyInboxRepository(InboxRepository):
    """
    SQLAlchemy implementation of the InboxRepository.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = InboxMapper()
        self.message_mapper = MessageMapper()

    async def get_by_id(self, inbox_id: uuid.UUID) -> Optional[Inbox]:
        statement = select(InboxDB).where(InboxDB.id == inbox_id)
        result = await self.session.execute(statement)
        inbox_db = result.scalar_one_or_none()
        return self.mapper.to_domain(inbox_db) if inbox_db else None

    async def get_messages_for_inbox(
        self, inbox_id: uuid.UUID, limit: int, offset: int
    ) -> List[Message]:
        statement = (
            select(MessageDB)
            .where(MessageDB.inbox_id == inbox_id)
            .order_by(MessageDB.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        rows = result.scalars().all()
        return [self.message_mapper.to_domain(r) for r in rows]

    async def save(self, domain_inbox: Inbox) -> Inbox:
        db_inbox = self.mapper.to_db(domain_inbox)
        # insert or update and handles the 'messages' relationship changes
        merged = await self.session.merge(db_inbox)
        await self.session.commit()
        return self.mapper.to_domain(merged)

    async def get_by_signature(
        self, signature: str, limit: int = 1, offset: int = 0
    ) -> List[Inbox]:
        statement = (
            select(InboxDB)
            .where(InboxDB.owner_signature == signature)
            .order_by(InboxDB.topic.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        rows = result.scalars().all()
        return [self.mapper.to_domain(r) for r in rows]

    async def add_message(self, message: Message) -> Message:
        db_message = self.message_mapper.to_db(message)
        self.session.add(db_message)
        await self.session.commit()
        return self.message_mapper.to_domain(db_message)
