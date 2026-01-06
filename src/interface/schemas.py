import uuid
from datetime import datetime
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field, FutureDatetime, ConfigDict, model_validator


TopicType = Annotated[
    str, Field(min_length=5, max_length=100, description="Subject of the discussion")
]
UsernameType = Annotated[
    str, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
]
SecretType = Annotated[
    str, Field(min_length=8, max_length=100, description="Password/Secret for signing")
]


class BaseSchema(BaseModel):
    """Base configuration for all input schemas."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )


class CreateInboxRequest(BaseSchema):
    topic: TopicType
    username: UsernameType
    secret: SecretType
    expires_at: FutureDatetime
    allow_anonymous: bool

    @model_validator(mode="after")
    def ensure_credentials_present(self):
        if not self.username or not self.secret:
            raise ValueError("Username and secret are required to create an inbox.")
        return self


class ReplyRequest(BaseSchema):
    body: str = Field(..., min_length=1, max_length=1000, description="Message content")
    username: Optional[UsernameType] = None
    secret: Optional[SecretType] = None

    @model_validator(mode="after")
    def check_credentials_completeness(self):
        """
        Checks consistency: If a username is provided, a secret must also be provided
        """
        user, sec = self.username, self.secret
        if (user and not sec) or (sec and not user):
            raise ValueError(
                "Both username and secret must be provided for a signed message."
            )
        return self


class ChangeTopicRequest(BaseSchema):
    new_topic: TopicType


class InboxOverview(BaseModel):
    id: uuid.UUID
    topic: str
    expires_at: datetime
    allow_anonymous: bool

    model_config = ConfigDict(from_attributes=True)


class InboxesResponse(BaseModel):
    inboxes: List[InboxOverview]

    model_config = ConfigDict(from_attributes=True)


class InboxPublicResponse(BaseModel):
    id: uuid.UUID
    topic: str
    owner_signature: str
    expires_at: datetime
    allow_anonymous: bool


class CreatedInboxResponse(BaseModel):
    id: uuid.UUID
    signature: str


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None


class MessageOverview(BaseModel):
    id: int
    body: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessagesResponse(BaseModel):
    messages: List[MessageOverview]

    model_config = ConfigDict(from_attributes=True)
