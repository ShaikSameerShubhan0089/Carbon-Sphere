import logging
from datetime import datetime, timedelta
import random
import math
import os

logger = logging.getLogger("CarbonSphere.GEE")

try:
    import ee
    GEE_AVAILABLE = True
except ImportError:
    GEE_AVAILABLE = False
    logger.warning("earthengine-api not found. Running in MOCK mode.")

class GEEService:
    def __init__(self):
        self.initialized = False
        if GEE_AVAILABLE:
            try:
                # Try to authenticate/initialize.
                # In a real app, you'd use a service account key file.
                # ee.Authenticate() # Interactive auth (skip for server)
                # ee.Initialize()
                
                # For this enterprise prompt, we'll assume credentials are set via env or file
                # If not, we fall back to mock mode.
                if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                     ee.Initialize()
                     self.initialized = True
                     logger.info("Google Earth Engine initialized successfully.")
                else:
                     logger.warning("GEE credentials not found. Running in MOCK mode.")
            except Exception as e:
                logger.error(f"Failed to initialize GEE: {e}. Running in MOCK mode.")

    def get_forest_metrics(self, lat: float, lon: float, radius_km: float = 1.0):
        """
        Fetches Sentinel-2 data and computes forest metrics (NDVI).
        """
        if not self.initialized:
            return self._mock_response(lat, lon)

        try:
            point = ee.Geometry.Point([lon, lat])
            buffer = point.buffer(radius_km * 1000)
            
            # Sentinel-2 collection
            s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
                .filterBounds(buffer) \
                .filterDate('2023-01-01', '2023-12-31') \
                .sort('CLOUDY_PIXEL_PERCENTAGE') \
                .first()

            # Compute NDVI
            ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')
            
            # Reduce region to get mean NDVI
            stats = ndvi.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=buffer,
                scale=10,
                maxPixels=1e9
            )
            
            mean_ndvi = stats.get('NDVI').getInfo()
            
            return {
                "ndvi_mean": mean_ndvi,
                "satellite_source": "Sentinel-2",
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"GEE Error: {e}")
            return self._mock_response(lat, lon)

    def get_historical_simulation(self, lat: float, lon: float, years: int = 2):
        """
        Simulates historical data fetching from GEE Archive.
        Generates seasonal trends for the past 'years'.
        """
        history = []
        base_ndvi = 0.65
        current_date = datetime.utcnow()
        
        for i in range(years * 12):
            # Go back month by month
            date = current_date - timedelta(days=30 * i)
            month = date.month
            
            # Simple Seasonality: Higher in summer/monsoon (months 6-9), lower in winter
            season_factor = 0.1 * math.sin((month - 1) * math.pi / 6) 
            
            # Random variation
            noise = random.uniform(-0.05, 0.05)
            
            ndvi = base_ndvi + season_factor + noise
            ndvi = max(0, min(1, ndvi)) # Clamp 0-1
            
            # Carbon estimation (consistent with 1km radius = 314.16 hectares)
            # Formula: Area (ha) * Biomass_Density (tons/ha) * 0.5 (C) * 3.67 (CO2)
            # Area = pi * 1^2 * 100 = 314.16 ha
            area_hectares = 314.16
            
            # Simple biomass proxy: 150 tons/ha for dense forest * ndvi
            biomass_density = ndvi * 150 
            
            carbon_tons = area_hectares * biomass_density * 0.5 * 3.67
            
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "ndvi": round(ndvi, 2),
                "carbon_credits": round(carbon_tons, 2)
            })
            
        return history[::-1] # Reverse to be chronological

    def _mock_response(self, lat, lon):
        import random
        return {
            "ndvi_mean": 0.65 + (random.random() * 0.2 - 0.1), # Random value between 0.55 and 0.75
            "satellite_source": "MOCK_DATA",
            "status": "mocked"
        }

gee_service = GEEService()
