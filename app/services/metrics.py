"""Metrics simulation services"""

from app.logging_config import get_logger

logger = get_logger(__name__)


async def metrics_simulate(campaign_id: str) -> str:
    """
    Start metrics simulation for a campaign.
    
    Args:
        campaign_id: Campaign ID to simulate
        
    Returns:
        Stream token for SSE connection
    """
    logger.info("metrics_simulate_called", campaign_id=campaign_id)
    
    # Stub implementation - returns mock token
    stream_token = f"stream_{campaign_id}_{hash(campaign_id)}"
    
    logger.info("metrics_simulate_completed", stream_token=stream_token)
    return stream_token

