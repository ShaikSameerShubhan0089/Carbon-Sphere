from fastapi import APIRouter
from backend.api import endpoints

api_router = APIRouter()

api_router.include_router(endpoints.router, prefix="/forest", tags=["Forest Analysis"])
