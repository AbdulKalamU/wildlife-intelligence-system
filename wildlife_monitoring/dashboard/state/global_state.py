"""
Global State Manager - TRUE Singleton

CRITICAL: Module-level singleton that persists across Streamlit reruns.
This is the ONLY source of truth for application state.

NEVER create AppState() anywhere else.
ALWAYS use get_app_state() to access the singleton.
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Dict, List
from collections import deque


@dataclass
class AppState:
    """
    Global application state - TRUE singleton.
    
    This instance persists across ALL Streamlit reruns.
    """
    # System initialization
    initialized: bool = False
    initializing: bool = False
    
    # Core components
    detector: Optional[Any] = None
    classifier: Optional[Any] = None
    tracker: Optional[Any] = None
    database: Optional[Any] = None
    analytics: Optional[Any] = None
    alerts: Optional[Any] = None
    
    # Live monitoring state
    processing: bool = False
    frame_number: int = 0
    video_source: Optional[tuple] = None
    current_frame: Optional[Any] = None
    current_detections: List[Dict] = field(default_factory=list)
    
    # Event logging
    event_log: deque = field(default_factory=lambda: deque(maxlen=100))
    track_zones: Dict[int, str] = field(default_factory=dict)
    
    # Zone statistics
    zone_stats: Dict[str, int] = field(default_factory=lambda: {'A': 0, 'B': 0, 'C': 0, 'D': 0})
    
    # Database path
    db_path: str = "wildlife_monitoring.db"
    
    # Configuration
    min_confidence: float = 0.5
    allowed_classes: set = field(default_factory=lambda: {
        "dog", "cat", "horse", "cow", "elephant",
        "bear", "zebra", "giraffe", "bird", "sheep"
    })


# CRITICAL: Module-level singleton - created ONCE when module is imported
_GLOBAL_APP_STATE = AppState()

print(f"[GLOBAL_STATE] Module loaded - Created singleton AppState: {id(_GLOBAL_APP_STATE)}")


def get_app_state() -> AppState:
    """
    Get the GLOBAL singleton AppState.
    
    CRITICAL: This returns the SAME instance across ALL Streamlit reruns.
    The instance is created at module import time and persists.
    
    Returns:
        The single global AppState instance
    """
    print(f"[GLOBAL_STATE] get_app_state() called - returning: {id(_GLOBAL_APP_STATE)}, initialized: {_GLOBAL_APP_STATE.initialized}")
    return _GLOBAL_APP_STATE


def initialize_system(app_state: AppState) -> bool:
    """
    Initialize all system components.
    
    Args:
        app_state: The global AppState singleton
        
    Returns:
        True if initialization successful, False otherwise
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"[INIT] {timestamp} - Starting initialization for AppState: {id(app_state)}")
    
    if app_state.initialized:
        print(f"[INIT] {timestamp} - Already initialized: {id(app_state)}")
        return True
    
    if app_state.initializing:
        print(f"[INIT] {timestamp} - Already initializing: {id(app_state)}")
        return False
    
    try:
        app_state.initializing = True
        print(f"[INIT] {timestamp} - Set initializing=True for: {id(app_state)}")
        
        # Import here to avoid circular dependencies
        from wildlife_monitoring.pipeline.modular_pipeline import create_modular_pipeline
        from wildlife_monitoring.database import WildlifeDatabase
        from wildlife_monitoring.analytics import SightingsAnalytics
        from wildlife_monitoring.alerts import AnalyticsAlertSystem, AlertConfig
        
        print(f"[INIT] {timestamp} - Creating pipeline components...")
        detector, classifier, tracker = create_modular_pipeline(
            yolo_model_path="yolov8n.pt",
            classification_enabled=True,
            allowed_animal_classes=app_state.allowed_classes
        )
        
        print(f"[INIT] {timestamp} - Creating database...")
        database = WildlifeDatabase(app_state.db_path)
        
        print(f"[INIT] {timestamp} - Creating analytics...")
        analytics = SightingsAnalytics(app_state.db_path)
        
        print(f"[INIT] {timestamp} - Creating alert system...")
        alert_config = AlertConfig(
            low_count_threshold=5,
            anomaly_spike_threshold=100.0,
            anomaly_min_count=3,
            decreasing_threshold=-10.0
        )
        alerts = AnalyticsAlertSystem(analytics, alert_config)
        
        # Update app state
        app_state.detector = detector
        app_state.classifier = classifier
        app_state.tracker = tracker
        app_state.database = database
        app_state.analytics = analytics
        app_state.alerts = alerts
        app_state.initialized = True
        app_state.initializing = False
        
        print(f"[INIT] {timestamp} - ✅ Initialization complete for: {id(app_state)}")
        print(f"[INIT] {timestamp} - app_state.initialized = {app_state.initialized}")
        
        return True
        
    except Exception as e:
        app_state.initializing = False
        print(f"[INIT] {timestamp} - ❌ Initialization failed: {e}")
        raise e


def reset_monitoring_state(app_state: AppState):
    """Reset monitoring-specific state."""
    app_state.processing = False
    app_state.frame_number = 0
    app_state.video_source = None
    app_state.current_frame = None
    app_state.current_detections = []
    app_state.event_log.clear()
    app_state.track_zones.clear()


def clear_database(app_state: AppState):
    """Clear database and reset related state."""
    if app_state.database:
        app_state.database.clear_all_sightings()
        reset_monitoring_state(app_state)
        app_state.zone_stats = {'A': 0, 'B': 0, 'C': 0, 'D': 0}


def get_database_stats(app_state: AppState) -> Dict[str, Any]:
    """Get database statistics."""
    if not app_state.database:
        return {
            'total_sightings': 0,
            'unique_species': 0,
            'unique_tracks': 0
        }
    
    try:
        return app_state.database.get_statistics()
    except:
        return {
            'total_sightings': 0,
            'unique_species': 0,
            'unique_tracks': 0
        }
