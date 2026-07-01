from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from bestiaux.auth.router import router as auth_router
from bestiaux.breeding.router import router as breeding_router
from bestiaux.config import settings
from bestiaux.core.exception_handlers import (
    authentication_handler,
    conflict_handler,
    forbidden_handler,
    not_found_handler,
)
from bestiaux.core.exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from bestiaux.creature.router import router as creature_router

app = FastAPI(title="Bestiaux API", version="0.1.0")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    max_age=settings.session_max_age_seconds,
    https_only=False,
    same_site="lax",
)

app.add_exception_handler(AuthenticationError, authentication_handler)
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(ConflictError, conflict_handler)
app.add_exception_handler(ForbiddenError, forbidden_handler)

app.include_router(auth_router)
app.include_router(creature_router)
app.include_router(breeding_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
