import uuid
from fastapi import APIRouter, Depends, Response, Query, Header
from fastapi.responses import JSONResponse
from typing import List

from src.interface.dependencies import get_service
from src.application.services.inbox import InboxService
from src.interface.schemas import (
    CreateInboxRequest,
    ReplyRequest,
    ChangeTopicRequest,
    CreatedInboxResponse,
    InboxesResponse,
    MessagesResponse,
    InboxPublicResponse,
)

router = APIRouter(tags=["Inboxes"], prefix="/inboxes")


@router.post("/", response_model=CreatedInboxResponse, status_code=201)
def create_inbox(req: CreateInboxRequest, service: InboxService = Depends(get_service)):

    inbox_id, signature = service.create_inbox(
        topic=req.topic,
        username=req.username,
        secret=req.secret,
        expires_at=req.expires_at,
        allow_anonymous=req.allow_anonymous,
    )
    return CreatedInboxResponse(id=inbox_id, signature=signature)


@router.get("/{inbox_id}", response_model=InboxPublicResponse)
def get_inbox_details(
    inbox_id: uuid.UUID,
    service: InboxService = Depends(get_service),
):
    inbox = service.get_inbox_metadata(inbox_id)
    return inbox


@router.post("/{inbox_id}/messages", status_code=201, response_class=Response)
def reply_to_inbox(
    inbox_id: uuid.UUID,
    req: ReplyRequest,
    service: InboxService = Depends(get_service),
):
    service.reply_to_inbox(
        inbox_id=inbox_id, body=req.body, username=req.username, secret=req.secret
    )


@router.patch("/{inbox_id}/topic", status_code=204, response_class=Response)
def change_topic(
    inbox_id: uuid.UUID,
    req: ChangeTopicRequest,
    x_username: str = Header(..., alias="X-username"),
    x_secret: str = Header(..., alias="X-secret"),
    service: InboxService = Depends(get_service),
):
    service.change_topic(
        inbox_id=inbox_id,
        new_topic=req.new_topic,
        username=x_username,
        secret=x_secret,
    )


@router.get("/{inbox_id}/messages", response_model=MessagesResponse)
def get_inbox_messages(
    inbox_id: uuid.UUID,
    x_username: str = Header(..., alias="X-username"),
    x_secret: str = Header(..., alias="X-secret"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: InboxService = Depends(get_service),
):
    messages = service.get_messages(
        inbox_id=inbox_id,
        username=x_username,
        secret=x_secret,
        page=page,
        page_size=page_size,
    )

    return MessagesResponse(messages=messages)


@router.get("/", response_model=InboxesResponse)
def search_inboxes(
    x_username: str = Header(..., alias="X-username"),
    x_secret: str = Header(..., alias="X-secret"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: InboxService = Depends(get_service),
):
    inboxes = service.list_user_inboxes(
        username=x_username,
        secret=x_secret,
        page=page,
        page_size=page_size,
    )
    return InboxesResponse(inboxes=inboxes)
