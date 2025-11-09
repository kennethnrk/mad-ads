"""Content-ad matching services"""

from typing import Any, Dict, Optional
from app.logging_config import get_logger

logger = get_logger(__name__)


async def score_match(content_id: str, ad_id: Optional[str] = None, ad_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate hybrid match score between content and ad.
    
    Args:
        content_id: Content item ID
        ad_id: Optional ad ID
        ad_text: Optional ad text for direct matching
        
    Returns:
        Match result with score and reasons
    """
    logger.info("score_match_called", content_id=content_id, ad_id=ad_id, has_ad_text=bool(ad_text))
    
    # Stub implementation
    result = {
        "score": 0.87,
        "reasons": {
            "overlap": ["fitness", "sustainability"],
            "cosine": 0.82,
            "demo_fit": 0.91
        }
    }
    
    logger.info("score_match_completed", score=result["score"])
    return result

