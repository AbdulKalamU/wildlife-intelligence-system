"""
Application Settings

Configuration settings for the wildlife monitoring system.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = DATA_DIR / "models"
VIDEOS_DIR = DATA_DIR / "videos"
OUTPUTS_DIR = DATA_DIR / "outputs"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Model settings
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
CLASSIFIER_MODEL_PATH = os.getenv("CLASSIFIER_MODEL_PATH", None)

# Detection settings
DETECTION_CONFIDENCE_THRESHOLD = float(os.getenv("DETECTION_CONFIDENCE", "0.5"))
DETECTION_IOU_THRESHOLD = float(os.getenv("DETECTION_IOU", "0.45"))

# Classification settings
CLASSIFICATION_CONFIDENCE_THRESHOLD = float(os.getenv("CLASSIFICATION_CONFIDENCE", "0.6"))

# Tracking settings
MAX_DISAPPEARED_FRAMES = int(os.getenv("MAX_DISAPPEARED_FRAMES", "50"))

# Analytics settings
TREND_ANALYSIS_WINDOW_HOURS = int(os.getenv("TREND_WINDOW_HOURS", "24"))
RISK_ASSESSMENT_ENABLED = os.getenv("RISK_ASSESSMENT_ENABLED", "true").lower() == "true"

# Alert settings
ALERT_ENABLED = os.getenv("ALERT_ENABLED", "true").lower() == "true"
ENDANGERED_SPECIES = os.getenv("ENDANGERED_SPECIES", "").split(",")
ENDANGERED_SPECIES = [s.strip() for s in ENDANGERED_SPECIES if s.strip()]

# Dashboard settings
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))
DASHBOARD_REFRESH_RATE = float(os.getenv("DASHBOARD_REFRESH_RATE", "1.0"))

# Video processing settings
VIDEO_FRAME_SKIP = int(os.getenv("VIDEO_FRAME_SKIP", "1"))  # Process every Nth frame
VIDEO_RESIZE_WIDTH = int(os.getenv("VIDEO_RESIZE_WIDTH", "0"))  # 0 = no resize
VIDEO_RESIZE_HEIGHT = int(os.getenv("VIDEO_RESIZE_HEIGHT", "0"))

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "wildlife_monitoring.log")

# Export settings
EXPORT_FORMAT = os.getenv("EXPORT_FORMAT", "json")  # json, csv, or both
EXPORT_DETECTIONS = os.getenv("EXPORT_DETECTIONS", "true").lower() == "true"
EXPORT_TRACKS = os.getenv("EXPORT_TRACKS", "true").lower() == "true"
EXPORT_ANALYTICS = os.getenv("EXPORT_ANALYTICS", "true").lower() == "true"
