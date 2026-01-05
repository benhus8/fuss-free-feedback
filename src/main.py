from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.config import settings
from src.interface.dependencies import engine
from src.interface.api import inboxes
from src.interface.schemas import ProblemDetails
from src.interface.exception_handlers import (
    DomainError,
    domain_exception_handler,
    unhandled_exception_handler,
)


app = FastAPI(
    title="Fuss-Free Feedback API",
    version="1.0.0",
)

app.include_router(inboxes.router, prefix=f"/api/{settings.API_VERSION}")

app.add_exception_handler(DomainError, domain_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)