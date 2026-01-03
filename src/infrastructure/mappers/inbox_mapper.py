from src.domain.models import Inbox, Message
from src.infrastructure.database.models import InboxDB, MessageDB

#TODO unit tests of that mapper
class InboxMapper:
    """
    Data Mapper Pattern.
    Responsible for transforming data between Persistence layer and Domain layer.
    """

    def to_domain(self, db_entity: InboxDB) -> Inbox:
        if not db_entity:
            return None
            
        domain_messages = [
            Message(
                id=m.id,
                body=m.body,
                created_at=m.created_at,
                signature=m.signature
            ) for m in db_entity.messages
        ]

        return Inbox(
            id=db_entity.id,
            topic=db_entity.topic,
            owner_signature=db_entity.owner_signature,
            expires_at=db_entity.expires_at,
            allow_anonymous=db_entity.allow_anonymous,
            messages=domain_messages
        )

    def to_db(self, domain_entity: Inbox) -> InboxDB:
        messages_db = [
            MessageDB(
                id=m.id,
                body=m.body,
                created_at=m.created_at,
                signature=m.signature,
                inbox_id=domain_entity.id
            ) for m in domain_entity.messages
        ]

        return InboxDB(
            id=domain_entity.id,
            topic=domain_entity.topic,
            owner_signature=domain_entity.owner_signature,
            expires_at=domain_entity.expires_at,
            allow_anonymous=domain_entity.allow_anonymous,
            messages=messages_db
        )