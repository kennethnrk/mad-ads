"""Budget/media optimization services"""

from typing import Any, Dict, List
from app.logging_config import get_logger

logger = get_logger(__name__)


async def opt_plan(goal: str, variants: List[str], channels: List[str], budget: float) -> Dict[str, Any]:
    """
    Generate budget/media plan using optimization.
    
    Args:
        goal: Campaign goal (e.g., "maximize_clicks")
        variants: List of variant IDs
        channels: List of channel names
        budget: Total budget
        
    Returns:
        Plan with channel allocations
    """
    logger.info("opt_plan_called", goal=goal, variant_count=len(variants), channel_count=len(channels), budget=budget)
    
    # Stub implementation - simple rule-based allocation
    plan = {
        "plan": [
            {
                "channel": channels[0] if channels else "instagram",
                "variant_id": variants[0] if variants else None,
                "budget": budget * 0.6,
                "est_clicks": 5000,
                "reason": "Primary channel for target demographic"
            },
            {
                "channel": channels[1] if len(channels) > 1 else "google_ads",
                "variant_id": variants[1] if len(variants) > 1 else None,
                "budget": budget * 0.4,
                "est_clicks": 3000,
                "reason": "Secondary channel for broader reach"
            }
        ]
    }
    
    logger.info("opt_plan_completed", plan_items=len(plan["plan"]))
    return plan

