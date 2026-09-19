import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import request_id_ctx_var

access_logger = logging.getLogger("synapse.access")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        incoming_id = request.headers.get("X-Request-ID")
        request_id = incoming_id or f"req_{uuid.uuid4().hex[:12]}"

        token = request_id_ctx_var.set(request_id)
        start = time.monotonic()
        try:
            response = await call_next(request)
        finally:
            request_id_ctx_var.reset(token)

        duration_ms = round((time.monotonic() - start) * 1000, 1)
        access_logger.info(
            "%s %s status=%s duration_ms=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        response.headers["X-Request-ID"] = request_id
        return response