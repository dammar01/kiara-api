from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.settings import settings


class InternalAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("X-Internal-Token")
        if token != settings.INTERNAL_AUTH_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized request origin")
        return await call_next(request)
