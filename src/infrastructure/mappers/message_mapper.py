from src.domain.models import Inbox, Message
from src.infrastructure.database.models import InboxDB, MessageDB
from datetime import timezone


# TODO unit tests of that mapper
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
            id=db_entity.id,
            body=db_entity.body,
            created_at=created_at,
            signature=db_entity.signature,
        )
    
    def to_db(self, domain_entity: Message) -> MessageDB:
        return MessageDB(
            id=domain_entity.id,
            body=domain_entity.body,
            created_at=domain_entity.created_at,
            signature=domain_entity.signature,
        )