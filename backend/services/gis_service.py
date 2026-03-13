import math
import logging

logger = logging.getLogger("CarbonSphere.GIS")

try:
    from shapely.geometry import Point, Polygon
    import geopandas as gpd
    GIS_AVAILABLE = True
except ImportError:
    GIS_AVAILABLE = False
    logger.warning("GIS libraries (shapely, geopandas) not found. Running in MOCK mode.")

class GISService:
    def calculate_circle_area(self, radius_km: float) -> float:
        """
        Calculates area of a circle in hectares given radius in km.
        """
        area_km2 = math.pi * (radius_km ** 2)
        area_hectares = area_km2 * 100
        return area_hectares

    def create_buffer_polygon(self, lat: float, lon: float, radius_km: float):
        """
        Creates a polygon buffer around a point.
        """
        if GIS_AVAILABLE:
             # Simple approximation for now using shapely
             # In production, use appropriate projection (e.g., EPSG:3857)
             return {"type": "Point", "coordinates": [lon, lat], "radius_km": radius_km}
        else:
             return {"mock_polygon": True, "lat": lat, "lon": lon, "radius": radius_km}

gis_service = GISService()
