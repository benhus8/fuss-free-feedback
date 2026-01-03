import uuid
from typing import Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from src.domain.repositories import InboxRepository
from src.domain.models import Inbox

from src.infrastructure.database.models import InboxDB

from src.infrastructure.mappers.inbox_mapper import InboxMapper

class SqlAlchemyInboxRepository(InboxRepository):
    """
    SQLAlchemy implementation of the InboxRepository.
    """

    def __init__(self, session: Session):
        self.session = session
        self.mapper = InboxMapper()

    def get_by_id(self, inbox_id: uuid.UUID) -> Optional[Inbox]:
        statement = (
            select(InboxDB)
            .where(InboxDB.id == inbox_id)
            .options(selectinload(InboxDB.messages))
        )
        result = self.session.exec(statement).first()
        
        if not result:
            return None
            
        return self.mapper.to_domain(result)

    def save(self, domain_inbox: Inbox) -> None:
        db_inbox = self.mapper.to_db(domain_inbox)
        
        # If the primary key exists, it updates; otherwise, it inserts.
        # It also handles the 'messages' relationship changes automatically.
        self.session.merge(db_inbox)
        
        self.session.commit()
