from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.config import settings
from src.interface.api import inboxes
from src.interface.exception_handlers import (
    DomainError,
    domain_exception_handler,
    unhandled_exception_handler,
)
from src.infrastructure.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


app = FastAPI(title="Fuss-Free Feedback API", version="1.0.0", lifespan=lifespan)

app.include_router(inboxes.router, prefix=f"/api/{settings.API_VERSION}")

app.add_exception_handler(DomainError, domain_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
