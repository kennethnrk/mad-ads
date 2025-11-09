"""Audit logging services"""

from typing import Any, Dict
from app.logging_config import get_logger

logger = get_logger(__name__)


async def audit_log(event: str, payload: Dict[str, Any]) -> None:
    """
    Log audit event.
    
    Args:
        event: Event name
        payload: Event payload
    """
    logger.info("audit_log", event=event, payload=payload)

