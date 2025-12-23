from pydantic import BaseModel, FutureDatetime
from datetime import datetime
from typing import Optional
import uuid


class CreateInboxRequest(BaseModel):
    topic: str
    username: str
    secret: str
    expires_at: FutureDatetime 
    allow_anonymous: bool

class ReplyRequest(BaseModel):
    body: str
    username: Optional[str] = None
    secret: Optional[str] = None

class ChangeTopicRequest(BaseModel):
    new_topic: str
    username: str
    secret: str


class InboxPublicResponse(BaseModel):
    id: uuid.UUID
    topic: str
    owner_signature: str
    expires_at: datetime
    allow_anonymous: bool

class CreatedInboxResponse(BaseModel):
    id: uuid.UUID
    tripcode: str


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None