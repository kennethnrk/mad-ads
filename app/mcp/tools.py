"""MCP tool implementations - thin wrappers that delegate to service modules"""

from app.snowflake.queries import snowflake_query, snowflake_vector_search
from app.services import (
    summarize_content_for_ads,
    score_match,
    tts_speak,
    opt_plan,
    metrics_simulate,
    storage_put,
    storage_url,
    audit_log,
)

# Re-export functions for MCP server compatibility
__all__ = [
    "snowflake_query",
    "snowflake_vector_search",
    "summarize_content_for_ads",
    "score_match",
    "tts_speak",
    "opt_plan",
    "metrics_simulate",
    "storage_put",
    "storage_url",
    "audit_log",
]
