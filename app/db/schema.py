"""SQLAlchemy database models matching outline data contracts"""

from sqlalchemy import (
    Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Ad(Base):
    """Ad model - represents buyer-uploaded ads"""
    __tablename__ = "ads"
    
    id = Column(String, primary_key=True)
    owner_id = Column(String, nullable=False, index=True)
    primary_text = Column(Text, nullable=False)
    tags = Column(JSON, default=list)  # List of tag strings
    product_facts = Column(JSON, default=dict)  # Dict of product facts
    target_demo = Column(JSON, default=dict)  # Dict of demographic targeting
    assets = Column(JSON, default=dict)  # Dict with image?, video? keys
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ContentItem(Base):
    """Content model - represents creator content/posts"""
    __tablename__ = "content_items"
    
    id = Column(String, primary_key=True)
    creator_id = Column(String, nullable=False, index=True)
    text = Column(Text)  # Transcript or text content
    transcript = Column(Text)  # Alternative transcript field
    tags = Column(JSON, default=list)  # List of tag strings
    audience_estimate = Column(JSON, default=dict)  # Dict of audience estimates
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MatchResult(Base):
    """Match result - stores matching scores between content and ads"""
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String, ForeignKey("content_items.id"), nullable=False, index=True)
    ad_id = Column(String, ForeignKey("ads.id"), nullable=False, index=True)
    score = Column(Float, nullable=False, index=True)
    reasons = Column(JSON, default=dict)  # Dict with overlap[], cosine, demo_fit
    created_at = Column(DateTime, server_default=func.now())


class Campaign(Base):
    """Campaign model - ties matches, plan, and assets together"""
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True)
    content_id = Column(String, ForeignKey("content_items.id"), nullable=False)
    ad_id = Column(String, ForeignKey("ads.id"), nullable=False)
    status = Column(String, default="draft")  # draft, active, completed
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class CreativeVariant(Base):
    """Creative variant - generated ad copy variants"""
    __tablename__ = "creative_variants"
    
    id = Column(String, primary_key=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    channel = Column(String, nullable=False)  # e.g., "twitter", "facebook", "email"
    headline = Column(Text)
    body = Column(Text)
    cta = Column(String)  # Call-to-action text
    script15s = Column(Text)  # 15-second script for audio
    created_at = Column(DateTime, server_default=func.now())


class AudioAsset(Base):
    """Audio asset - TTS-generated audio files"""
    __tablename__ = "audio_assets"
    
    id = Column(String, primary_key=True)
    variant_id = Column(String, ForeignKey("creative_variants.id"), nullable=False, index=True)
    voice = Column(String, nullable=False)  # Voice ID used
    url = Column(String, nullable=False)  # URL to audio file
    duration = Column(Float)  # Duration in seconds
    created_at = Column(DateTime, server_default=func.now())


class Plan(Base):
    """Budget plan - channel allocation and strategy"""
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    channel = Column(String, nullable=False)
    variant_id = Column(String, ForeignKey("creative_variants.id"), nullable=True)
    budget = Column(Float, nullable=False)
    est_clicks = Column(Float)
    note = Column(Text)  # Rationale for allocation
    created_at = Column(DateTime, server_default=func.now())


class Event(Base):
    """Metrics event - fake live metrics for demo"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    channel = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # impression, click, conv
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    event_data = Column(JSON, default=dict)  # Additional event data (renamed from metadata to avoid SQLAlchemy conflict)

