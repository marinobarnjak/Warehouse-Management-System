from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions.business import NotFoundError, ValidationError, ConflictError

async def not_found_handler(request: Request, exc: NotFoundError):

    return JSONResponse(content={"detail": str(exc)}, status_code=404)

async def validation_handler(request: Request, exc: ValidationError):

    return JSONResponse(content={"detail": str(exc)}, status_code=400)

async def conflict_handler(request: Request, exc: ConflictError):

    return JSONResponse(content={"detail": str(exc)}, status_code=409)