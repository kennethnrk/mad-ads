"""Snowflake query functions"""

from typing import Any, Dict, List, Optional
from app.logging_config import get_logger
from app.snowflake.connection import get_snowflake_connection
from app.snowflake.cortex import cortex_search_rest

logger = get_logger(__name__)


async def snowflake_query(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Query Snowflake for facts/metrics.
    
    Args:
        query: SQL query string
        params: Optional query parameters
        
    Returns:
        List of result dictionaries
    """
    logger.info("snowflake_query_called", query=query, params=params)
    
    try:
        conn = get_snowflake_connection()
        try:
            cs = conn.cursor()
            try:
                if params:
                    cs.execute(query, params)
                else:
                    cs.execute(query)
                
                # Fetch results and convert to list of dicts
                columns = [desc[0] for desc in cs.description] if cs.description else []
                rows = cs.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
                
                logger.info("snowflake_query_completed", result_count=len(results))
                return results
            finally:
                cs.close()
        finally:
            conn.close()
    except Exception as e:
        logger.error("snowflake_query_error", error=str(e), exc_info=True)
        # Fallback to mock data if connection fails
        logger.warning("falling_back_to_mock_data")
        return [
            {"id": "1", "fact": "Product is eco-friendly", "source": "product_catalog"},
            {"id": "2", "fact": "Target audience: 20-30 years", "source": "demographics"}
        ]


async def snowflake_vector_search(text: str, k: int = 5, columns: Optional[List[str]] = None, filter_obj: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Vector search using Snowflake Cortex REST API.
    
    Args:
        text: Query text
        k: Number of results to return
        columns: Optional list of columns to return
        filter_obj: Optional filter object
        
    Returns:
        List of similar content with scores
    """
    logger.info("snowflake_vector_search_called", text=text, k=k, has_columns=bool(columns), has_filter=bool(filter_obj))
    
    try:
        results = cortex_search_rest(
            query=text,
            columns=columns,
            filter_obj=filter_obj,
            limit=k
        )
        
        logger.info("snowflake_vector_search_completed", result_count=len(results))
        return results
    except Exception as e:
        logger.error("snowflake_vector_search_error", error=str(e), exc_info=True)
        # Fallback to mock data if connection fails
        logger.warning("falling_back_to_mock_data")
        return [
            {
                "id": "vec_1",
                "text": "Similar ad content about eco-friendly products",
                "score": 0.85,
                "metadata": {"category": "Gear"}
            },
            {
                "id": "vec_2", 
                "text": "Related marketing content for fitness enthusiasts",
                "score": 0.78,
                "metadata": {"category": "Snacks"}
            }
        ][:k]

