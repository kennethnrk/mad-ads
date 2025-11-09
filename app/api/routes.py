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
    TranscriptionResponse,
    CompanyCreateRequest, CompanyResponse, CompanyUpdateRequest,
    ProductCreateRequest, ProductResponse, ProductUpdateRequest,
    ImageUploadResponse
)
from app.database import get_db
from app.db.schema import Company, Product
from app.services.matching import score_match
from app.services.ai import summarize_content_for_ads
from app.snowflake.queries import snowflake_query, snowflake_vector_search
from app.services.storage import storage_put, storage_url
from app.services.content_generator import generate_company_content, generate_product_content
from app.logging_config import get_logger
import uuid
from datetime import datetime

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
                logger.info("summarizing_content_for_ads", 
                           transcript_length=len(result["text"]),
                           transcript_preview=result["text"][:100])
                try:
                    summary = await summarize_content_for_ads(result["text"])
                    logger.info("summary_received",
                               has_summary=bool(summary),
                               has_embedding_query=bool(summary.get("embedding_query")),
                               embedding_query_length=len(summary.get("embedding_query", "")),
                               embedding_query_preview=summary.get("embedding_query", "")[:150] if summary.get("embedding_query") else None,
                               query=summary.get("query") if summary else None)
                except Exception as summary_error:
                    logger.error("summary_generation_failed", 
                                error=str(summary_error), 
                                error_type=type(summary_error).__name__,
                                exc_info=True)
                    # Don't set summary - let it be None so process-and-match can regenerate
                    summary = None
                
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
        logger.info("step_1_transcribing_video", filename=file.filename, model_size=model_size)
        transcription_response = await transcribe_video(file, model_size)
        transcript = transcription_response.text
        summary = transcription_response.summary
        
        logger.info("transcription_complete",
                   transcript_length=len(transcript),
                   has_summary_from_transcribe=bool(summary),
                   summary_keys=list(summary.keys()) if summary else [])
        
        # Regenerate if summary is missing or is just the transcript (fallback case)
        if not summary or (summary.get("embedding_query", "")[:100].strip() == transcript[:100].strip() if summary.get("embedding_query") else False):
            if summary:
                logger.warning("summary_is_transcript", 
                             message="Regenerating summary - original was transcript",
                             original_embedding_preview=summary.get("embedding_query", "")[:100])
            else:
                logger.warning("summary_missing", message="Creating summary - none from transcribe")
            # This will now raise an error if JSON parsing fails - no more hiding it!
            summary = await summarize_content_for_ads(transcript)
            logger.info("summary_ready", 
                       has_embedding_query=bool(summary.get("embedding_query")),
                       embedding_length=len(summary.get("embedding_query", "")),
                       embedding_preview=summary.get("embedding_query", "")[:150],
                       is_still_transcript=summary.get("embedding_query", "")[:100].strip() == transcript[:100].strip() if summary.get("embedding_query") else False)
        
        # Step 2: Find matching ads using Cortex Search
        logger.info("step_2_finding_matching_ads",
                   summary_has_embedding_query=bool(summary.get("embedding_query")),
                   summary_has_query=bool(summary.get("query")),
                   embedding_query_length=len(summary.get("embedding_query", "")),
                   embedding_query_preview=summary.get("embedding_query", "")[:150] if summary.get("embedding_query") else None)
        search_text = summary.get("embedding_query") or summary.get("query") or transcript[:200]
        logger.info("search_text_selected",
                   search_text_length=len(search_text),
                   search_text_preview=search_text[:150],
                   source="embedding_query" if summary.get("embedding_query") else ("query" if summary.get("query") else "transcript"))
        
        # Default columns if not specified - include all metadata fields
        if not columns:
            columns = [
                "id", 
                "name", 
                "category", 
                "price", 
                "image_url", 
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
        
        print(summary)
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


# Company onboarding routes
@router.post("/companies", response_model=CompanyResponse)
async def create_company(company_req: CompanyCreateRequest, db: Session = Depends(get_db)):
    try:
        company = Company(
            id=str(uuid.uuid4()),
            name=company_req.name
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        return CompanyResponse(id=company.id, name=company.name)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create company: {str(e)}")

@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    db: Session = Depends(get_db)
):
    """Get a company by ID"""
    logger.info("get_company_requested", company_id=company_id)
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return CompanyResponse(
        id=company.id,
        name=company.name,
    )


@router.get("/companies", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all companies"""
    logger.info("list_companies_requested", skip=skip, limit=limit)
    
    query = db.query(Company)
    
    companies = query.offset(skip).limit(limit).all()
    
    return [
        CompanyResponse(
            id=company.id,
            name=company.name,
        )
        for company in companies
    ]



# Product onboarding routes
@router.post("/products", response_model=ProductResponse)
async def create_product(req: ProductCreateRequest, db: Session = Depends(get_db)):
    try:
        product = Product(
            id=str(uuid.uuid4()),
            company_id=req.company_id,
            name=req.name,
            description=req.description,
            price=req.price,
            tags=req.tags if req.tags else "",
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        return ProductResponse(
            id=product.id,
            company_id=product.company_id,
            name=product.name,
            description=product.description,
            price=product.price,
            tags=product.tags,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to create product: {str(e)}")



@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get a product by ID"""
    logger.info("get_product_requested", product_id=product_id)
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductResponse(
        id=product.id,
        company_id=product.company_id,
        name=product.name,
        description=product.description,
        price=product.price,
        tags=product.tags,
    )


@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    company_id: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List products with optional filters"""
    logger.info("list_products_requested", company_id=company_id, category=category, skip=skip, limit=limit)
    
    query = db.query(Product)
    
    if company_id:
        query = query.filter(Product.company_id == company_id)
    if category:
        query = query.filter(Product.category == category)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    products = query.offset(skip).limit(limit).all()
    
    return [
        ProductResponse(
        id=product.id,
        company_id=product.company_id,
        name=product.name,
        description=product.description,
        price=product.price,
        tags=product.tags,
    )        for product in products
    ]


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a product"""
    logger.info("update_product_requested", product_id=product_id)
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields
    if request.name is not None:
        product.name = request.name
    if request.description is not None:
        product.description = request.description
    if request.price is not None:
        product.price = request.price
    if request.currency is not None:
        product.currency = request.currency
    if request.category is not None:
        product.category = request.category
    if request.ad_phrases is not None:
        product.ad_phrases = request.ad_phrases
    if request.use_cases is not None:
        product.use_cases = request.use_cases
    if request.features is not None:
        product.features = request.features
    if request.target_audience is not None:
        product.target_audience = request.target_audience
    if request.pain_points is not None:
        product.pain_points = request.pain_points
    if request.keywords is not None:
        product.keywords = request.keywords
    if request.extra_metadata is not None:
        product.extra_metadata = request.extra_metadata
    if request.is_active is not None:
        product.is_active = request.is_active
    
    # Regenerate LLM content if key fields changed
    if request.name or request.description or request.category or request.features or request.use_cases or request.pain_points:
        logger.info("regenerating_product_content")
        company = db.query(Company).filter(Company.id == product.company_id).first()
        llm_content = await generate_product_content(
            name=product.name,
            description=product.description,
            category=product.category,
            company_name=company.name if company else None,
            features=product.features,
            use_cases=product.use_cases,
            pain_points=product.pain_points
        )
        product.embedded_text = llm_content.get("embedded_text")
        product.product_summary = llm_content.get("product_summary")
        if not request.ad_phrases:
            product.ad_phrases = llm_content.get("ad_phrases", [])
        if not request.keywords:
            product.keywords = llm_content.get("keywords", [])
        if not request.target_audience:
            product.target_audience = llm_content.get("target_audience", {})
        if not request.pain_points:
            product.pain_points = llm_content.get("pain_points", [])
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    
    return ProductResponse(
        id=product.id,
        company_id=product.company_id,
        name=product.name,
        description=product.description,
        price=product.price,
        currency=product.currency,
        category=product.category,
        image_urls=product.image_urls,
        embedded_text=product.embedded_text,
        ad_phrases=product.ad_phrases,
        use_cases=product.use_cases,
        product_summary=product.product_summary,
        features=product.features,
        target_audience=product.target_audience,
        pain_points=product.pain_points,
        keywords=product.keywords,
        extra_metadata=product.extra_metadata,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at
    )


# Image upload routes
@router.post("/companies/{company_id}/logo", response_model=ImageUploadResponse)
async def upload_company_logo(
    company_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a company logo"""
    logger.info("upload_company_logo_requested", company_id=company_id, filename=file.filename)
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Generate storage key
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        storage_key = f"companies/{company_id}/logo{file_ext}"
        
        # Upload to storage
        storage_id = await storage_put(file_content, storage_key)
        
        # Get URL
        image_url = await storage_url(storage_id)
        
        # Update company record
        company.logo_url = image_url
        db.commit()
        
        logger.info("company_logo_uploaded", company_id=company_id, image_url=image_url)
        
        return ImageUploadResponse(
            image_url=image_url,
            storage_id=storage_id,
            message="Company logo uploaded successfully"
        )
    except Exception as e:
        logger.error("upload_company_logo_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload logo: {str(e)}")


@router.post("/products/{product_id}/images", response_model=ImageUploadResponse)
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a product image"""
    logger.info("upload_product_image_requested", product_id=product_id, filename=file.filename)
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Generate storage key
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        image_id = uuid.uuid4().hex[:8]
        storage_key = f"products/{product_id}/images/{image_id}{file_ext}"
        
        # Upload to storage
        storage_id = await storage_put(file_content, storage_key)
        
        # Get URL
        image_url = await storage_url(storage_id)
        
        # Update product record
        if product.image_urls is None:
            product.image_urls = []
        product.image_urls.append(image_url)
        db.commit()
        
        logger.info("product_image_uploaded", product_id=product_id, image_url=image_url)
        
        return ImageUploadResponse(
            image_url=image_url,
            storage_id=storage_id,
            message="Product image uploaded successfully"
        )
    except Exception as e:
        logger.error("upload_product_image_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

