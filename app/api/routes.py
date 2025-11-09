"""API route handlers"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import whisper
import tempfile
import os
import subprocess
import mimetypes
import shutil

from app.api.models import (
    MatchRequest, MatchResponse, MatchResult, 
    MatchReason, HealthResponse,
    SnowflakeQueryRequest, SnowflakeVectorSearchRequest, SnowflakeTestResponse,
    TranscriptionResponse
)
from app.database import get_db
from app.mcp.tools import score_match, snowflake_query, snowflake_vector_search, summarize_content_for_ads
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


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_video(
    file: UploadFile = File(...),
    model_size: str = "base"  # Can be tiny, base, small, medium, or large
):
    """
    Transcribe a video file and extract relevant topics.
    Returns the transcription text, detected language, and potential ad topics.
    """
    # Validate file type
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
    
    # Check file extension as fallback
    if not content_type or not (content_type.startswith('video/') or content_type.startswith('audio/')):
        # Check by file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
        audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac']
        
        if file_ext in video_extensions:
            content_type = 'video/mp4'  # Default to mp4
        elif file_ext in audio_extensions:
            content_type = 'audio/mpeg'  # Default to audio
        else:
            raise HTTPException(
                status_code=400,
                detail=f"File must be a video or audio file. Got: {content_type or 'unknown'}, extension: {file_ext}"
            )
    
    logger.info(
        "transcription_requested", 
        filename=file.filename,
        content_type=content_type,
        model_size=model_size
    )
    
    try:
        # Load the Whisper model
        # Disable SSL verification for model download (hackathon/demo only)
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        model = whisper.load_model(model_size)
        
        # Create temp directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file
            input_path = os.path.join(temp_dir, "input" + os.path.splitext(file.filename)[1])
            audio_path = os.path.join(temp_dir, "audio.wav")
            
            with open(input_path, "wb") as input_file:
                content = await file.read()
                input_file.write(content)
            
            try:
                if content_type.startswith('video/'):
                    # Check if ffmpeg is available
                    if not shutil.which('ffmpeg'):
                        raise HTTPException(
                            status_code=500,
                            detail="FFmpeg is not installed. Please install FFmpeg to process video files."
                        )
                    
                    # Extract audio from video using ffmpeg
                    logger.info("extracting_audio", input_file=input_path)
                    try:
                        subprocess.run([
                            'ffmpeg', '-i', input_path,
                            '-vn',  # Disable video
                            '-acodec', 'pcm_s16le',  # Audio codec
                            '-ac', '1',  # Mono
                            '-ar', '16000',  # 16kHz sampling
                            '-y',  # Overwrite output
                            audio_path
                        ], check=True, capture_output=True, text=True)
                        transcription_input = audio_path
                    except subprocess.CalledProcessError as e:
                        logger.error("ffmpeg_error", error=str(e.stderr))
                        raise HTTPException(
                            status_code=500,
                            detail=f"Error processing video: {e.stderr}"
                        )
                else:
                    # For audio files, use directly
                    transcription_input = input_path
                
                # Transcribe the audio
                logger.info("starting_transcription")
                result = model.transcribe(transcription_input)
                
                # Extract potential topics (simple implementation)
                words = result["text"].lower().split()
                topics = list(set([word for word in words if len(word) > 5]))[:10]
                
                # Summarize content for ad matching
                logger.info("summarizing_content_for_ads")
                summary = await summarize_content_for_ads(result["text"])
                
                response = TranscriptionResponse(
                    text=result["text"],
                    language=result["language"],
                    duration=result.get("duration", 0.0),
                    segments=result["segments"],
                    topics=topics,
                    summary=summary
                )
                
                logger.info(
                    "transcription_completed",
                    language=result["language"],
                    duration=result.get("duration", 0.0)
                )
                
                return response 
                
            except Exception as e:
                logger.error("transcription_error", error=str(e), exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Transcription failed: {str(e)}"
                )
                
    except Exception as e:
        logger.error("transcription_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/video/process-and-match")
async def process_video_and_find_ads(
    file: UploadFile = File(...),
    model_size: str = "tiny",
    limit: int = 10,
    columns: Optional[List[str]] = None,
    filter_obj: Optional[Dict[str, Any]] = None
):
    """
    Complete workflow: Upload video → Transcribe → Summarize → Find matching ads → Return ranked results.
    
    Args:
        file: Video file to upload
        model_size: Whisper model size (tiny, base, small, medium, large)
        limit: Number of ads to return
        columns: Optional columns to return from Snowflake
        filter_obj: Optional filter object for Snowflake
        
    Returns:
        Dictionary with transcription, summary, and ranked ads
    """
    logger.info("process_video_and_find_ads_called", filename=file.filename, model_size=model_size, limit=limit)
    
    try:
        # Step 1: Transcribe the video
        logger.info("step_1_transcribing_video")
        transcription_response = await transcribe_video(file, model_size)
        transcript = transcription_response.text
        summary = transcription_response.summary
        
        if not summary:
            # Fallback: create summary if not included
            summary = await summarize_content_for_ads(transcript)
        
        # Step 2: Find matching ads using Cortex Search
        logger.info("step_2_finding_matching_ads")
        search_text = summary.get("embedding_query") or summary.get("query") or transcript[:200]
        
        # Default columns if not specified - include all metadata fields
        if not columns:
            columns = [
                "id", 
                "name", 
                "category", 
                "price", 
                "image_url", 
                "description",
                "company",
                "brand",
                "product",
                "product_name",
                "product_description",
                "manufacturer"
            ]
        
        ads = await snowflake_vector_search(
            text=search_text,
            k=limit,
            columns=columns,
            filter_obj=filter_obj
        )
        
        # Step 3: Rank ads (they should already be ranked by Cortex, but we can add additional scoring)
        logger.info("step_3_ranking_ads", ad_count=len(ads))
        
        # Add ranking metadata if scores are available
        ranked_ads = []
        for idx, ad in enumerate(ads):
            ranked_ad = {
                **ad,
                "rank": idx + 1,
                "relevance_score": ad.get("@score", ad.get("score", 1.0 - (idx * 0.1)))  # Use score if available
            }
            ranked_ads.append(ranked_ad)
        
        # Sort by relevance score (highest first)
        ranked_ads.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Re-assign ranks after sorting
        for idx, ad in enumerate(ranked_ads):
            ad["rank"] = idx + 1
        
        return {
            "success": True,
            "transcription": {
                "text": transcript,
                "language": transcription_response.language,
                "duration": transcription_response.duration,
                "topics": transcription_response.topics
            },
            "summary": summary,
            "query_used": search_text,
            "ads": ranked_ads,
            "count": len(ranked_ads),
            "metadata": {
                "model_size": model_size,
                "limit_requested": limit,
                "limit_returned": len(ranked_ads)
            }
        }
    except Exception as e:
        logger.error("process_video_and_find_ads_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process video and find ads: {str(e)}"
        )


@router.post("/transcribe/find-ads")
async def find_ads_from_transcript(
    transcript: str,
    limit: int = 5,
    columns: Optional[List[str]] = None,
    filter_obj: Optional[Dict[str, Any]] = None
):
    """
    Summarize transcript and find relevant ads using Cortex Search.
    
    Args:
        transcript: Content transcript text
        limit: Number of ads to return
        columns: Optional columns to return
        filter_obj: Optional filter object
        
    Returns:
        Dictionary with summary and matching ads
    """
    logger.info("find_ads_from_transcript_called", transcript_length=len(transcript), limit=limit)
    
    try:
        # Summarize the transcript
        summary = await summarize_content_for_ads(transcript)
        
        # Use embedding_query for better semantic search, fallback to query
        search_text = summary.get("embedding_query") or summary.get("query") or transcript[:200]
        
        # Default columns if not specified - include all metadata fields
        if not columns:
            columns = [
                "id", 
                "name", 
                "category", 
                "price", 
                "image_url", 
                "description",
                "company",
                "brand",
                "product",
                "product_name",
                "product_description",
                "manufacturer"
            ]
        
        # Search for relevant ads using Cortex
        ads = await snowflake_vector_search(
            text=search_text,
            k=limit,
            columns=columns,
            filter_obj=filter_obj
        )
        
        # Rank ads by relevance score
        ranked_ads = []
        for idx, ad in enumerate(ads):
            ranked_ad = {
                **ad,
                "rank": idx + 1,
                "relevance_score": ad.get("@score", ad.get("score", 1.0 - (idx * 0.1)))
            }
            ranked_ads.append(ranked_ad)
        
        ranked_ads.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        for idx, ad in enumerate(ranked_ads):
            ad["rank"] = idx + 1
        
        return {
            "summary": summary,
            "query_used": search_text,
            "ads": ranked_ads,
            "count": len(ranked_ads)
        }
    except Exception as e:
        logger.error("find_ads_from_transcript_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find ads: {str(e)}"
        )


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

