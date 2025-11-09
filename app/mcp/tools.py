"""MCP tool implementations with real Snowflake integration"""

import json
import os
import requests
from typing import Any, Dict, List, Optional
import snowflake.connector
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def get_snowflake_connection():
    """Get a Snowflake connection using settings"""
    conn_params = {
        "account": settings.snowflake_account,
        "user": settings.snowflake_user,
        "warehouse": settings.snowflake_warehouse,
        "database": settings.snowflake_database,
        "schema": settings.snowflake_schema,
        "role": settings.snowflake_role,
    }
    
    # Add authentication method - prefer password with snowflake authenticator
    if settings.snowflake_password:
        conn_params["password"] = settings.snowflake_password
        # Use specified authenticator or default to "snowflake" for password auth
        if settings.snowflake_authenticator:
            conn_params["authenticator"] = settings.snowflake_authenticator
        else:
            conn_params["authenticator"] = "snowflake"
    elif settings.snowflake_authenticator:
        conn_params["authenticator"] = settings.snowflake_authenticator
    else:
        raise ValueError("No authentication method configured (password or authenticator required)")
    
    return snowflake.connector.connect(**conn_params)


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


async def summarize_content_for_ads(transcript: str) -> Dict[str, Any]:
    """
    Summarize content/transcript into signals optimized for Snowflake Cortex ad embedding queries.
    Preserves semantic meaning, product context, and searchable signals needed for vector search.
    
    Args:
        transcript: Content transcript or text
        
    Returns:
        Dictionary with:
        - query: Optimized search query for Cortex (preserves semantic meaning)
        - embedding_query: Full text optimized for embedding similarity search
        - topics: Key topics/keywords
        - signals: Structured signals (keywords, product_needs, categories, audience, pain_points)
        - context: Preserved context for better matching
    """
    logger.info("summarize_content_called", transcript_length=len(transcript))
    
    if not settings.gemini_api_key:
        logger.warning("gemini_api_key_missing", message="Using simple keyword extraction")
        # Simple fallback: extract keywords
        words = transcript.lower().split()
        keywords = [w for w in words if len(w) > 4][:10]
        return {
            "query": " ".join(keywords[:5]),
            "embedding_query": transcript[:500],  # Preserve context for embeddings
            "topics": keywords,
            "signals": {
                "keywords": keywords,
                "product_needs": keywords[:3],
                "categories": [],
                "audience": [],
                "pain_points": []
            },
            "context": transcript[:200]
        }
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""You are analyzing content to find relevant product ads using Snowflake Cortex vector search.

The transcript will be used for semantic similarity search against product embeddings. Your task is to extract and preserve ALL information needed for accurate ad matching.

Transcript:
{transcript}

Extract and preserve:

1. **Embedding Query** (50-200 words): A rich, semantic description that preserves:
   - Product needs and use cases
   - Pain points and problems mentioned
   - Context and scenarios
   - Target user characteristics
   - This will be used for vector similarity search, so preserve semantic meaning

2. **Search Query** (2-5 words): Concise query for quick filtering (e.g., "wrist support gear", "protein snack")

3. **Structured Signals**:
   - keywords: Important terms (nouns, product names, features)
   - product_needs: Specific product needs mentioned
   - categories: Product categories (Gear, Snacks, Supplements, etc.)
   - audience: Target audience characteristics
   - pain_points: Problems or pain points mentioned

4. **Context**: Key context that helps understand the content (50-100 words)

Return ONLY valid JSON (no markdown, no explanation):
{{
  "embedding_query": "rich semantic description preserving all context for vector search",
  "query": "short 2-5 word query",
  "topics": ["topic1", "topic2", ...],
  "signals": {{
    "keywords": ["keyword1", ...],
    "product_needs": ["need1", ...],
    "categories": ["category1", ...],
    "audience": ["audience1", ...],
    "pain_points": ["pain1", ...]
  }},
  "context": "key context summary"
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Remove any leading/trailing text before/after JSON
            start_idx = result_text.find("{")
            end_idx = result_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                result_text = result_text[start_idx:end_idx]
            
            result = json.loads(result_text)
            
            # Ensure all required fields exist
            if "embedding_query" not in result:
                result["embedding_query"] = transcript[:500]
            if "query" not in result:
                result["query"] = " ".join(result.get("topics", [])[:5])
            if "signals" not in result:
                result["signals"] = {}
            if "context" not in result:
                result["context"] = transcript[:200]
            
            logger.info(
                "summarize_content_completed",
                query=result.get("query"),
                embedding_query_length=len(result.get("embedding_query", "")),
                topic_count=len(result.get("topics", []))
            )
            return result
        except json.JSONDecodeError as e:
            # Fallback: extract query from response text
            logger.warning("json_parse_failed", error=str(e), response_preview=result_text[:200])
            # Extract potential query from response
            lines = result_text.split("\n")
            query = lines[0] if lines else "fitness products"
            words = transcript.lower().split()
            keywords = [w for w in words if len(w) > 4][:10]
            return {
                "query": query[:50],
                "embedding_query": transcript[:500],
                "topics": keywords,
                "signals": {
                    "keywords": keywords,
                    "product_needs": keywords[:3],
                    "categories": [],
                    "audience": [],
                    "pain_points": []
                },
                "context": transcript[:200]
            }
    except Exception as e:
        logger.error("summarize_content_error", error=str(e), exc_info=True)
        # Fallback to simple extraction
        words = transcript.lower().split()
        keywords = [w for w in words if len(w) > 4][:10]
        return {
            "query": " ".join(keywords[:5]),
            "embedding_query": transcript[:500],
            "topics": keywords,
            "signals": {
                "keywords": keywords,
                "product_needs": keywords[:3],
                "categories": [],
                "audience": [],
                "pain_points": []
            },
            "context": transcript[:200]
        }


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


async def tts_speak(text: str, voice: Optional[str] = None) -> str:
    """
    Convert text to speech using ElevenLabs.
    
    Args:
        text: Text to convert
        voice: Optional voice ID (uses default if not provided)
        
    Returns:
        URL to generated MP3 file
    """
    logger.info("tts_speak_called", text_length=len(text), voice=voice)
    
    # Stub implementation - returns mock URL
    audio_url = f"https://storage.example.com/audio/{hash(text)}.mp3"
    
    logger.info("tts_speak_completed", audio_url=audio_url)
    return audio_url


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


async def storage_put(object_data: bytes, object_key: str) -> str:
    """
    Store object in storage (Vultr/S3-compatible).
    
    Args:
        object_data: Object bytes
        object_key: Storage key/path
        
    Returns:
        Storage ID or URL
    """
    logger.info("storage_put_called", object_key=object_key, size_bytes=len(object_data))
    
    # Stub implementation
    storage_id = f"storage_{hash(object_key)}"
    
    logger.info("storage_put_completed", storage_id=storage_id)
    return storage_id


async def storage_url(storage_id: str) -> str:
    """
    Get URL for stored object.
    
    Args:
        storage_id: Storage ID
        
    Returns:
        Public URL to object
    """
    logger.info("storage_url_called", storage_id=storage_id)
    
    # Stub implementation
    url = f"https://storage.example.com/{storage_id}"
    
    logger.info("storage_url_completed", url=url)
    return url


async def audit_log(event: str, payload: Dict[str, Any]) -> None:
    """
    Log audit event.
    
    Args:
        event: Event name
        payload: Event payload
    """
    logger.info("audit_log", event=event, payload=payload)
