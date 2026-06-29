from fastapi import Request
from fastapi.responses import JSONResponse

from bestiaux.core.exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)


async def authentication_handler(_request: Request, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def conflict_handler(_request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def forbidden_handler(_request: Request, exc: ForbiddenError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})
