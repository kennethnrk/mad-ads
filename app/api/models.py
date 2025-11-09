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


# Company onboarding models
class CompanyCreateRequest(BaseModel):
    """Request for creating a new company"""
    name: str = Field(..., description="Company name")
    description: Optional[str] = Field(None, description="Company description")
    industry: Optional[str] = Field(None, description="Industry category")
    website: Optional[str] = Field(None, description="Company website URL")
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    target_audience: Optional[Dict[str, Any]] = Field(None, description="Target audience characteristics")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CompanyResponse(BaseModel):
    """Response for company operations"""
    id: str
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    logo_url: Optional[str] = None
    brand_voice: Optional[str] = None
    company_summary: Optional[str] = None
    target_audience: Optional[Dict[str, Any]] = None
    brand_keywords: Optional[List[str]] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CompanyUpdateRequest(BaseModel):
    """Request for updating a company"""
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    target_audience: Optional[Dict[str, Any]] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


# Product onboarding models
class ProductCreateRequest(BaseModel):
    """Request for creating a new product"""
    company_id: str = Field(..., description="Company ID that owns this product")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Optional[float] = Field(None, description="Product price")
    currency: Optional[str] = Field("USD", description="Currency code")
    category: Optional[str] = Field(None, description="Product category")
    ad_phrases: Optional[List[str]] = Field(None, description="Ad phrases for matching")
    use_cases: Optional[List[str]] = Field(None, description="Use cases for this product")
    features: Optional[List[str]] = Field(None, description="Product features")
    target_audience: Optional[Dict[str, Any]] = Field(None, description="Target audience")
    pain_points: Optional[List[str]] = Field(None, description="Pain points addressed")
    keywords: Optional[List[str]] = Field(None, description="Product keywords")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ProductResponse(BaseModel):
    """Response for product operations"""
    id: str
    company_id: str
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    currency: str
    category: Optional[str] = None
    image_urls: Optional[List[str]] = None
    embedded_text: Optional[str] = None
    ad_phrases: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    product_summary: Optional[str] = None
    features: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None
    pain_points: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductUpdateRequest(BaseModel):
    """Request for updating a product"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    ad_phrases: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    features: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None
    pain_points: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ImageUploadResponse(BaseModel):
    """Response for image upload"""
    image_url: str
    storage_id: Optional[str] = None
    message: str = "Image uploaded successfully"