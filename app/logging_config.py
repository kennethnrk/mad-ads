"""Structured logging configuration with observability"""

import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict
import structlog
from structlog.types import Processor

# Request ID context variable
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def add_request_id(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add request ID to log events"""
    request_id = request_id_var.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging with JSON output"""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_request_id,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


def set_request_id(request_id: str) -> None:
    """Set the current request ID in context"""
    request_id_var.set(request_id)


def get_request_id() -> str:
    """Get the current request ID"""
    return request_id_var.get()


def generate_request_id() -> str:
    """Generate a new request ID"""
    return str(uuid.uuid4())


class RequestTimingMiddleware:
    """Middleware to track request timing and log requests/responses"""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("http")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request_id = generate_request_id()
        set_request_id(request_id)
        
        start_time = time.time()
        path = scope.get("path", "")
        method = scope.get("method", "")
        
        # Log request
        self.logger.info(
            "incoming_request",
            request_id=request_id,
            method=method,
            path=path,
            client=scope.get("client", [None, None])[0] if scope.get("client") else None
        )
        
        # Track response status
        status_code = 200
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            status_code = 500
            elapsed = time.time() - start_time
            self.logger.error(
                "request_error",
                request_id=request_id,
                method=method,
                path=path,
                status_code=status_code,
                elapsed_ms=round(elapsed * 1000, 2),
                error=str(e),
                exc_info=True
            )
            raise
        finally:
            elapsed = time.time() - start_time
            self.logger.info(
                "request_completed",
                request_id=request_id,
                method=method,
                path=path,
                status_code=status_code,
                elapsed_ms=round(elapsed * 1000, 2)
            )

