"""Pydantic models for API request/response contracts"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import UploadFile


# Match endpoint models
class MatchRequest(BaseModel):
    """Request for matching content to ads"""
    content_id: str = Field(..., description="Content item ID")
    ad_pool_id: Optional[str] = Field(None, description="Optional ad pool ID to filter")
    brief: Optional[str] = Field(None, description="Optional brief/goals")
    limit: int = Field(5, ge=1, le=50, description="Number of results to return")


class MatchReason(BaseModel):
    """Match reason breakdown"""
    overlap: List[str] = Field(default_factory=list, description="Overlapping tags")
    cosine: float = Field(..., description="Cosine similarity score")
    demo_fit: float = Field(..., description="Demographic fit score")


class MatchResult(BaseModel):
    """Single match result"""
    ad_id: str
    score: float = Field(..., ge=0.0, le=1.0, description="Match score")
    why: MatchReason


class MatchResponse(BaseModel):
    """Response for match endpoint"""
    top_k: List[MatchResult]


# Health endpoint models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "0.1.0"


# Snowflake test endpoint models
class SnowflakeQueryRequest(BaseModel):
    """Request for Snowflake query test"""
    query: str = Field(..., description="SQL query to execute")
    params: Optional[Dict[str, Any]] = Field(None, description="Query parameters")


class SnowflakeVectorSearchRequest(BaseModel):
    """Request for Snowflake vector search test"""
    text: str = Field(..., description="Search query text")
    k: int = Field(5, ge=1, le=50, description="Number of results")
    columns: Optional[List[str]] = Field(None, description="Columns to return")
    filter_obj: Optional[Dict[str, Any]] = Field(None, description="Filter object")


class SnowflakeTestResponse(BaseModel):
    """Response for Snowflake test endpoints"""
    success: bool
    results: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
# Transcription endpoint models
class TranscriptionResponse(BaseModel):
    """Response for transcription endpoint"""
    text: str
    language: str
    duration: float
    segments: List[Dict[str, Any]] = Field(
        description="List of transcribed segments with timestamps"
    )
    topics: List[str] = Field(
        default_factory=list,
        description="Extracted topics from the transcription"
    )
    summary: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Summary signals for finding relevant ads (query, topics, signals)"
    )

