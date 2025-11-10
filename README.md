# Mad Ads — Smart Ad Matching for Content Creators

## Inspiration

For years, ads have been annoying.

Creators hate interrupting their content.  
Viewers hate irrelevant, random ads.  
Brands hate wasting money on impressions that don't convert.

There was a time we were all just scrolling TikTok/YouTube and thinking — *"wait… this video would be PERFECT for a Nike ad"* but instead the platform was sending a totally irrelevant, generic filler ad.

Meanwhile — billions of dollars are burned every year on **spray-and-pray advertising**.

- Global digital ad spend = **$740B+ by 2025**
- 65%+ of advertisers say they **struggle to reach the right audience**
- 54% of creators say brand deals are **their #1 revenue source** but only **12%** actually get inbound brand sponsorship requests

This is inefficient.

But there's another problem: **the creator economy is gatekept**.

The top 1% of creators get all the brand deals. Small creators — even those with engaged, niche audiences — are locked out. They don't have the reach numbers that brands look for, they don't have agents, they don't have connections. Meanwhile, these same small creators are often the ones producing the most authentic, targeted content that would be perfect for specific brands.

We wanted to **democratize access to brand deals** by giving smaller creators the same opportunities as the big players. By automating the matchmaking process, we remove the barriers of scale, connections, and negotiation power. A creator with 10K followers making fitness content should be able to monetize just as easily as someone with 1M followers — if their content is the right fit for the brand.

That inefficiency became the spark.

We wanted to build a world where ads don't interrupt — they *blend*.

Where ads become native, contextual *content*, not just an interruption.

Where **every creator**, regardless of follower count, can access brand monetization opportunities.

That is where Mad Ads started.


## What it does

Mad Ads is an AI ad marketplace that auto-matches brands to creators and then programmatically inserts the right ads into the right moment in a video.

**Flow:**
1. Brands upload their product + ad videos.
2. Creators upload their raw content.
3. Our model:
   - understands the context of the content
   - finds breakpoints — natural cut points in the video
   - chooses relevant ads based on semantic match
   - edits the video to insert those ads *precisely where they make sense*

In the future — Mad Ads will not only place ads.  
It will **generate ads**.

Creators don't need to pitch brands.  
Brands don't need to cold-email creators.  
The entire matchmaking + insertion pipeline is automated.


## How we built it

- Computer vision + scene segmentation to detect breakpoints
- Vector embeddings for contextual similarity between content themes and product categories
- Rule-based and ML-based ad selection scoring
- Automated video editing pipeline to stitch ad clips into the creator content timeline

We made creators and marketers speak the same language — through embeddings.


## Challenges we ran into

- Finding breakpoints that *feel* natural (audience perception matters more than just scene cuts)
- Dealing with variable video formats, codecs, fps differences
- Semantic similarity scoring that avoids false positives
- Making sure ads don't ruin pacing or comedic timing


## Accomplishments that we're proud of

- Fully automated ad insertion without manual editing
- A pipeline that helps **small creators** access brand money — not just the top 1%
- Interpretation of content at semantic level (not just keyword matching)


## What we learned

- Creator economy ≠ linear marketplace
- Attention is the new currency
- Relevancy determines whether an ad is *annoying* or *valuable*

The biggest lesson?  
The future of ads is **contextual, invisible, intelligent**.


## What's next for Mad Ads

- Generative ad creation (no existing ad needed)
- Pay-per-performance revenue split between brand + creator
- Real-time A/B preference matching based on viewer cohorts
- Subscription model for creators who want passive brand monetization

Mad Ads is building towards a future where every piece of content becomes monetizable — **without ever breaking the vibe**.

---

# Mad Ads Backend

AI-powered ad campaign generator and optimizer with React frontend and FastAPI backend.

## Quick Start

### Run Both Services

**Terminal 1 - Backend:**
```bash
./run.sh
```

**Terminal 2 - Frontend:**
```bash
./run-frontend.sh
```

- Backend API: http://localhost:8000
- Frontend UI: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Backend Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:

- **Snowflake**: Account, user, password, warehouse, database, schema, role
- **Gemini AI**: API key for content generation
- **ElevenLabs**: API key for text-to-speech
- **Vultr**: API key and endpoint (optional, for object storage)
- **Solana**: RPC URL and private key (optional)

### 4. Run the Application

```bash
# Option 1: Use the run script (recommended)
./run.sh

# Option 2: Manual activation and run
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Use Python directly
source venv/bin/activate
python -m app.main
```

**Note:** Always activate the virtual environment (`source venv/bin/activate`) before running the application or installing packages.

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Match Content to Ads
```
POST /api/v1/match
Body: {
  "content_id": "content_123",
  "ad_pool_id": "pool_456",  # optional
  "brief": "target fitness enthusiasts",  # optional
  "limit": 5
}
```

## Project Structure

```
mad-ads-backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── database.py           # Database connection
│   ├── logging_config.py     # Structured logging
│   ├── api/
│   │   ├── routes.py         # API route handlers
│   │   └── models.py         # Pydantic models
│   ├── mcp/
│   │   ├── server.py         # MCP server setup
│   │   └── tools.py          # MCP tool implementations
│   └── db/
│       └── schema.py         # SQLAlchemy models
├── requirements.txt
├── .env.example
└── README.md
```

## Features

- **FastAPI** REST API with automatic OpenAPI documentation
- **MCP Server** with tool stubs for Snowflake, TTS, optimization, etc.
- **SQLite In-Memory Database** for hackathon demo
- **Structured Logging** with JSON output and request tracing
- **Environment Configuration** with validation using pydantic-settings

## Development

### Logging

All logs are structured JSON format with:
- Request IDs for tracing
- Request/response timing
- Error tracking with stack traces

### Database

The database is SQLite in-memory, so data is lost on restart. For production, switch to persistent storage.

### MCP Tools

All MCP tools are currently stubs returning mock data. Implement real functionality by updating `app/mcp/tools.py`.

## Frontend Setup

The frontend is a React application built with:
- **React 19** with Create React App
- **Tailwind CSS** for styling
- **Chakra UI** components
- **React Router** for navigation
- **Horizon UI** template

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL

Create a `.env` file in the `frontend/` directory:

```bash
cd frontend
cp .env.example .env
```

Edit `.env` and set the backend API URL (default: `http://localhost:8000`):

```
REACT_APP_API_URL=http://localhost:8000
```

### 3. Run Frontend

```bash
# Option 1: Use the run script
./run-frontend.sh

# Option 2: Manual
cd frontend
npm start
```

The frontend will be available at `http://localhost:3000`

### Frontend API Integration

The frontend includes API service utilities in:
- `src/config/api.js` - API endpoint configuration
- `src/services/api.js` - API service functions

Example usage:
```javascript
import { matchContent, checkHealth } from 'services/api';

// Check backend health
const health = await checkHealth();

// Match content to ads
const matches = await matchContent({
  content_id: "content_123",
  limit: 5
});
```

## Project Structure

```
mad-ads-backend/
├── app/                    # Backend FastAPI application
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── api/
│   ├── mcp/
│   └── db/
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── config/         # API configuration
│   │   ├── services/       # API service functions
│   │   ├── components/     # React components
│   │   └── views/          # Page views
│   ├── package.json
│   └── .env.example
├── requirements.txt
├── run.sh                  # Backend run script
├── run-frontend.sh         # Frontend run script
└── README.md
```

## Next Steps

1. Connect Snowflake Cortex search (see teammate's code in research.md)
2. Implement Gemini AI integration for content generation
3. Add ElevenLabs TTS integration
4. Implement real matching algorithm
5. Add budget optimization logic
6. Set up metrics simulation with SSE
7. Integrate frontend with backend API endpoints
