
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api.endpoints import router as api_router

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CarbonSphere")

app = FastAPI(
    title="CarbonSphere AI",
    description="Enterprise-grade AI Forest Carbon Credit Platform",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Frontend directory
FRONTEND_DIR = os.path.join(os.getcwd(), "frontend")

# Serve static files (css, js, images)
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Root endpoint -> serve index.html
@app.get("/")
async def serve_frontend():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "CarbonSphere frontend not found"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "CarbonSphere Backend"}

