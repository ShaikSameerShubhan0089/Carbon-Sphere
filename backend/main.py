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

# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# API ROUTES
# ----------------------------
app.include_router(api_router, prefix="/api/v1")

# ----------------------------
# FRONTEND PATH
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# ----------------------------
# SERVE FRONTEND
# ----------------------------
if os.path.exists(FRONTEND_DIR):

    # Serve JS, CSS, images
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

    # Root route -> index.html
    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

else:

    @app.get("/")
    async def root():
        return {"message": "Frontend not found"}


# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "CarbonSphere Backend"}