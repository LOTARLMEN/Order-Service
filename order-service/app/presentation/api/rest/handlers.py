from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.infrastructure.db.repositories.order.exceptions import ItemNotEnoughException


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )


async def not_item_error_handler(
    request: Request,
    exc: ItemNotEnoughException,
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc}
    )
