from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from dotenv import load_dotenv
import os

# Import configurations and routes
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import connect_to_mongo, close_mongo_connection
from routes.diagnostico_routes import router as diagnostico_router
from routes.auth_routes import router as auth_router
from services.auth_service import AuthService

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Sustainability Backend API...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Initialize admin user
    auth_service = AuthService()
    await auth_service.initialize_admin_user()
    
    logger.info("Backend API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Backend API...")
    await close_mongo_connection()
    logger.info("Backend API shutdown complete")

# Create FastAPI app with lifespan management
app = FastAPI(
    title="Sustainability Backend API",
    description="""
    Backend API for the Sustainability Widget - Diagnostico Verde platform.
    
    ## Features
    * Submit green diagnosis requests
    * Admin authentication with JWT
    * Analytics and metrics tracking
    * Webhook notifications (Slack/Discord)
    * Comprehensive data validation
    
    ## Authentication
    Protected endpoints require admin authentication:
    - Email: focalisstrategagroup@gmail.com
    - Password: FSG*2025
    
    ## Growth Hacking
    * Traffic source tracking
    * Real-time notifications
    * Analytics dashboard
    * Lead scoring capabilities
    """,
    version="1.0.0",
    contact={
        "name": "Sustainability Team",
        "email": "focalisstrategagroup@gmail.com"
    },
    lifespan=lifespan
)

# Create API router with prefix
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # In production, specify exact origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@api_router.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "Sustainability Backend API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@api_router.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "1.0.0",
        "environment": os.environ.get("NODE_ENV", "development")
    }

# Include routers
api_router.include_router(diagnostico_router)
api_router.include_router(auth_router)

# Add API router to main app
app.include_router(api_router)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "status_code": 404
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error", 
            "message": "An internal server error occurred",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app", 
        host="0.0.0.0", 
        port=8001, 
        reload=True,
        log_level="info"
    )