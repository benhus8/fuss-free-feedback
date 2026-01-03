from fastapi import Depends
from sqlmodel import Session
from sqlalchemy import create_engine
from src.config import settings
from src.infrastructure.repositories.inbox import SqlAlchemyInboxRepository
from src.application.services.inbox import InboxService

engine = create_engine(settings.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

def get_repo(session: Session = Depends(get_session)):
    return SqlAlchemyInboxRepository(session)

def get_service(repo: SqlAlchemyInboxRepository = Depends(get_repo)) -> InboxService:
    return InboxService(repository=repo)