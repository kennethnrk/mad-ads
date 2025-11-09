"""API route handlers"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import whisper
import tempfile
import os
import subprocess
import mimetypes
import shutil

from app.api.models import (
    (
    MatchRequest, MatchResponse, MatchResult, 
    MatchReason, HealthResponse,
    SnowflakeQueryRequest, SnowflakeVectorSearchRequest, SnowflakeTestResponse
), TranscriptionResponse
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
    if not content_type or not (content_type.startswith('video/') or content_type.startswith('audio/')):
        raise HTTPException(
            status_code=400,
            detail="File must be a video or audio file"
        )
    
    logger.info(
        "transcription_requested", 
        filename=file.filename,
        content_type=content_type,
        model_size=model_size
    )
    
    try:
        # Load the Whisper model
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
                # TODO: Replace with proper NLP-based topic extraction
                words = result["text"].lower().split()
                topics = list(set([word for word in words if len(word) > 5]))[:10]
                
                response = TranscriptionResponse(
                    text=result["text"],
                    language=result["language"],
                    duration=result.get("duration", 0.0),
                    segments=result["segments"],
                    topics=topics
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

