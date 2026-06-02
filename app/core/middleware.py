import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        logger.info(
            f"Request started | method={request.method} | "
            f"path={request.url.path} | correlation_id={correlation_id}"
            )
        
        response = await call_next(request)

        response.headers["X-Correlation-ID"] = correlation_id

        logger.info(
            f"Request completed | method={request.method} | "
            f"path={request.url.path} | status={response.status_code} | "
            f"correlation_id={correlation_id}"
        )

        return response