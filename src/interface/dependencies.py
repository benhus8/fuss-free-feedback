from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from src.domain.repositories import InboxRepository
from src.infrastructure.repositories.inbox import SqlAlchemyInboxRepository
from src.application.services.inbox import InboxService
from src.infrastructure.database import get_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_repo(session: AsyncSession = Depends(get_db_session)) -> InboxRepository:
    return SqlAlchemyInboxRepository(session)


def get_service(repo: InboxRepository = Depends(get_repo)) -> InboxService:
    return InboxService(repository=repo)
