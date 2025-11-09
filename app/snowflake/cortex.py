"""Snowflake Cortex Search functions"""

import json
from typing import Any, Dict, List
import requests
from app.config import settings
from app.logging_config import get_logger
from app.snowflake.connection import get_snowflake_connection

logger = get_logger(__name__)


def cortex_search_rest(query: str, columns=None, filter_obj=None, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Calls Snowflake Cortex Search using REST API.
    Returns a list of result dicts.
    """
    if not settings.snowflake_account_url or not settings.snowflake_pat:
        logger.warning("cortex_search_rest_missing_config", message="Using SQL fallback - REST API config missing")
        # Fallback to SQL method
        return cortex_search_preview_sql(query, columns, filter_obj, limit)
    
    url = f"{settings.snowflake_account_url}/api/v2/databases/{settings.snowflake_database}/{settings.snowflake_schema}/cortex-search-services/{settings.snowflake_cortex_service_name}:query"
    
    payload = {"query": query, "limit": limit}
    if columns:
        payload["columns"] = columns
    if filter_obj:
        payload["filter"] = filter_obj

    try:
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.snowflake_pat}",
                "Content-Type": "application/json"
            },
            data=json.dumps(payload),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as e:
        logger.error("cortex_search_rest_error", error=str(e), exc_info=True)
        # Fallback to SQL method
        logger.info("falling_back_to_sql_method")
        return cortex_search_preview_sql(query, columns, filter_obj, limit)


def cortex_search_preview_sql(query: str, columns=None, filter_obj=None, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Calls SNOWFLAKE.CORTEX.SEARCH_PREVIEW using SQL (fallback method).
    Returns a list of result dicts (already parsed from JSON).
    """
    conn = get_snowflake_connection()
    try:
        service_name = settings.snowflake_cortex_service_name
        payload = {
            "query": query,
            "limit": limit
        }
        if columns:
            payload["columns"] = columns
        if filter_obj:
            payload["filter"] = filter_obj

        sql = """
        SELECT PARSE_JSON(
          SNOWFLAKE.CORTEX.SEARCH_PREVIEW(%(svc)s, %(payload)s)
        )['results']
        """
        
        cs = conn.cursor()
        try:
            cs.execute(sql, {"svc": service_name, "payload": json.dumps(payload)})
            row = cs.fetchone()
            if row and row[0]:
                # Parse JSON if it's a string, otherwise use as-is
                if isinstance(row[0], str):
                    try:
                        results = json.loads(row[0])
                    except json.JSONDecodeError:
                        results = row[0]
                else:
                    results = row[0]
                # Ensure it's a list
                if not isinstance(results, list):
                    results = [results] if results else []
            else:
                results = []
            return results
        finally:
            cs.close()
    finally:
        conn.close()

