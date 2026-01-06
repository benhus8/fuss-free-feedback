from src.domain.models import Inbox
from src.infrastructure.database.models import InboxDB
from datetime import timezone


class InboxMapper:
    """
    Data Mapper Pattern.
    Responsible for transforming data between Persistence layer and Domain layer.
    """

    def to_domain(self, db_entity: InboxDB) -> Inbox:
        if not db_entity:
            return None

        expires_at = db_entity.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return Inbox(
            id=db_entity.id,
            topic=db_entity.topic,
            owner_signature=db_entity.owner_signature,
            expires_at=expires_at,
            allow_anonymous=db_entity.allow_anonymous,
        )

    def to_db(self, domain_entity: Inbox) -> InboxDB:

        return InboxDB(
            id=domain_entity.id,
            topic=domain_entity.topic,
            owner_signature=domain_entity.owner_signature,
            expires_at=domain_entity.expires_at,
            allow_anonymous=domain_entity.allow_anonymous,
        )
