# API Testing Dashboard Guide

## Access the Testing Dashboard

1. **Frontend**: http://localhost:3000
2. Navigate to: **API Testing** in the sidebar (or go to http://localhost:3000/admin/testing)
3. **Backend API**: http://localhost:8000
4. **API Docs**: http://localhost:8000/docs

## Available Test Endpoints

### 1. Health Check
- **Endpoint**: `GET /api/v1/health`
- **Purpose**: Verify backend is running
- **Expected Response**: 
  ```json
  {
    "status": "healthy",
    "timestamp": "2025-11-08T18:49:20.402232",
    "version": "0.1.0"
  }
  ```

### 2. Match Content to Ads
- **Endpoint**: `POST /api/v1/match`
- **Purpose**: Match creator content to relevant ads
- **Request Body**:
  ```json
  {
    "content_id": "content_123",
    "ad_pool_id": "pool_456",  // optional
    "brief": "target fitness enthusiasts",  // optional
    "limit": 5
  }
  ```
- **Expected Response**: List of matched ads with scores and reasons

### 3. Generate Ad Variants
- **Endpoint**: `POST /api/v1/generate`
- **Purpose**: Generate ad copy variants (stub - returns mock data)
- **Request Body**:
  ```json
  {
    "content_id": "content_123",
    "ad_id": "ad_1"
  }
  ```

### 4. Text to Speech
- **Endpoint**: `POST /api/v1/tts`
- **Purpose**: Convert text to speech (stub - returns mock data)
- **Request Body**:
  ```json
  {
    "text": "Your ad script here",
    "voice": ""  // optional
  }
  ```

### 5. Optimize Campaign
- **Endpoint**: `POST /api/v1/optimize`
- **Purpose**: Generate budget/media plan (stub - returns mock data)
- **Request Body**:
  ```json
  {
    "goal": "maximize_clicks",
    "variants": ["variant_1", "variant_2"],
    "channels": ["instagram", "google_ads"],
    "budget": 10000
  }
  ```

## Testing Tips

1. **Start with Health Check** - Always verify backend is running first
2. **Use Default Values** - The form comes pre-filled with dummy data
3. **Check Console** - Some endpoints log results to browser console
4. **Error Handling** - Errors are displayed in red alert boxes
5. **Response Display** - Successful responses show formatted results

## Current Status

✅ **Backend**: Running on port 8000
✅ **Frontend**: Running on port 3000
✅ **CORS**: Configured to allow frontend requests
✅ **API Integration**: Service functions ready

## Next Steps

- Implement real backend logic for generate, TTS, and optimize endpoints
- Add more detailed response displays
- Add request/response logging
- Add metrics streaming visualization

