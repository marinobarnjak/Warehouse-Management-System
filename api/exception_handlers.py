from fastapi import Request
from fastapi.responses import JSONResponse
from exceptions.business import NotFoundError, ValidationError, ConflictError
from sqlalchemy.exc import IntegrityError

async def not_found_handler(request: Request, exc: NotFoundError):

    return JSONResponse(content={"detail": str(exc)}, status_code=404)

async def validation_handler(request: Request, exc: ValidationError):

    return JSONResponse(content={"detail": str(exc)}, status_code=400)

async def conflict_handler(request: Request, exc: ConflictError):

    return JSONResponse(content={"detail": str(exc)}, status_code=409)

async def integrity_error_handler(request: Request, exc: IntegrityError):

    code = exc.orig.sqlstate

    if code == "23505": 
        return JSONResponse(content={"detail": "Resource already exist"}, status_code=409)

    if code == "23503":
        return JSONResponse(content={"detail": "Foreign key constraint violation"}, status_code=409)

    return JSONResponse(content={"detail": "Internal database error"}, status_code=500)

