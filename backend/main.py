from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Email Processor",
    description="GDPR-compliant AI system for processing emails and creating Pipedrive deals",
    version="0.1.0",
)

# CORS middleware for Railway deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://adaptable-liberation-production.up.railway.app",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_origin_regex="https://.*\\.railway\\.app",  # Allow all Railway subdomains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api import auth

app.include_router(auth.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-email-processor"}


# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI Email Processor API", "version": "0.1.0", "docs": "/docs"}


# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        from app.core.database import create_tables

        create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")


# Include additional routers (will be added as we build them)
# from app.api import dashboard, webhooks, websocket
# app.include_router(dashboard.router, prefix="/api/dashboard")
# app.include_router(webhooks.router, prefix="/api/webhooks")
# app.include_router(websocket.router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
