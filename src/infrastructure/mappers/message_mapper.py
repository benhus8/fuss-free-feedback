from src.domain.models import Message
from src.infrastructure.database.models import MessageDB
from datetime import timezone


class MessageMapper:
    """
    Data Mapper Pattern.
    Responsible for transforming data between Persistence layer and Domain layer.
    """

    def to_domain(self, db_entity: MessageDB) -> Message:
        if not db_entity:
            return None

        created_at = db_entity.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return Message(
            inbox_id=db_entity.inbox_id,
            id=db_entity.id,
            body=db_entity.body,
            created_at=created_at,
            signature=db_entity.signature,
        )

    def to_db(self, domain_entity: Message) -> MessageDB:
        return MessageDB(
            id=domain_entity.id,
            inbox_id=domain_entity.inbox_id,
            body=domain_entity.body,
            created_at=domain_entity.created_at,
            signature=domain_entity.signature,
        )
