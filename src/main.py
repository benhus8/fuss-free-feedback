from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from src.interface.dependencies import engine
from src.interface.api import inboxes  
from src.interface.schemas import ProblemDetails
from src.domain.exceptions import (
    DomainError, InboxExpiredError, TopicChangeNotAllowedError,
    InvalidSignatureError, AnonymousMessagesNotAllowedError
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(
    title="Fuss-Free Feedback API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(inboxes.router) 

EXCEPTION_MAPPING = {
    InboxExpiredError: (status.HTTP_410_GONE, "Inbox Expired"),
    TopicChangeNotAllowedError: (status.HTTP_409_CONFLICT, "State Conflict"),
    InvalidSignatureError: (status.HTTP_403_FORBIDDEN, "Invalid Credentials"),
    AnonymousMessagesNotAllowedError: (status.HTTP_403_FORBIDDEN, "Anonymity Forbidden"),
}

@app.exception_handler(DomainError)
async def domain_exception_handler(request: Request, exc: DomainError):
    http_status, title = EXCEPTION_MAPPING.get(type(exc), (status.HTTP_400_BAD_REQUEST, "Business Rule Violation"))
    problem = ProblemDetails(
        title=title, status=http_status, detail=str(exc), instance=str(request.url)
    )
    return JSONResponse(status_code=http_status, content=problem.model_dump())