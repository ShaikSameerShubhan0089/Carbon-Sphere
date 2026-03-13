import json
from datetime import datetime
import certifi
import logging
import os
from pymongo import MongoClient
from datetime import datetime
import certifi

logger = logging.getLogger("CarbonSphere.DB")

class DBService:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        # Use absolute path to avoid CWD issues (run.py changes dir to frontend)
        # db_service.py is in backend/services/ -> go up 3 levels to get to root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.local_file = os.path.join(base_dir, "history.json")
        self._ensure_local_db()
        self.connect()

    def _ensure_local_db(self):
        """Creates an empty history file with sample data if it doesn't exist or is empty."""
        should_seed = False
        
        if not os.path.exists(self.local_file):
            should_seed = True
        else:
            try:
                # Check if file has valid data, if it's just empty list [], re-seed
                with open(self.local_file, 'r') as f:
                    data = json.load(f)
                    if not data: # Empty list
                        should_seed = True
            except:
                should_seed = True # Corrupt file
        
        if should_seed:
            # Seed with Sample Data for Demo
            sample_data = [
                {
                    "latitude": 13.6355, "longitude": 79.4236,
                    "timestamp": "2025-10-24T10:00:00",
                    "carbon_analysis": {"carbon_credits": 15230.5, "confidence_score": 0.88},
                    "ai_metrics": {"tree_cover_ratio": 0.75, "segmentation_method": "ResNet50 (Sample)"}
                },
                {
                    "latitude": 13.6355, "longitude": 79.4236,
                    "timestamp": "2025-11-15T14:30:00",
                    "carbon_analysis": {"carbon_credits": 16800.2, "confidence_score": 0.91},
                    "ai_metrics": {"tree_cover_ratio": 0.82, "segmentation_method": "U-Net (Sample)"}
                },
                {
                    "latitude": 13.6355, "longitude": 79.4236,
                    "timestamp": "2025-12-05T09:15:00",
                    "carbon_analysis": {"carbon_credits": 14900.8, "confidence_score": 0.85},
                    "ai_metrics": {"tree_cover_ratio": 0.71, "segmentation_method": "HSV (Sample)"}
                },
                {
                    "latitude": 13.6355, "longitude": 79.4236,
                    "timestamp": "2026-01-20T11:45:00",
                    "carbon_analysis": {"carbon_credits": 18500.0, "confidence_score": 0.94},
                    "ai_metrics": {"tree_cover_ratio": 0.89, "segmentation_method": "U-Net (Sample)"}
                },
                {
                    "latitude": 13.6355, "longitude": 79.4236,
                    "timestamp": datetime.utcnow().isoformat(),
                    "carbon_analysis": {"carbon_credits": 17250.4, "confidence_score": 0.92},
                    "ai_metrics": {"tree_cover_ratio": 0.84, "segmentation_method": "DeepLabV3 (Real)"}
                }
            ]
            
            with open(self.local_file, 'w') as f:
                json.dump(sample_data, f, indent=4)

    def connect(self):
        url = os.environ.get("MONGODB_URL")
        # Default to offline unless proven otherwise
        self.offline_mode = True 
        
        if url:
            try:
                # 1. Try Secure Connection with Certifi
                logger.info("🔌 Connecting to MongoDB...")
                # Short timeout for better UX
                self.client = MongoClient(url, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=3000)
                self.client.admin.command('ping')
                
                self.db = self.client.get_database("carbonsphere_db")
                self.collection = self.db.get_collection("forest_analysis")
                self.offline_mode = False
                logger.info("✅ Connected to MongoDB Atlas.")
                
            except Exception as e:
                # Catch ALL DB errors -> Fallback to Offline Mode
                logger.warning(f"⚠️ MongoDB Connection Failed: {str(e).split(',')[0]}...") 
                logger.warning("🚀 Running in OFFLINE MODE (Using 'history.json' for storage).")
                self.client = None
                self.collection = None
                self.offline_mode = True
        else:
            logger.warning("⚠️ MONGODB_URL not set. Running in Offline Mode.")

    def save_analysis(self, data: dict):
        # Add timestamp
        data["timestamp"] = datetime.utcnow().isoformat()
        
        # 1. Try MongoDB
        if not self.offline_mode and self.collection is not None:
            try:
                # Clone data to avoid reference mutation issues
                doc = data.copy()
                doc["timestamp"] = datetime.utcnow() # Mongo prefers datetime objects
                result = self.collection.insert_one(doc)
                return str(result.inserted_id)
            except Exception as e:
                logger.error(f"Failed to save to MongoDB: {e}")
                # Fallback to local if Mongo insert fails unexpectedly
        
        # 2. Local File Fallback
        try:
            with open(self.local_file, 'r+') as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
                
                history.append(data)
                
                # Rewind and write
                f.seek(0)
                json.dump(history, f, indent=4)
                f.truncate()
                return "saved_locally"
        except Exception as e:
             logger.error(f"Failed to save locally: {e}")
             return "error_save"

    def get_history(self, limit=10):
        # 1. Try MongoDB
        if not self.offline_mode and self.collection is not None:
            try:
                cursor = self.collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
                return list(cursor)
            except Exception as e:
                logger.error(f"Failed to fetch history from DB: {e}")
        
        # 2. Local File Fallback
        try:
            with open(self.local_file, 'r') as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    return []
                # Sort by timestamp descending (newest first)
                history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                return history[:limit]
        except Exception:
            return []

db_service = DBService()
