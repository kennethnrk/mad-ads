"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.logging_config import configure_logging, get_logger, RequestTimingMiddleware
from app.database import init_db
from app.api import routes

# Configure logging first
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("application_starting", version="0.1.0")
    
    # Validate settings
    settings.validate_required()
    
    # Initialize database
    init_db()
    logger.info("application_started")
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")


# Create FastAPI app
app = FastAPI(
    title="Mad Ads Backend",
    description="AI-powered ad campaign generator and optimizer",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
app.add_middleware(RequestTimingMiddleware)

# Include API routes
app.include_router(routes.router, prefix="/api/v1", tags=["api"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Mad Ads Backend",
        "version": "0.1.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_config=None  # Use our custom logging
    )

