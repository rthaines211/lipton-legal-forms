"""
FastAPI application for the normalization pipeline.

This module initializes the FastAPI application and configures middleware,
CORS, and routing for the normalization API service.
"""

import os
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"✅ Loaded environment variables from {env_path}")
    else:
        logger.warning(f"⚠️  .env file not found at {env_path}")
except ImportError:
    logger.warning("⚠️  python-dotenv not installed, skipping .env file loading")
except Exception as e:
    logger.error(f"❌ Failed to load .env file: {e}")

# Initialize FastAPI application
app = FastAPI(
    title="Legal Discovery Normalization API",
    description="API service for normalizing legal form data and generating discovery documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes
from api.routes import router
app.include_router(router)

# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint providing basic API information.

    Returns:
        Dict containing API name and version information
    """
    return {
        "service": "Legal Discovery Normalization API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring service availability.

    Returns:
        Dict with status information
    """
    return {
        "status": "healthy",
        "service": "normalization-api"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Args:
        request: The incoming request
        exc: The exception that was raised

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"Internal server error: {str(exc)}"
        }
    )

if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))

    logger.info(f"Starting server on {host}:{port}")

    # Run the application
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
