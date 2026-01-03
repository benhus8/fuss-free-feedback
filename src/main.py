from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.config import settings
from src.interface.dependencies import engine
from src.interface.api import inboxes
from src.interface.schemas import ProblemDetails
from src.interface.exception_handlers import (
    DomainError,
    EXCEPTION_MAPPING,
)


app = FastAPI(
    title="Fuss-Free Feedback API",
    version="1.0.0",
)

app.include_router(inboxes.router, prefix=f"/api/{settings.API_VERSION}")


@app.exception_handler(DomainError)
async def domain_exception_handler(request: Request, exc: DomainError):
    http_status, title = EXCEPTION_MAPPING.get(
        type(exc), (status.HTTP_400_BAD_REQUEST, "Business Rule Violation")
    )
    problem = ProblemDetails(
        title=title, status=http_status, detail=str(exc), instance=str(request.url)
    )
    return JSONResponse(status_code=http_status, content=problem.model_dump())
