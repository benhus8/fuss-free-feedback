from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    DomainError,
    InboxExpiredError,
    TopicChangeNotAllowedError,
    InvalidSignatureError,
    AnonymousMessagesNotAllowedError,
)
from src.interface.schemas import ProblemDetails

EXCEPTION_MAPPING = {
    InboxExpiredError: (status.HTTP_410_GONE, "Inbox Expired"),
    TopicChangeNotAllowedError: (status.HTTP_409_CONFLICT, "State Conflict"),
    InvalidSignatureError: (status.HTTP_403_FORBIDDEN, "Invalid Credentials"),
    AnonymousMessagesNotAllowedError: (
        status.HTTP_403_FORBIDDEN,
        "Anonymity Forbidden",
    ),
}


async def domain_exception_handler(request: Request, exc: DomainError):
    http_status, title = EXCEPTION_MAPPING.get(
        type(exc), (status.HTTP_400_BAD_REQUEST, "Business Rule Violation")
    )

    problem = ProblemDetails(
        title=title, status=http_status, detail=str(exc), instance=str(request.url)
    )
    return JSONResponse(status_code=http_status, content=problem.model_dump())


async def unhandled_exception_handler(request: Request, exc: Exception):
    problem = ProblemDetails(
        title="Internal Server Error",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred.",
        instance=str(request.url),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=problem.model_dump()
    )
