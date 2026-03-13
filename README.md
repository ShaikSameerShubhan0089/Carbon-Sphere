# CarbonSphere AI 🌍
> **Enterprise-Grade AI Forest Carbon Credit Platform**

## 🚀 Overview
CarbonSphere AI is a scalable, real-time system for estimating forest carbon credits using:
- 🛰️ **Satellite Imagery** (Sentinel-2 via Google Earth Engine)
- 🧠 **Deep Learning** (Tree Canopy Segmentation)
- 📍 **GIS Spatial Analysis**
- 📊 **IPCC-Compliant Carbon Modelling**

## 📂 Project Structure
```
carbon_sphere_ai/
├── backend/                # FastAPI Backend
│   ├── api/                # API Routes & Endpoints
│   ├── models/             # Pydantic Schemas
│   ├── services/           # Business Logic (GEE, AI, Carbon)
│   ├── utils/              # Helper utilities
│   └── main.py             # Server Entry Point
├── frontend/               # Web Dashboard
│   ├── index.html          # Main User Interface
│   ├── style.css           # Styling
│   └── script.js           # Logic & API Integration
├── requirements.txt        # Python Dependencies
├── run_app.bat             # ONE-CLICK RUN SCRIPT (Windows)
└── README.md               # Documentation
```

## 🛠️ Setup & Installation (No Docker)

### Prerequisites
1.  **Python 3.10+** installed.
2.  **MongoDB** (Optional): If you have a remote URL, set `MONGODB_URL` in environment variables.

### ⚡ Quick Start (Windows)
Double-click **`run_app.bat`**. 
This will:
1.  Install Python dependencies.
2.  Start the Backend API (**localhost:8081**).
3.  Open the Frontend Dashboard in your browser.

### 💻 Manual Run
**1. Backend**
```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 2020 --reload
```

**2. Frontend**
Simply open `frontend/index.html` in your web browser.

## 📡 API Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/analyze` | Analyze forest area & calc carbon credits |
| `GET` | `/api/v1/history` | Retrieve historical analysis records |
