import uuid
from fastapi import APIRouter, Depends, Response, Query
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
    Credentials,
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


@router.post("/{inbox_id}/messages", status_code=201, response_class=Response)
def reply_to_inbox(
    inbox_id: uuid.UUID, req: ReplyRequest, service: InboxService = Depends(get_service)
):
    service.reply_to_inbox(
        inbox_id=inbox_id, body=req.body, username=req.username, secret=req.secret
    )


@router.patch("/{inbox_id}/topic")
def change_topic(
    inbox_id: uuid.UUID,
    req: ChangeTopicRequest,
    service: InboxService = Depends(get_service),
):
    result = service.change_topic(
        inbox_id=inbox_id,
        new_topic=req.new_topic,
        username=req.username,
        secret=req.secret,
    )

    if result is None:
        return JSONResponse(status_code=404, content={"detail": "Inbox not found"})


@router.post("/{inbox_id}/messages/read", response_model=MessagesResponse)
def get_inbox_messages(
    inbox_id: uuid.UUID,
    request: Credentials,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: InboxService = Depends(get_service),
):
    messages = service.get_messages(
        inbox_id=inbox_id,
        username=request.username,
        secret=request.secret,
        page=page,
        page_size=page_size,
    )

    return MessagesResponse(messages=messages)


@router.post("/search", response_model=InboxesResponse)
def search_inboxes(
    req: Credentials,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: InboxService = Depends(get_service),
):
    inboxes = service.list_user_inboxes(
        username=req.username,
        secret=req.secret,
        page=page,
        page_size=page_size,
    )
    return InboxesResponse(inboxes=inboxes)
