from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from backend.services.gee_service import gee_service
from backend.services.ai_service import ai_service
from backend.services.gis_service import gis_service
from backend.services.carbon_service import carbon_service
from backend.services.db_service import db_service
from backend.models.schemas import AnalysisResponse, CarbonResult
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger("CarbonSphere.API")

@router.post("/forest/analyze", response_model=AnalysisResponse)
async def analyze_forest(
    latitude: float = Form(...),
    longitude: float = Form(...),
    image: UploadFile = File(...),
    sensitivity: int = Form(50), # New parameter for tuning
    model: str = Form("hsv")
):
    """
    Analyzes forest area from uploaded image and coordinates.
    Returns Carbon Credits estimation.
    """
    logger.info(f"Received analysis request for {latitude}, {longitude}")
    
    # 1. Fetch Satellite Data (Sentinel-2 NDVI)
    satellite_metrics = gee_service.get_forest_metrics(latitude, longitude)
    ndvi = satellite_metrics.get("ndvi_mean", 0.0)
    
    # 2. AI Tree Segmentation
    image_bytes = await image.read()
    ai_metrics = ai_service.segment_trees(image_bytes, sensitivity, model)
    tree_cover = ai_metrics.get("tree_cover_ratio", 0.0)
    
    # 3. GIS Area Calculation (Fixed 1km radius for now)
    radius_km = 1.0
    area_hectares = gis_service.calculate_circle_area(radius_km)
    
    # 4. Carbon Credit Calculation
    carbon_result = carbon_service.calculate_carbon_credits(area_hectares, tree_cover, ndvi)
    
    # 5. Construct Response
    response_data = {
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": datetime.utcnow(),
        "satellite_metrics": satellite_metrics,
        "ai_metrics": ai_metrics,
        "carbon_analysis": carbon_result,
        "status": "success"
    }
    
    # 6. Save to Database
    db_id = db_service.save_analysis(response_data)
    response_data["id"] = db_id
    
    return response_data

@router.get("/history")
async def get_history():
    """
    Fetches historical analysis records from MongoDB.
    """
    return db_service.get_history()

@router.get("/forest/history-simulation")
async def get_historical_simulation(lat: float, lon: float):
    """
    Returns simulated 2-year historical data (Mocking GEE Archive).
    """
    return gee_service.get_historical_simulation(lat, lon)
