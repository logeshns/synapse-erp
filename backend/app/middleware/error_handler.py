import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import request_id_ctx_var
from app.exceptions import AppException

logger = logging.getLogger(__name__)


def _envelope(code: str, message: str) -> dict:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id_ctx_var.get(),
        },
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning("handled_exception code=%s message=%s", exc.code, exc.message)
        return JSONResponse(status_code=exc.status_code, content=_envelope(exc.code, exc.message))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_exception")
        return JSONResponse(
            status_code=500,
            content=_envelope("INTERNAL_ERROR", "Something went wrong. Please try again."),
        )