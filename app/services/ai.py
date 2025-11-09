"""AI/content processing services using Gemini"""

import json
import os
import csv
from datetime import datetime
from typing import Any, Dict, Optional
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


def _log_to_csv(transcript: str, prompt: str, gemini_response: str, result: Dict[str, Any], error: Optional[str] = None):
    """Log Gemini input/output to CSV for debugging"""
    csv_file = "gemini_summary_logs.csv"
    file_exists = os.path.exists(csv_file)
    
    try:
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    'timestamp',
                    'transcript_length',
                    'transcript_preview',
                    'prompt_length',
                    'prompt_preview',
                    'gemini_response_length',
                    'gemini_response_preview',
                    'embedding_query',
                    'query',
                    'has_signals',
                    'error',
                    'result_json'
                ])
            
            writer.writerow([
                datetime.now().isoformat(),
                len(transcript),
                transcript[:200],
                len(prompt),
                prompt[:200],
                len(gemini_response) if gemini_response else 0,
                gemini_response[:200] if gemini_response else '',
                result.get('embedding_query', '')[:500],
                result.get('query', ''),
                bool(result.get('signals')),
                error or '',
                json.dumps(result)[:1000]  # Limit JSON size
            ])
        logger.info("logged_to_csv", csv_file=csv_file)
    except Exception as e:
        logger.error("csv_log_error", error=str(e))


async def summarize_content_for_ads(transcript: str) -> Dict[str, Any]:
    """
    Summarize content/transcript into signals optimized for Snowflake Cortex ad embedding queries.
    
    Returns dict with: query, embedding_query, topics, signals, context
    """
    logger.info("summarize_content_called", transcript_length=len(transcript))
    
    if not settings.gemini_api_key:
        logger.warning("gemini_api_key_missing")
        raise ValueError("GEMINI_API_KEY not set - cannot generate summary")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""Analyze this content for product ad matching. Return ONLY valid JSON (no markdown):

Transcript:
{transcript}

Return JSON:
{{
  "embedding_query": "50-200 word semantic description for vector search",
  "query": "2-5 word search query",
  "topics": ["topic1", "topic2"],
  "signals": {{
    "keywords": ["keyword1"],
    "product_needs": ["need1"],
    "categories": ["category1"],
    "audience": ["audience1"],
    "pain_points": ["pain1"]
  }},
  "context": "50-100 word context summary"
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from response - more robust parsing
        original_text = result_text
        
        # Remove markdown code blocks
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        # Find JSON boundaries
        start_idx = result_text.find("{")
        end_idx = result_text.rfind("}") + 1
        if start_idx >= 0 and end_idx > start_idx:
            result_text = result_text[start_idx:end_idx]
        
        # Try parsing with better error handling
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError as e:
            logger.warning("json_parse_attempt_failed", error=str(e), preview=result_text[:200])
            # Try to fix common issues: unescaped quotes, trailing commas
            fixed_text = result_text.replace("'", '"')  # Replace single quotes
            fixed_text = fixed_text.replace(',\n}', '\n}')  # Remove trailing commas
            fixed_text = fixed_text.replace(',\n]', '\n]')  # Remove trailing commas in arrays
            try:
                result = json.loads(fixed_text)
                logger.info("json_parse_retry_success")
            except:
                # Last resort: try to extract just the embedding_query from the raw response
                logger.error("json_parse_final_failure", response_preview=original_text[:300])
                raise
        
        # Ensure required fields - raise error if critical fields missing instead of using transcript
        if not result.get("embedding_query"):
            raise ValueError(f"Gemini response missing 'embedding_query' field. Response: {result_text[:300]}")
        if not result.get("query"):
            result["query"] = " ".join(result.get("topics", [])[:5]) if result.get("topics") else "products"
        if not result.get("signals"):
            result["signals"] = {}
        if not result.get("context"):
            result["context"] = result.get("embedding_query", "")[:200]  # Use embedding_query instead of transcript
        
        logger.info("summarize_completed", query=result.get("query"), embedding_length=len(result.get("embedding_query", "")))
        return result
        
    except json.JSONDecodeError as e:
        logger.error("json_parse_failed", 
                    error=str(e), 
                    error_position=getattr(e, 'pos', None),
                    response_preview=original_text[:500] if 'original_text' in locals() else result_text[:500],
                    extracted_json_preview=result_text[:500] if 'result_text' in locals() else 'N/A')
        # Re-raise to see the actual error instead of hiding it
        raise ValueError(f"Failed to parse JSON from Gemini response: {str(e)}. Response preview: {original_text[:300] if 'original_text' in locals() else 'N/A'}")
    except Exception as e:
        logger.error("summarize_error", error=str(e), error_type=type(e).__name__, exc_info=True)
        # Re-raise to see the actual error instead of hiding it
        raise

