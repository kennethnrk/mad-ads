"""LLM-powered content generation for companies and products"""

import json
from typing import Any, Dict, List, Optional

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


async def generate_company_content(
    name: str,
    description: Optional[str] = None,
    industry: Optional[str] = None,
    website: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate LLM-powered company content including brand voice, summary, and keywords.
    
    Args:
        name: Company name
        description: Optional company description
        industry: Optional industry category
        website: Optional website URL
        
    Returns:
        Dictionary with:
        - brand_voice: Brand voice description
        - company_summary: Summary optimized for content matching
        - brand_keywords: List of brand-relevant keywords
        - target_audience: Target audience characteristics
    """
    logger.info("generate_company_content_called", company_name=name, has_description=bool(description))
    
    if not settings.gemini_api_key:
        logger.warning("gemini_api_key_missing", message="Using simple fallback")
        # Simple fallback
        keywords = [name.lower()] + (description.split()[:10] if description else [])
        return {
            "brand_voice": description or f"{name} is a company in the {industry or 'general'} industry.",
            "company_summary": description or f"{name} provides products and services.",
            "brand_keywords": keywords[:15],
            "target_audience": {}
        }
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""You are analyzing a company to generate content for an ad matching platform. The company information will be used to match with video content from creators.

Company Information:
- Name: {name}
- Description: {description or "Not provided"}
- Industry: {industry or "Not specified"}
- Website: {website or "Not provided"}

Generate the following:

1. **Brand Voice** (100-200 words): Describe the company's brand voice, tone, and personality. Include:
   - Communication style
   - Values and messaging
   - How they present themselves to customers
   - Brand personality traits

2. **Company Summary** (150-300 words): A comprehensive summary optimized for matching with video content. Include:
   - What the company does
   - Key products/services
   - Target market and audience
   - Use cases and scenarios where their products would be relevant
   - Context that would help match this company with relevant video content

3. **Brand Keywords** (15-25 keywords): Important terms, phrases, and concepts related to:
   - Products/services
   - Industry terms
   - Use cases
   - Target audience characteristics
   - Brand values

4. **Target Audience** (structured): Describe the target audience with characteristics like:
   - Demographics (age, gender, location if relevant)
   - Interests and hobbies
   - Pain points
   - Lifestyle characteristics
   - Content consumption patterns

Return ONLY valid JSON (no markdown, no explanation):
{{
  "brand_voice": "detailed brand voice description",
  "company_summary": "comprehensive summary for matching",
  "brand_keywords": ["keyword1", "keyword2", ...],
  "target_audience": {{
    "demographics": {{"age_range": "...", "gender": "...", ...}},
    "interests": ["interest1", ...],
    "pain_points": ["pain1", ...],
    "lifestyle": ["characteristic1", ...]
  }}
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from response
        try:
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            start_idx = result_text.find("{")
            end_idx = result_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                result_text = result_text[start_idx:end_idx]
            
            result = json.loads(result_text)
            
            # Ensure all required fields exist
            if "brand_voice" not in result:
                result["brand_voice"] = description or f"{name} is a company in the {industry or 'general'} industry."
            if "company_summary" not in result:
                result["company_summary"] = description or f"{name} provides products and services."
            if "brand_keywords" not in result:
                keywords = [name.lower()] + (description.split()[:10] if description else [])
                result["brand_keywords"] = keywords[:15]
            if "target_audience" not in result:
                result["target_audience"] = {}
            
            logger.info("generate_company_content_completed", keyword_count=len(result.get("brand_keywords", [])))
            return result
        except json.JSONDecodeError as e:
            logger.warning("json_parse_failed", error=str(e), response_preview=result_text[:200])
            # Fallback
            keywords = [name.lower()] + (description.split()[:10] if description else [])
            return {
                "brand_voice": description or f"{name} is a company in the {industry or 'general'} industry.",
                "company_summary": description or f"{name} provides products and services.",
                "brand_keywords": keywords[:15],
                "target_audience": {}
            }
    except Exception as e:
        logger.error("generate_company_content_error", error=str(e), exc_info=True)
        # Fallback
        keywords = [name.lower()] + (description.split()[:10] if description else [])
        return {
            "brand_voice": description or f"{name} is a company in the {industry or 'general'} industry.",
            "company_summary": description or f"{name} provides products and services.",
            "brand_keywords": keywords[:15],
            "target_audience": {}
        }


async def generate_product_content(
    name: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    company_name: Optional[str] = None,
    features: Optional[List[str]] = None,
    use_cases: Optional[List[str]] = None,
    pain_points: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate LLM-powered product content including embedded text, summary, and matching signals.
    
    Args:
        name: Product name
        description: Optional product description
        category: Optional product category
        company_name: Optional company name for context
        features: Optional list of product features
        use_cases: Optional list of use cases
        pain_points: Optional list of pain points addressed
        
    Returns:
        Dictionary with:
        - embedded_text: Single paragraph optimized for embedding & search
        - product_summary: Summary for matching with video content
        - ad_phrases: List of ad phrases for matching
        - keywords: Product keywords
        - target_audience: Target audience characteristics
        - pain_points: Pain points this product addresses
    """
    logger.info("generate_product_content_called", product_name=name, category=category)
    
    if not settings.gemini_api_key:
        logger.warning("gemini_api_key_missing", message="Using simple fallback")
        # Simple fallback
        keywords = [name.lower()] + (description.split()[:10] if description else [])
        embedded_text = f"{name}. {description or 'A product'}." + (f" Category: {category}." if category else "")
        return {
            "embedded_text": embedded_text,
            "product_summary": description or f"{name} is a product.",
            "ad_phrases": use_cases or [],
            "keywords": keywords[:20],
            "target_audience": {},
            "pain_points": pain_points or []
        }
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        features_str = ", ".join(features) if features else "Not specified"
        use_cases_str = ", ".join(use_cases) if use_cases else "Not specified"
        pain_points_str = ", ".join(pain_points) if pain_points else "Not specified"
        
        prompt = f"""You are analyzing a product to generate content for an ad matching platform. The product information will be used to match with video content from creators.

Product Information:
- Name: {name}
- Description: {description or "Not provided"}
- Category: {category or "Not specified"}
- Company: {company_name or "Not specified"}
- Features: {features_str}
- Use Cases: {use_cases_str}
- Pain Points Addressed: {pain_points_str}

Generate the following:

1. **Embedded Text** (100-200 words): A single, rich paragraph optimized for semantic embedding and vector search. Include:
   - Product name and key features
   - Use cases and scenarios
   - Target audience and context
   - Pain points addressed
   - How it's used
   - This will be embedded for similarity search, so include all relevant context

2. **Product Summary** (150-300 words): A comprehensive summary optimized for matching with video content. Include:
   - What the product is and does
   - Key features and benefits
   - When and how it's used
   - Target audience
   - Scenarios where this product would be relevant in video content
   - Context that helps match with relevant creators

3. **Ad Phrases** (10-20 phrases): Short, searchable phrases that describe when this product would be relevant. Examples:
   - "wrist pain on bench press"
   - "post-workout recovery"
   - "morning energy boost"
   - "travel fitness gear"
   Each phrase should be 2-6 words and describe a specific use case or scenario.

4. **Keywords** (20-30 keywords): Important terms for matching:
   - Product features
   - Use cases
   - Target audience terms
   - Related concepts
   - Industry terms

5. **Target Audience**: Characteristics of who would use this product:
   - Demographics
   - Interests
   - Lifestyle
   - Content consumption patterns

6. **Pain Points**: List of specific problems or pain points this product addresses (expand on provided ones if needed).

Return ONLY valid JSON (no markdown, no explanation):
{{
  "embedded_text": "single rich paragraph for embedding",
  "product_summary": "comprehensive summary for matching",
  "ad_phrases": ["phrase1", "phrase2", ...],
  "keywords": ["keyword1", "keyword2", ...],
  "target_audience": {{
    "demographics": {{"age_range": "...", ...}},
    "interests": ["interest1", ...],
    "lifestyle": ["characteristic1", ...]
  }},
  "pain_points": ["pain1", "pain2", ...]
}}"""
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from response
        try:
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            start_idx = result_text.find("{")
            end_idx = result_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                result_text = result_text[start_idx:end_idx]
            
            result = json.loads(result_text)
            
            # Ensure all required fields exist
            if "embedded_text" not in result:
                result["embedded_text"] = f"{name}. {description or 'A product'}." + (f" Category: {category}." if category else "")
            if "product_summary" not in result:
                result["product_summary"] = description or f"{name} is a product."
            if "ad_phrases" not in result:
                result["ad_phrases"] = use_cases or []
            if "keywords" not in result:
                keywords = [name.lower()] + (description.split()[:10] if description else [])
                result["keywords"] = keywords[:20]
            if "target_audience" not in result:
                result["target_audience"] = {}
            if "pain_points" not in result:
                result["pain_points"] = pain_points or []
            
            logger.info("generate_product_content_completed", ad_phrases_count=len(result.get("ad_phrases", [])))
            return result
        except json.JSONDecodeError as e:
            logger.warning("json_parse_failed", error=str(e), response_preview=result_text[:200])
            # Fallback
            keywords = [name.lower()] + (description.split()[:10] if description else [])
            embedded_text = f"{name}. {description or 'A product'}." + (f" Category: {category}." if category else "")
            return {
                "embedded_text": embedded_text,
                "product_summary": description or f"{name} is a product.",
                "ad_phrases": use_cases or [],
                "keywords": keywords[:20],
                "target_audience": {},
                "pain_points": pain_points or []
            }
    except Exception as e:
        logger.error("generate_product_content_error", error=str(e), exc_info=True)
        # Fallback
        keywords = [name.lower()] + (description.split()[:10] if description else [])
        embedded_text = f"{name}. {description or 'A product'}." + (f" Category: {category}." if category else "")
        return {
            "embedded_text": embedded_text,
            "product_summary": description or f"{name} is a product.",
            "ad_phrases": use_cases or [],
            "keywords": keywords[:20],
            "target_audience": {},
            "pain_points": pain_points or []
        }

