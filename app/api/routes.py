"""API route handlers"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.models import (
    MatchRequest, MatchResponse, MatchResult, MatchReason, HealthResponse,
    SnowflakeQueryRequest, SnowflakeVectorSearchRequest, SnowflakeTestResponse
)
from app.database import get_db
from app.mcp.tools import score_match, snowflake_query, snowflake_vector_search
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("health_check_requested")
    return HealthResponse(status="healthy")


@router.post("/match", response_model=MatchResponse)
async def match_content_to_ads(
    request: MatchRequest,
    db: Session = Depends(get_db)
):
    """
    Match creator content to ads.
    
    Returns top-k matches with scores and reasons.
    """
    logger.info(
        "match_request",
        content_id=request.content_id,
        ad_pool_id=request.ad_pool_id,
        limit=request.limit
    )
    
    try:
        # Stub implementation - returns mock matches
        # In real implementation, would query database and use MCP tools
        
        mock_matches = [
            MatchResult(
                ad_id="ad_1",
                score=0.87,
                why=MatchReason(
                    overlap=["fitness", "sustainability", "eco-friendly"],
                    cosine=0.82,
                    demo_fit=0.91
                )
            ),
            MatchResult(
                ad_id="ad_2",
                score=0.75,
                why=MatchReason(
                    overlap=["fitness", "health"],
                    cosine=0.71,
                    demo_fit=0.78
                )
            ),
            MatchResult(
                ad_id="ad_3",
                score=0.68,
                why=MatchReason(
                    overlap=["sustainability"],
                    cosine=0.65,
                    demo_fit=0.72
                )
            )
        ][:request.limit]
        
        logger.info("match_completed", result_count=len(mock_matches))
        
        return MatchResponse(top_k=mock_matches)
    
    except Exception as e:
        logger.error("match_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Match failed: {str(e)}")


@router.post("/snowflake/query", response_model=SnowflakeTestResponse)
async def test_snowflake_query(request: SnowflakeQueryRequest):
    """Test Snowflake query execution"""
    logger.info("snowflake_query_test", query=request.query)
    
    try:
        results = await snowflake_query(request.query, request.params)
        return SnowflakeTestResponse(success=True, results=results)
    except Exception as e:
        logger.error("snowflake_query_test_error", error=str(e), exc_info=True)
        return SnowflakeTestResponse(success=False, error=str(e))


@router.post("/snowflake/vector-search", response_model=SnowflakeTestResponse)
async def test_snowflake_vector_search(request: SnowflakeVectorSearchRequest):
    """Test Snowflake Cortex vector search"""
    logger.info("snowflake_vector_search_test", text=request.text, k=request.k)
    
    try:
        results = await snowflake_vector_search(request.text, request.k)
        return SnowflakeTestResponse(success=True, results=results)
    except Exception as e:
        logger.error("snowflake_vector_search_test_error", error=str(e), exc_info=True)
        return SnowflakeTestResponse(success=False, error=str(e))

