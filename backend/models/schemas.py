from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 1.0

class CarbonResult(BaseModel):
    biomass_tons: float
    carbon_stock_tons: float
    co2_tons: float
    carbon_credits: float
    confidence_score: float

class AnalysisResponse(BaseModel):
    id: Optional[str] = None
    latitude: float
    longitude: float
    timestamp: datetime
    satellite_metrics: dict
    ai_metrics: dict
    carbon_analysis: CarbonResult
    status: str

class HistoryResponse(BaseModel):
    results: List[AnalysisResponse]
