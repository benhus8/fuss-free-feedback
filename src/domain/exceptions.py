# TODO implement RFC 7807
class DomainError(Exception):
    """Base exception for all domain-related errors."""
    pass

class InboxExpiredError(DomainError):
    """Raised when an action is attempted on an expired inbox."""
    pass

class TopicChangeNotAllowedError(DomainError):
    """Raised when attempting to change the topic of an inbox that already has messages."""
    pass

class AnonymousMessagesNotAllowedError(DomainError):
    """Raised when an anonymous message is sent to an inbox that requires signatures."""
    pass

## TODO change to not found for security reasons?
class InvalidSignatureError(DomainError):
    """Raised when the provided credentials do not match the inbox owner."""
    pass