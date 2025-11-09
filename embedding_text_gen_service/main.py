# pip install fastapi uvicorn google-genai snowflake-connector-python python-dotenv

import os
import json
import asyncio
import random
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv
import snowflake.connector  # Use synchronous connector

# --------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------
load_dotenv()

app = FastAPI(title="Product Enrichment Service", version="1.0")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Singleton snowflake connect object
sf_conn = None  # initialized below

def get_sf_conn():
    global sf_conn
    if sf_conn is None or sf_conn.is_closed():  # is_closed for auto reconnect
        sf_conn = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            autocommit=True,
        )
    return sf_conn

# --------------------------------------------------------------------
# Input schema
# --------------------------------------------------------------------
class ProductInput(BaseModel):
    id: str
    product_name: str
    company_name: str
    product_short_description: Optional[str] = None
    price: float
    currency: str
    image_url: str


# --------------------------------------------------------------------
# Helper: retry wrapper with exponential backoff (async)
# --------------------------------------------------------------------
async def retry_with_backoff(func, *args, max_retries=5, base_delay=1, context="", **kwargs):
    for attempt in range(max_retries):
        try:
            logging.info(f"🧠 Gemini request ({context}) attempt {attempt + 1}")
            return await func(*args, **kwargs)
        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ["503", "service unavailable", "rate limit"]):
                wait = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
                logging.warning(f"⚠️ Retry {attempt+1}/{max_retries} in {wait:.1f}s for {context}")
                await asyncio.sleep(wait)
                continue
            raise
    raise RuntimeError(f"Gemini failed after {max_retries} retries for {context}")


# --------------------------------------------------------------------
# Core logic (image extraction + enrichment + Snowflake insert)
# --------------------------------------------------------------------
async def extract_from_image(image_url: str) -> str:
    async def call_model():
        model = "gemini-2.5-flash-lite"
        contents = [
            types.Content(role="user", parts=[
                types.Part.from_text(
                    text=f"Extract all information about the product visible in this image: {image_url}"
                )
            ])
        ]
        tools = [types.Tool(url_context=types.UrlContext())]
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            image_config=types.ImageConfig(image_size="1K"),
            tools=tools,
        )
        # Gemini SDK is sync, so run in thread executor for async
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=model, contents=contents, config=config
            )
        )
        return response.text

    return await retry_with_backoff(call_model, context="image_extraction")


async def enrich_metadata(prod):
    image_text = await extract_from_image(prod['image_url'])

    prompt = f"""
You are an AI enrichment model for product metadata enrichment.

Product:
- Product Name: {prod['product_name']}
- Company Name: {prod['company_name']}
- Short description: {prod['product_short_description']}
- Price: {prod['price']} {prod['currency']}
- Image details: {image_text}

Tasks:
1. Choose a category of the product that makes sense based on the product name, description, and image.
2. Write one long paragraph "embedded_text" describing purpose, materials, benefits, who/when to use, numeric claims.
3. List 5–10 realistic "ad_phrases" users might say.
4. List 3–5 concise "use_cases".

Output valid JSON:
{{
  "category": "...",
  "embedded_text": "...",
  "ad_phrases": ["..."],
  "use_cases": ["..."]
}}
"""
    async def call_model():
        model = "gemini-2.5-flash"
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
        config = types.GenerateContentConfig(
            temperature=0.5,
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            response_mime_type="application/json",
        )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(model=model, contents=contents, config=config)
        )
        return response.text

    response_text = await retry_with_backoff(call_model, context="metadata_enrichment")

    try:
        return json.loads(response_text)
    except Exception:
        logging.error(f"Bad JSON from Gemini:\n{response_text}")
        raise HTTPException(status_code=500, detail="Gemini returned invalid JSON")


async def insert_to_snowflake(record):
    ad_phrases_array = ",".join([f"'{p}'" for p in record["ad_phrases"]])
    use_cases_array = ",".join([f"'{u}'" for u in record["use_cases"]])

    sql = f"""
    INSERT INTO PRODUCTS (
        id, product_name, company_name, product_short_description,
        price, currency, image_url, category,
        embedded_text, ad_phrases, use_cases
    )
    SELECT
        %(id)s, %(product_name)s, %(company_name)s, %(product_short_description)s,
        %(price)s, %(currency)s, %(image_url)s, %(category)s,
        %(embedded_text)s,
        ARRAY_CONSTRUCT({ad_phrases_array}),
        ARRAY_CONSTRUCT({use_cases_array});
    """

    # record["id"] = record["product_name"].upper().replace(" ", "-")[:20]

    # The snowflake connector is synchronous, so run in executor for async integration
    def db_task(sql, record):
        conn = get_sf_conn()
        with conn.cursor() as cur:
            cur.execute(sql, record)
            # Commit is a no-op if autocommit True, but included for clarity
            conn.commit()

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, db_task, sql, record)
    logging.info(f"✅ Inserted {record['product_name']} into Snowflake.")


# --------------------------------------------------------------------
# API Endpoint (async)
# --------------------------------------------------------------------
@app.post("/enrich")
async def enrich_product(input_product: ProductInput):
    product_dict = input_product.model_dump()
    logging.info(f"🚀 Received product: {product_dict['product_name']}")
    enriched = await enrich_metadata(product_dict)
    full_record = {**product_dict, **enriched}
    await insert_to_snowflake(full_record)
    return {"status": "success", "record": full_record}