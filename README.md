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

