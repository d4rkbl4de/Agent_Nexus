import jwt
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from common.config.settings import settings
from common.config.logging import logger
from tracing.context import get_trace_id

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str = settings.SECRET_KEY, algorithm: str = "HS256"):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.exclude_paths = ["/api/v1/health", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        trace_id = get_trace_id()

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.error(f"Unauthorized access attempt: Missing token | TraceID: {trace_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing authentication credentials"
            )

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            user_id = payload.get("sub")
            if not user_id:
                raise jwt.InvalidTokenError("Subject missing in payload")
            
            request.state.user = payload
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"Auth Failure: Token Expired | TraceID: {trace_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Auth Failure: Invalid Token: {str(e)} | TraceID: {trace_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authentication token"
            )

        return await call_next(request)