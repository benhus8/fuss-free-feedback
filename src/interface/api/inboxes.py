import uuid
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.interface.dependencies import get_service
from src.application.services.inbox import InboxService
from src.interface.schemas import (
    CreateInboxRequest, ReplyRequest, ChangeTopicRequest,
    CreatedInboxResponse, InboxPublicResponse
)

router = APIRouter(tags=["Inboxes"])

@router.post("/inboxes", response_model=CreatedInboxResponse, status_code=201)
def create_inbox(
    req: CreateInboxRequest, 
    service: InboxService = Depends(get_service)
):

    inbox_id, signature = service.create_inbox(
        topic=req.topic,
        username=req.username,
        secret=req.secret,
        expires_at=req.expires_at,
        allow_anonymous=req.allow_anonymous
    )
    return CreatedInboxResponse(id=inbox_id, tripcode=signature)

@router.get("/inboxes/{inbox_id}", response_model=InboxPublicResponse)
def get_inbox(
    inbox_id: uuid.UUID, 
    service: InboxService = Depends(get_service)
):
    inbox = service.get_inbox(inbox_id)
    if not inbox:
        return JSONResponse(status_code=404, content={"detail": "Inbox not found"})
    return inbox

@router.post("/inboxes/{inbox_id}/messages", status_code=201)
def reply_to_inbox(
    inbox_id: uuid.UUID, 
    req: ReplyRequest, 
    service: InboxService = Depends(get_service)
):
    result = service.reply_to_inbox(
        inbox_id=inbox_id,
        body=req.body,
        username=req.username,
        secret=req.secret
    )
    
    if result is None:
         return JSONResponse(status_code=404, content={"detail": "Inbox not found"})
         
    return {"message": "Reply sent"}

@router.patch("/inboxes/{inbox_id}/topic")
def change_topic(
    inbox_id: uuid.UUID,
    req: ChangeTopicRequest,
    service: InboxService = Depends(get_service)
):
    result = service.change_topic(
        inbox_id=inbox_id,
        new_topic=req.new_topic,
        username=req.username,
        secret=req.secret
    )
    
    if result is None:
        return JSONResponse(status_code=404, content={"detail": "Inbox not found"})

    return {"message": "Topic updated"}