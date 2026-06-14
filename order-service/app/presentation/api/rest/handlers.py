import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.application.use_cases.order_usecases.exceptions import (
    IdempotencyKeyExistException,
    ItemNotEnoughException,
)

logger = logging.getLogger(__name__)


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    try:
        body = await request.body()
        logger.error(
            "Validation error for %s %s. Body: %s, Errors: %s",
            request.method,
            request.url,
            body.decode("utf-8", errors="ignore"),
            exc.errors(),
        )
    except Exception:
        logger.error(
            "Validation error for %s %s. Errors: %s",
            request.method,
            request.url,
            exc.errors(),
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )


async def item_not_enough_handler(
    request: Request,
    exc: ItemNotEnoughException,
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def idempotency_key_conflict_handler(
    request: Request,
    exc: IdempotencyKeyExistException,
):
    logger.warning("Idempotency key conflict: %s", str(exc))
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Idempotency key already used"},
    )


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
):
    logger.error("Database integrity error: %s", str(exc))
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Duplicate key violation"},
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception("Unhandled exception occurred: %s", str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


handlers_mapping = {
    RequestValidationError: validation_error_handler,
    ItemNotEnoughException: item_not_enough_handler,
    IdempotencyKeyExistException: idempotency_key_conflict_handler,
    IntegrityError: integrity_error_handler,
    Exception: general_exception_handler,
}
