# Video Processing Workflow - Testing Guide

## Complete Workflow

The system now supports a complete end-to-end workflow:

1. **Upload Video** → `/api/v1/video/process-and-match`
2. **Transcribe** (using Whisper AI)
3. **Summarize** (using Gemini AI) - extracts signals for ad matching
4. **Find Matching Ads** (using Snowflake Cortex Search)
5. **Rank Results** by relevance score
6. **Return to UI** in ranked order

## API Endpoint

### `POST /api/v1/video/process-and-match`

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/video/process-and-match \
  -F "file=@test_vid/videoplayback.mp4" \
  -F "model_size=tiny" \
  -F "limit=10"
```

**Parameters:**
- `file`: Video file (required)
- `model_size`: Whisper model size - `tiny`, `base`, `small`, `medium`, `large` (default: `tiny`)
- `limit`: Number of ads to return (default: 10)
- `columns`: Optional - columns to return from Snowflake (default: `["id", "name", "category", "price", "image_url", "description"]`)
- `filter_obj`: Optional - filter object for Snowflake (e.g., `{"@eq": {"category": "Gear"}}`)

**Response:**
```json
{
  "success": true,
  "transcription": {
    "text": "Full transcript text...",
    "language": "en",
    "duration": 49.36,
    "topics": ["topic1", "topic2", ...]
  },
  "summary": {
    "query": "short query",
    "embedding_query": "rich semantic description for vector search",
    "topics": ["topic1", ...],
    "signals": {
      "keywords": [...],
      "product_needs": [...],
      "categories": [...],
      "audience": [...],
      "pain_points": [...]
    },
    "context": "context summary"
  },
  "query_used": "embedding query text used for search",
  "ads": [
    {
      "rank": 1,
      "relevance_score": 0.95,
      "id": "product_id",
      "name": "Product Name",
      "category": "Gear",
      "price": 199,
      "image_url": "https://...",
      "description": "...",
      "@score": 0.95
    },
    ...
  ],
  "count": 10,
  "metadata": {
    "model_size": "tiny",
    "limit_requested": 10,
    "limit_returned": 10
  }
}
```

## Snowflake Database Requirements

For the workflow to work properly, you need:

### 1. Cortex Search Service
- **Service Name**: `product_search` (configurable via `SNOWFLAKE_CORTEX_SERVICE_NAME`)
- **Database**: `HACKATHON`
- **Schema**: `PRODUCTS`

### 2. Product Table Structure
The Cortex Search service should be configured to search a products table with columns like:
- `id` - Product ID
- `name` - Product name
- `category` - Product category (Gear, Snacks, Supplements, etc.)
- `price` - Product price
- `image_url` - Product image URL
- `description` - Product description (used for embeddings)

### 3. Configuration Needed

**For REST API (Recommended):**
```env
SNOWFLAKE_ACCOUNT_URL=https://ZGXJKBZ-LH19094.snowflakecomputing.com
SNOWFLAKE_PAT=your_personal_access_token
SNOWFLAKE_DATABASE=HACKATHON
SNOWFLAKE_SCHEMA=PRODUCTS
SNOWFLAKE_CORTEX_SERVICE_NAME=product_search
```

**For SQL Fallback:**
```env
SNOWFLAKE_ACCOUNT=ZGXJKBZ-LH19094
SNOWFLAKE_USER=PURUJIT
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKATHON
SNOWFLAKE_SCHEMA=PRODUCTS
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

## Testing

### Quick Test
```bash
# Run the test script
python test_workflow.py
```

### Manual Test
```bash
# 1. Check health
curl http://localhost:8000/api/v1/health

# 2. Test transcription only
curl -X POST http://localhost:8000/api/v1/transcribe \
  -F "file=@test_vid/videoplayback.mp4" \
  -F "model_size=tiny"

# 3. Test full workflow
curl -X POST http://localhost:8000/api/v1/video/process-and-match \
  -F "file=@test_vid/videoplayback.mp4" \
  -F "model_size=tiny" \
  -F "limit=5" | jq
```

## What to Check in Snowflake

If ads are not being returned, verify:

1. **Cortex Search Service exists:**
   ```sql
   SHOW CORTEX SEARCH SERVICES;
   -- Should show "product_search" service
   ```

2. **Service is configured correctly:**
   ```sql
   DESCRIBE CORTEX SEARCH SERVICE product_search;
   ```

3. **Products table has data:**
   ```sql
   SELECT COUNT(*) FROM MVP_PRODUCTS;
   -- Should return > 0
   ```

4. **Test Cortex Search directly:**
   ```sql
   SELECT PARSE_JSON(
     SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
       'product_search',
       '{"query": "protein snack", "limit": 5}'
     )
   )['results'];
   ```

## Current Status

✅ **Implemented:**
- Video transcription (Whisper)
- Content summarization (Gemini)
- Snowflake Cortex Search integration (REST API + SQL fallback)
- Ranking by relevance score
- Complete workflow endpoint

⚠️ **Needs Verification:**
- Snowflake Cortex Search service configuration
- Product table structure matches expected columns
- REST API authentication (PAT token) or SQL connection works

## Next Steps

1. **Verify Snowflake Setup:**
   - Confirm Cortex Search service `product_search` exists
   - Verify product table has data
   - Test direct Cortex Search query

2. **If using REST API:**
   - Set `SNOWFLAKE_ACCOUNT_URL` and `SNOWFLAKE_PAT` in `.env`

3. **If using SQL:**
   - Ensure `SNOWFLAKE_PASSWORD` and other connection params are set

4. **Test the workflow:**
   - Run `python test_workflow.py`
   - Check logs for any errors
   - Verify ads are returned and ranked correctly

