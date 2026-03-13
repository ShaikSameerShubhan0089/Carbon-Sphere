import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.endpoints import router as api_router

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CarbonSphere")

app = FastAPI(
    title="CarbonSphere AI",
    description="Enterprise-grade AI Forest Carbon Credit Platform",
    version="1.0.0"
)

# CORS Middleware (Allow All for now, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to CarbonSphere AI 🌍 - Enterprise Carbon Credit Platform"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "CarbonSphere Backend"}
