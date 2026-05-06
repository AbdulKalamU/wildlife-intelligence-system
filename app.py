"""
Wildlife Monitoring Intelligence Command Center

Professional command center dashboard with:
- Real-time detection and tracking
- Intelligent species classification
- Zone-based monitoring
- Advanced analytics and charts
- Sightings database
- Smart alert system
"""

import streamlit as st
import cv2
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
import tempfile
import time
import random
from collections import deque, defaultdict
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from wildlife_monitoring.pipeline.modular_pipeline import (
    create_modular_pipeline,
    process_frame_modular
)
from wildlife_monitoring.database import WildlifeDatabase
from wildlife_monitoring.database.pipeline_integration import save_pipeline_results_to_db
from wildlife_monitoring.database.demo_data import DemoDataGenerator
from wildlife_monitoring.analytics import SightingsAnalytics
from wildlife_monitoring.alerts import AnalyticsAlertSystem, AlertConfig


# Page configuration
st.set_page_config(
    page_title="Wildlife Intelligence Command Center",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Intelligent species mapping (YOLO class -> Wildlife species)
SPECIES_MAPPING = {
    "dog": "Labrador Retriever",
    "cat": "Leopard Cat",
    "bird": "Eagle",
    "horse": "Wild Horse",
    "cow": "Bison",
    "elephant": "African Elephant",
    "bear": "Grizzly Bear",
    "zebra": "Plains Zebra",
    "giraffe": "Masai Giraffe",
    "sheep": "Bighorn Sheep"
}

# Custom CSS for command center aesthetic
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    
    /* Command center header */
    h1 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
    }
    
    h2 {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c2c2c;
        margin-bottom: 0.5rem;
    }
    
    h3 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #3c3c3c;
        margin-bottom: 0.5rem;
    }
    
    /* Summary metrics */
    .summary-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.25rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #f0f0f0;
        margin-top: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Species card */
    .species-item {
        background-color: #f8f9fa;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #28a745;
        transition: all 0.2s;
    }
    
    .species-item:hover {
        background-color: #e9ecef;
        transform: translateX(4px);
    }
    
    .species-name {
        font-weight: 600;
        color: #1f1f1f;
        font-size: 0.95rem;
    }
    
    .species-count {
        font-size: 1.5rem;
        font-weight: 700;
        color: #28a745;
    }
    
    /* Zone card */
    .zone-item {
        background-color: #f8f9fa;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #007bff;
        transition: all 0.2s;
    }
    
    .zone-item:hover {
        background-color: #e9ecef;
        transform: translateX(4px);
    }
    
    .zone-name {
        font-weight: 600;
        color: #1f1f1f;
        font-size: 0.95rem;
    }
    
    .zone-count {
        font-size: 1.5rem;
        font-weight: 700;
        color: #007bff;
    }
    
    /* Alert cards */
    .alert-critical {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .alert-high {
        background-color: #fee;
        border-left: 4px solid #dc3545;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 6px;
    }
    
    .alert-medium {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 6px;
    }
    
    .alert-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.25rem;
    }
    
    .alert-message {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    /* Event log */
    .event-item {
        padding: 0.6rem 0.75rem;
        border-bottom: 1px solid #e9ecef;
        font-size: 0.9rem;
        transition: background-color 0.2s;
    }
    
    .event-item:hover {
        background-color: #f8f9fa;
    }
    
    .event-time {
        color: #666;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .event-species {
        font-weight: 600;
        color: #1f1f1f;
    }
    
    .event-zone {
        color: #007bff;
        font-weight: 600;
    }
    
    /* Sightings table */
    .dataframe {
        font-size: 0.85rem;
    }
    
    /* Section dividers */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 2px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)


# Zone definitions (divide frame into 4 quadrants)
ZONES = {
    'A': {'name': 'Zone A', 'color': (255, 0, 0)},      # Red - Top Left
    'B': {'name': 'Zone B', 'color': (0, 255, 0)},      # Green - Top Right
    'C': {'name': 'Zone C', 'color': (0, 0, 255)},      # Blue - Bottom Left
    'D': {'name': 'Zone D', 'color': (255, 255, 0)}     # Yellow - Bottom Right
}


def initialize_session_state():
    """Initialize session state variables."""
    if 'detector' not in st.session_state:
        st.session_state.detector = None
    if 'classifier' not in st.session_state:
        st.session_state.classifier = None
    if 'tracker' not in st.session_state:
        st.session_state.tracker = None
    if 'db' not in st.session_state:
        st.session_state.db = None
    if 'analytics' not in st.session_state:
        st.session_state.analytics = None
    if 'alert_system' not in st.session_state:
        st.session_state.alert_system = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'frame_number' not in st.session_state:
        st.session_state.frame_number = 0
    if 'video_source' not in st.session_state:
        st.session_state.video_source = None
    if 'event_log' not in st.session_state:
        st.session_state.event_log = deque(maxlen=100)
    if 'sightings_log' not in st.session_state:
        st.session_state.sightings_log = []
    if 'track_history' not in st.session_state:
        st.session_state.track_history = {}  # track_id -> {last_zone, last_species, last_seen}
    if 'alert_history' not in st.session_state:
        st.session_state.alert_history = {}  # Changed from set to dict for timestamp tracking
    if 'detection_timeline' not in st.session_state:
        st.session_state.detection_timeline = deque(maxlen=100)  # (timestamp, count)
    if 'demo_data_loaded' not in st.session_state:
        st.session_state.demo_data_loaded = False


@st.cache_resource
def load_models():
    """Load models with caching for performance optimization."""
    try:
        detector, classifier, tracker = create_modular_pipeline(
            yolo_model_path="yolov8n.pt",
            classification_enabled=True,
            allowed_animal_classes={
                "dog", "cat", "horse", "cow", "elephant", 
                "bear", "zebra", "giraffe", "bird", "sheep"
            }
        )
        return detector, classifier, tracker
    except Exception as e:
        st.error(f"Failed to load models: {e}")
        return None, None, None


def initialize_system(db_path="wildlife_monitoring.db"):
    """Initialize all system components with cached model loading."""
    try:
        # Load models with caching
        detector, classifier, tracker = load_models()
        
        if detector is None or classifier is None or tracker is None:
            return False
        
        # Initialize database
        db = WildlifeDatabase(db_path)
        
        # Initialize analytics
        analytics = SightingsAnalytics(db_path)
        
        # Initialize alert system
        alert_config = AlertConfig(
            low_count_threshold=5,
            anomaly_spike_threshold=100.0,
            anomaly_min_count=3,
            decreasing_threshold=-10.0
        )
        alert_system = AnalyticsAlertSystem(analytics, alert_config)
        
        # Store in session state
        st.session_state.detector = detector
        st.session_state.classifier = classifier
        st.session_state.tracker = tracker
        st.session_state.db = db
        st.session_state.analytics = analytics
        st.session_state.alert_system = alert_system
        
        return True
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")
        return False


def load_demo_data():
    """Load demo data into the database for demonstration."""
    try:
        generator = DemoDataGenerator("wildlife_monitoring.db")
        count = generator.load_demo_data_to_db(count=150)
        
        # Generate demo events
        demo_events = generator.generate_demo_events(count=50)
        
        # Add events to session state
        for event in demo_events:
            st.session_state.event_log.appendleft(event)
        
        # Generate demo timeline
        base_time = datetime.now() - timedelta(hours=1)
        for i in range(50):
            timestamp = base_time + timedelta(minutes=i * 1.2)
            count_val = random.randint(2, 8)
            st.session_state.detection_timeline.append((timestamp, count_val))
        
        st.session_state.demo_data_loaded = True
        
        return count
    except Exception as e:
        st.error(f"Failed to load demo data: {e}")
        return 0


def get_zone_from_bbox(bbox, frame_width, frame_height):
    """
    Determine which zone a bounding box is in.
    
    Args:
        bbox: [x1, y1, x2, y2]
        frame_width: Frame width
        frame_height: Frame height
    
    Returns:
        Zone letter ('A', 'B', 'C', or 'D')
    """
    x1, y1, x2, y2 = bbox
    
    # Calculate center point
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    
    # Determine zone based on center point
    mid_x = frame_width / 2
    mid_y = frame_height / 2
    
    if center_x < mid_x and center_y < mid_y:
        return 'A'  # Top Left
    elif center_x >= mid_x and center_y < mid_y:
        return 'B'  # Top Right
    elif center_x < mid_x and center_y >= mid_y:
        return 'C'  # Bottom Left
    else:
        return 'D'  # Bottom Right


def map_species_name(yolo_class, confidence):
    """
    Map YOLO class to wildlife species name.
    
    Args:
        yolo_class: YOLO detected class
        confidence: Detection confidence
    
    Returns:
        Mapped species name
    """
    if yolo_class.lower() == "unknown" or confidence < 0.3:
        return "Unverified Species"
    
    return SPECIES_MAPPING.get(yolo_class.lower(), yolo_class.title())


def generate_smart_alert(track_id, species, zone, confidence, track_history):
    """
    Generate intelligent, meaningful alerts.
    
    Args:
        track_id: Track ID
        species: Species name
        zone: Current zone
        confidence: Detection confidence
        track_history: Track history dict
    
    Returns:
        Alert dict or None
    """
    alerts = []
    
    # Restricted zone intrusion (Zone D is restricted)
    if zone == 'D' and track_id not in track_history:
        alerts.append({
            'type': 'RESTRICTED_ZONE',
            'severity': 'critical',
            'message': f'{species} entered Restricted Zone D',
            'emoji': '🚨'
        })
    
    # Human detection (if person class is detected)
    if species.lower() in ['person', 'human']:
        alerts.append({
            'type': 'HUMAN_DETECTED',
            'severity': 'critical',
            'message': f'Human detected in Zone {zone}',
            'emoji': '👤'
        })
    
    # Low confidence detection
    if confidence < 0.5:
        alerts.append({
            'type': 'LOW_CONFIDENCE',
            'severity': 'medium',
            'message': f'Low confidence detection: {species} ({confidence:.1%})',
            'emoji': '⚠️'
        })
    
    # Rare species (example: Eagle, Grizzly Bear)
    if species in ['Eagle', 'Grizzly Bear', 'African Elephant']:
        if track_id not in track_history:
            alerts.append({
                'type': 'RARE_SPECIES',
                'severity': 'high',
                'message': f'Rare species detected: {species}',
                'emoji': '⭐'
            })
    
    # Zone transition
    if track_id in track_history:
        last_zone = track_history[track_id].get('last_zone')
        if last_zone and last_zone != zone:
            alerts.append({
                'type': 'ZONE_TRANSITION',
                'severity': 'low',
                'message': f'{species} moved from Zone {last_zone} to Zone {zone}',
                'emoji': '🔄'
            })
    
    return alerts if alerts else None


def draw_zones_and_tracks(frame, tracks, classifications, frame_width, frame_height):
    """
    Draw zone boundaries and track IDs on frame with species labels.
    
    Args:
        frame: Video frame
        tracks: Dictionary of tracks
        classifications: Dictionary of classifications
        frame_width: Frame width
        frame_height: Frame height
    
    Returns:
        Annotated frame
    """
    annotated = frame.copy()
    
    # Draw zone boundaries (semi-transparent lines)
    mid_x = frame_width // 2
    mid_y = frame_height // 2
    
    # Vertical line
    cv2.line(annotated, (mid_x, 0), (mid_x, frame_height), (200, 200, 200), 2)
    
    # Horizontal line
    cv2.line(annotated, (0, mid_y), (frame_width, mid_y), (200, 200, 200), 2)
    
    # Draw zone labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(annotated, "Zone A", (20, 30), font, 0.7, ZONES['A']['color'], 2)
    cv2.putText(annotated, "Zone B", (mid_x + 20, 30), font, 0.7, ZONES['B']['color'], 2)
    cv2.putText(annotated, "Zone C", (20, mid_y + 30), font, 0.7, ZONES['C']['color'], 2)
    cv2.putText(annotated, "Zone D", (mid_x + 20, mid_y + 30), font, 0.7, ZONES['D']['color'], 2)
    
    # Draw track IDs and species on bounding boxes
    for track_id, track_info in tracks.items():
        bbox = track_info['bbox']
        x1, y1, x2, y2 = map(int, bbox)
        
        # Get zone
        zone = get_zone_from_bbox(bbox, frame_width, frame_height)
        zone_color = ZONES[zone]['color']
        
        # Get species from classification
        species = "Unverified Species"
        confidence = 0.0
        for det_idx, cls in classifications.items():
            if not cls.get('is_unknown', False) and cls.get('confidence', 0) >= 0.3:
                yolo_class = cls['species']
                confidence = cls['confidence']
                species = map_species_name(yolo_class, confidence)
                break
        
        # Draw bounding box with zone color
        cv2.rectangle(annotated, (x1, y1), (x2, y2), zone_color, 2)
        
        # Draw track ID, species, and zone label
        label = f"Track {track_id:02d} • {species} • Zone {zone}"
        label_size = cv2.getTextSize(label, font, 0.5, 2)[0]
        
        # Background for label
        cv2.rectangle(
            annotated,
            (x1, y1 - label_size[1] - 10),
            (x1 + label_size[0] + 10, y1),
            zone_color,
            -1
        )
        
        # Label text
        cv2.putText(
            annotated,
            label,
            (x1 + 5, y1 - 5),
            font,
            0.5,
            (255, 255, 255),
            2
        )
        
        # Draw confidence bar
        conf_width = int((x2 - x1) * confidence)
        cv2.rectangle(annotated, (x1, y2 + 2), (x1 + conf_width, y2 + 8), zone_color, -1)
    
    return annotated


def add_event_to_log(species, zone, track_id, event_type="detection"):
    """
    Add event to the event log with intelligent deduplication.
    
    Args:
        species: Species name
        zone: Zone letter
        track_id: Track ID
        event_type: Type of event (detection, zone_change, alert)
    """
    # Create event key for deduplication
    event_key = f"{track_id}_{species}_{zone}_{event_type}"
    
    # Check if this is a new track
    if track_id not in st.session_state.track_history:
        # New track - log it
        event = {
            'timestamp': datetime.now(),
            'species': species,
            'zone': zone,
            'track_id': track_id,
            'type': 'new_track',
            'message': f"{species} entered Zone {zone}"
        }
        st.session_state.event_log.appendleft(event)
        st.session_state.track_history[track_id] = {
            'last_zone': zone,
            'last_species': species,
            'last_seen': datetime.now()
        }
    else:
        # Existing track - check for zone change
        last_zone = st.session_state.track_history[track_id].get('last_zone')
        if last_zone and last_zone != zone:
            event = {
                'timestamp': datetime.now(),
                'species': species,
                'zone': zone,
                'track_id': track_id,
                'type': 'zone_change',
                'message': f"{species} moved from Zone {last_zone} to Zone {zone}"
            }
            st.session_state.event_log.appendleft(event)
            st.session_state.track_history[track_id]['last_zone'] = zone
        
        # Update last seen
        st.session_state.track_history[track_id]['last_seen'] = datetime.now()


def add_alert_to_log(alert_dict):
    """
    Add alert to event log with deduplication.
    
    Args:
        alert_dict: Alert dictionary
    """
    alert_key = f"{alert_dict['type']}_{alert_dict['message']}"
    
    # Deduplicate - only add if not seen in last 30 seconds
    current_time = datetime.now()
    
    # Clean old alerts from history (older than 30 seconds)
    st.session_state.alert_history = {
        k: v for k, v in st.session_state.alert_history.items()
        if (current_time - v).total_seconds() < 30
    }
    
    if alert_key not in st.session_state.alert_history:
        event = {
            'timestamp': current_time,
            'species': alert_dict.get('species', 'System'),
            'zone': alert_dict.get('zone', '-'),
            'track_id': alert_dict.get('track_id', '-'),
            'type': 'alert',
            'message': f"{alert_dict['emoji']} {alert_dict['message']}"
        }
        st.session_state.event_log.appendleft(event)
        st.session_state.alert_history[alert_key] = current_time


def process_frame_and_update(frame, frame_number):
    """Process a single frame and update database/analytics with smart features."""
    frame_height, frame_width = frame.shape[:2]
    
    # Process frame through pipeline
    state = process_frame_modular(
        frame=frame,
        frame_number=frame_number,
        detector=st.session_state.detector,
        classifier=st.session_state.classifier,
        tracker=st.session_state.tracker,
        allowed_classes={
            "dog", "cat", "horse", "cow", "elephant",
            "bear", "zebra", "giraffe", "bird", "sheep"
        },
        apply_filter=True,
        annotate=False  # We'll do custom annotation
    )
    
    # Draw zones and tracks with species labels
    if state.tracks:
        annotated_frame = draw_zones_and_tracks(
            frame,
            state.tracks,
            state.classifications,
            frame_width,
            frame_height
        )
    else:
        annotated_frame = frame.copy()
    
    # Process each track
    if len(state.tracks) > 0:
        for track_id, track_info in state.tracks.items():
            zone = get_zone_from_bbox(track_info['bbox'], frame_width, frame_height)
            
            # Get species from classification
            species = "Unverified Species"
            confidence = 0.0
            for det_idx, cls in state.classifications.items():
                if not cls.get('is_unknown', False) and cls.get('confidence', 0) >= 0.3:
                    yolo_class = cls['species']
                    confidence = cls['confidence']
                    species = map_species_name(yolo_class, confidence)
                    break
            
            # Add to event log (with deduplication)
            add_event_to_log(species, zone, track_id)
            
            # Generate smart alerts
            alerts = generate_smart_alert(track_id, species, zone, confidence, st.session_state.track_history)
            if alerts:
                for alert in alerts:
                    if alert['severity'] in ['critical', 'high']:  # Only log high-value alerts
                        alert['species'] = species
                        alert['zone'] = zone
                        alert['track_id'] = track_id
                        add_alert_to_log(alert)
            
            # Add to sightings log
            sighting = {
                'timestamp': datetime.now(),
                'species': species,
                'confidence': confidence,
                'zone': zone,
                'track_id': track_id,
                'frame_number': frame_number
            }
            st.session_state.sightings_log.append(sighting)
        
        # Save to database
        save_pipeline_results_to_db(
            st.session_state.db,
            state,
            timestamp=datetime.now()
        )
        
        # Update detection timeline
        st.session_state.detection_timeline.append((datetime.now(), len(state.tracks)))
    
    # Update state with annotated frame
    state.annotated_frame = annotated_frame
    
    return state


def get_dashboard_data():
    """Get all dashboard data (summary, species, zones, alerts)."""
    # Get analytics data (last 5 minutes)
    all_species = st.session_state.analytics.analyze_all_species(
        time_window_minutes=5,
        min_count=1
    )
    
    # Filter out unknown/unverified species and map names
    valid_species = []
    for s in all_species:
        if s.species.lower() not in ['unknown', 'unverified species']:
            mapped_name = map_species_name(s.species, 1.0)  # Assume high confidence for analytics
            valid_species.append({
                'species': mapped_name,
                'count': s.count,
                'trend': s.trend
            })
    
    # Get alerts (only meaningful ones)
    all_alerts = st.session_state.alert_system.generate_alerts_for_all_species(
        time_window_minutes=5,
        min_count=1
    )
    
    # Filter alerts (only high and medium, exclude stable)
    meaningful_alerts = [
        a for a in all_alerts 
        if a.severity in ['high', 'medium'] and a.alert != 'stable'
    ]
    
    # Calculate zone distribution from database (location field contains "Zone X")
    zone_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    try:
        recent_sightings = st.session_state.db.get_recent_sightings(limit=100)
        for sighting in recent_sightings:
            location = sighting.get('location', '')
            if location and location.startswith('Zone '):
                zone = location.split(' ')[1]
                if zone in zone_counts:
                    zone_counts[zone] += 1
    except:
        # Fallback to event log if database query fails
        for event in list(st.session_state.event_log)[:50]:
            zone = event.get('zone', 'A')
            if zone in zone_counts:
                zone_counts[zone] += 1
    
    # Calculate summary
    total_animals = sum(s['count'] for s in valid_species)
    total_species = len(valid_species)
    total_alerts = len([e for e in list(st.session_state.event_log)[:20] if e.get('type') == 'alert'])
    
    return {
        'summary': {
            'total_animals': total_animals,
            'total_species': total_species,
            'total_alerts': total_alerts
        },
        'species': valid_species,
        'zones': zone_counts,
        'alerts': meaningful_alerts
    }


def render_summary_bar(data):
    """Render top summary bar."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="summary-metric">
            <div class="metric-value">{data['summary']['total_animals']}</div>
            <div class="metric-label">Total Animals</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="summary-metric">
            <div class="metric-value">{data['summary']['total_species']}</div>
            <div class="metric-label">Species Detected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        alert_color = "#dc3545" if data['summary']['total_alerts'] > 0 else "#28a745"
        st.markdown(f"""
        <div class="summary-metric">
            <div class="metric-value" style="color: {alert_color};">{data['summary']['total_alerts']}</div>
            <div class="metric-label">Active Alerts</div>
        </div>
        """, unsafe_allow_html=True)


def render_species_counts(species_list):
    """Render species counts."""
    if species_list:
        for species_data in species_list:
            trend_emoji = ""
            if species_data.get('trend') == 'increasing':
                trend_emoji = "📈"
            elif species_data.get('trend') == 'decreasing':
                trend_emoji = "📉"
            else:
                trend_emoji = "➡️"
            
            st.markdown(f"""
            <div class="species-item">
                <span class="species-name">{trend_emoji} {species_data['species']}</span>
                <span class="species-count">{species_data['count']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No species detected")


def render_zone_distribution(zone_counts):
    """Render zone distribution."""
    for zone_id in ['A', 'B', 'C', 'D']:
        count = zone_counts.get(zone_id, 0)
        st.markdown(f"""
        <div class="zone-item">
            <span class="zone-name">Zone {zone_id}</span>
            <span class="zone-count">{count}</span>
        </div>
        """, unsafe_allow_html=True)


def render_alerts(alerts):
    """Render alerts panel with smart filtering."""
    # Get recent alert events from event log
    alert_events = [e for e in list(st.session_state.event_log)[:20] if e.get('type') == 'alert']
    
    # Filter out empty or invalid alerts
    valid_alerts = []
    for event in alert_events:
        message = event.get('message', '').strip()
        # Skip if message is empty or just an emoji
        if message and len(message) > 2 and not message.isspace():
            valid_alerts.append(event)
    
    if valid_alerts:
        for event in valid_alerts[:5]:  # Show top 5
            # Determine severity from message
            message = event.get('message', '')
            if '🚨' in message or 'Restricted' in message or 'Human' in message:
                severity_class = "alert-critical"
            elif '⭐' in message or 'Rare' in message:
                severity_class = "alert-high"
            else:
                severity_class = "alert-medium"
            
            time_str = event['timestamp'].strftime("%H:%M:%S")
            
            st.markdown(f"""
            <div class="{severity_class}">
                <div class="alert-title">{message}</div>
                <div class="alert-message">Zone {event.get('zone', '-')} • Track ID: {event.get('track_id', '-')} • {time_str}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No active alerts")


def render_event_log(events):
    """Render event log with formatted messages."""
    if events:
        for event in list(events)[:15]:  # Show last 15
            time_str = event['timestamp'].strftime("%H:%M:%S")
            message = event.get('message', f"{event.get('species', 'Unknown')} in Zone {event.get('zone', '-')}")
            
            st.markdown(f"""
            <div class="event-item">
                <span class="event-time">[{time_str}]</span> {message}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No events yet")


def render_species_chart(species_list):
    """Render species distribution bar chart."""
    if species_list and len(species_list) > 0:
        df = pd.DataFrame(species_list)
        fig = px.bar(
            df,
            x='species',
            y='count',
            title="Species Distribution",
            labels={'species': 'Species', 'count': 'Count'},
            color='count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No species data available")


def render_zone_chart(zone_counts):
    """Render zone activity bar chart."""
    if zone_counts and sum(zone_counts.values()) > 0:
        df = pd.DataFrame([
            {'Zone': f'Zone {k}', 'Count': v}
            for k, v in zone_counts.items()
        ])
        fig = px.bar(
            df,
            x='Zone',
            y='Count',
            title="Zone Activity",
            labels={'Zone': 'Zone', 'Count': 'Detections'},
            color='Count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No zone data available")


def render_detection_timeline():
    """Render detection timeline chart."""
    if st.session_state.detection_timeline and len(st.session_state.detection_timeline) > 1:
        timeline_data = list(st.session_state.detection_timeline)
        df = pd.DataFrame(timeline_data, columns=['timestamp', 'count'])
        
        fig = px.line(
            df,
            x='timestamp',
            y='count',
            title="Detection Timeline",
            labels={'timestamp': 'Time', 'count': 'Active Tracks'}
        )
        fig.update_layout(
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        fig.update_traces(line_color='#00d4ff', line_width=2)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No timeline data available")


def render_confidence_distribution():
    """Render confidence distribution histogram."""
    # Try to get from database first
    try:
        db_sightings = st.session_state.db.get_recent_sightings(limit=100)
        if db_sightings and len(db_sightings) > 0:
            confidences = [s['confidence'] for s in db_sightings]
            df = pd.DataFrame({'confidence': confidences})
            
            fig = px.histogram(
                df,
                x='confidence',
                nbins=20,
                title="Confidence Distribution",
                labels={'confidence': 'Confidence', 'count': 'Frequency'}
            )
            fig.update_layout(
                template='plotly_dark',
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False
            )
            fig.update_traces(marker_color='#ff6b6b')
            st.plotly_chart(fig, use_container_width=True)
            return
    except Exception as e:
        # Fall back to session state
        pass
    
    # Fallback: use session state sightings_log
    if st.session_state.sightings_log and len(st.session_state.sightings_log) > 0:
        df = pd.DataFrame(st.session_state.sightings_log)
        fig = px.histogram(
            df,
            x='confidence',
            nbins=20,
            title="Confidence Distribution",
            labels={'confidence': 'Confidence', 'count': 'Frequency'}
        )
        fig.update_layout(
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        fig.update_traces(marker_color='#ff6b6b')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No confidence data available")


def render_sightings_table():
    """Render recent sightings database table."""
    # Try to get from database first
    try:
        db_sightings = st.session_state.db.get_recent_sightings(limit=50)
        if db_sightings and len(db_sightings) > 0:
            # Convert to DataFrame
            df_data = []
            for s in db_sightings:
                # Extract zone from location field
                location = s.get('location', '')
                zone = location.split(' ')[1] if location and location.startswith('Zone ') else '-'
                
                df_data.append({
                    'Time': datetime.fromisoformat(s['timestamp']).strftime('%H:%M:%S'),
                    'Species': s['species'],
                    'Confidence': f"{s['confidence']:.1%}",
                    'Zone': zone,
                    'Track ID': s['track_id']
                })
            
            df = pd.DataFrame(df_data)
            
            # Display table
            st.dataframe(df, use_container_width=True, height=300)
            
            # Export buttons
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Export CSV",
                    data=csv,
                    file_name=f"sightings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                json_data = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="Export JSON",
                    data=json_data,
                    file_name=f"sightings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            return
    except Exception as e:
        # Fall back to session state sightings_log
        pass
    
    # Fallback: use session state sightings_log
    if st.session_state.sightings_log and len(st.session_state.sightings_log) > 0:
        # Get last 50 sightings
        recent_sightings = st.session_state.sightings_log[-50:]
        df = pd.DataFrame(recent_sightings)
        
        # Format timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
        
        # Format confidence as percentage
        df['confidence'] = df['confidence'].apply(lambda x: f"{x:.1%}")
        
        # Reorder columns
        df = df[['timestamp', 'species', 'confidence', 'zone', 'track_id']]
        df.columns = ['Time', 'Species', 'Confidence', 'Zone', 'Track ID']
        
        # Display table
        st.dataframe(df, use_container_width=True, height=300)
        
        # Export buttons
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Export CSV",
                data=csv,
                file_name=f"sightings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col2:
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="Export JSON",
                data=json_data,
                file_name=f"sightings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("No sightings recorded yet")


def process_webcam(video_placeholder, dashboard_placeholder, camera_index=0):
    """Process webcam feed with cloud environment safety."""
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            st.error("Webcam unavailable in cloud environment. Please upload image or video.")
            st.info("💡 Tip: Use the 'Upload' option to process video files instead.")
            st.session_state.processing = False
            return
    except Exception as e:
        st.error("Webcam unavailable in cloud environment. Please upload image or video.")
        st.info("💡 Tip: Use the 'Upload' option to process video files instead.")
        st.session_state.processing = False
        return
    
    try:
        while st.session_state.processing:
            ret, frame = cap.read()
            
            if not ret:
                st.error("Failed to read from camera")
                st.session_state.processing = False
                break
            
            st.session_state.frame_number += 1
            
            # Process frame
            state = process_frame_and_update(frame, st.session_state.frame_number)
            
            # Display annotated frame
            if state.annotated_frame is not None:
                display_frame = cv2.cvtColor(state.annotated_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(display_frame, channels="RGB", use_container_width=True)
            
            # Update dashboard every 30 frames
            if st.session_state.frame_number % 30 == 0:
                update_dashboard(dashboard_placeholder)
            
            time.sleep(0.03)  # ~30 FPS
    
    finally:
        cap.release()


def process_video_file(video_file, video_placeholder, dashboard_placeholder):
    """Process uploaded video file."""
    # Save to temp file
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(video_file.read())
    video_path = tfile.name
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        st.error("Failed to open video file")
        return
    
    try:
        while st.session_state.processing:
            ret, frame = cap.read()
            
            if not ret:
                st.session_state.processing = False
                st.success("Video processing complete")
                break
            
            st.session_state.frame_number += 1
            
            # Process frame
            state = process_frame_and_update(frame, st.session_state.frame_number)
            
            # Display annotated frame
            if state.annotated_frame is not None:
                display_frame = cv2.cvtColor(state.annotated_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(display_frame, channels="RGB", use_container_width=True)
            
            # Update dashboard every 30 frames
            if st.session_state.frame_number % 30 == 0:
                update_dashboard(dashboard_placeholder)
            
            time.sleep(0.01)
    
    finally:
        cap.release()
        Path(video_path).unlink(missing_ok=True)


def update_dashboard(dashboard_placeholder):
    """Update the dashboard with latest data."""
    data = get_dashboard_data()
    
    with dashboard_placeholder.container():
        # Summary bar
        render_summary_bar(data)
        
        st.markdown("---")
        
        # Two columns for species and zones
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Species Analysis")
            render_species_counts(data['species'])
        
        with col2:
            st.markdown("### Zone Monitoring")
            render_zone_distribution(data['zones'])
        
        st.markdown("---")
        
        # Alerts
        st.markdown("### System Alerts")
        render_alerts(data['alerts'])
        
        st.markdown("---")
        
        # Event log
        st.markdown("### Event Log")
        render_event_log(st.session_state.event_log)


def main():
    """Main application - Wildlife Intelligence Command Center."""
    initialize_session_state()
    
    # Header
    st.title("Wildlife Intelligence Command Center")
    st.markdown("Real-time Detection • Zone Monitoring • Advanced Analytics")
    
    # Show demo data suggestion on first load
    if not st.session_state.demo_data_loaded:
        st.info("👋 **Welcome!** Click '📊 Load Demo Data' to see the dashboard with sample wildlife sightings, or upload your own video to start monitoring.")
    
    st.markdown("")
    
    # Initialize system if not already done
    if st.session_state.detector is None:
        with st.spinner("Initializing intelligence systems..."):
            if not initialize_system():
                st.stop()
    
    # Control panel (compact)
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1.5, 1.5])
    
    with col1:
        source_type = st.selectbox("Source", ["Webcam", "Upload"], label_visibility="collapsed")
    
    with col2:
        if source_type == "Webcam":
            camera_index = st.number_input("Camera", 0, 10, 0, label_visibility="collapsed")
            st.session_state.video_source = ('camera', camera_index)
        else:
            video_file = st.file_uploader("Video", type=["mp4", "avi", "mov"], label_visibility="collapsed")
            if video_file:
                st.session_state.video_source = ('file', video_file)
    
    with col3:
        start_disabled = (st.session_state.video_source is None or st.session_state.processing)
        if st.button("▶️ Start", disabled=start_disabled, use_container_width=True):
            st.session_state.processing = True
            st.session_state.frame_number = 0
            st.session_state.event_log.clear()
            st.session_state.track_history.clear()
            st.session_state.alert_history.clear()
            st.rerun()
    
    with col4:
        if st.button("⏸️ Stop", disabled=not st.session_state.processing, use_container_width=True):
            st.session_state.processing = False
            st.rerun()
    
    with col5:
        if st.button("📊 Load Demo Data", use_container_width=True, type="primary"):
            with st.spinner("Loading demo data..."):
                count = load_demo_data()
                if count > 0:
                    st.success(f"✅ Loaded {count} demo sightings!")
                    st.rerun()
    
    with col6:
        if st.button("🔄 Clear All Data", use_container_width=True):
            st.session_state.db.clear_all_sightings()
            st.session_state.frame_number = 0
            st.session_state.event_log.clear()
            st.session_state.sightings_log.clear()
            st.session_state.track_history.clear()
            st.session_state.alert_history.clear()
            st.session_state.detection_timeline.clear()
            st.session_state.demo_data_loaded = False
            st.success("All data cleared!")
            st.rerun()
    
    st.markdown("")
    
    # Dynamic layout based on processing state
    if st.session_state.processing:
        # When processing: Video (left 2/3) | Dashboard (right 1/3)
        col_video, col_dashboard = st.columns([2, 1])
        
        with col_video:
            st.markdown("### Live Feed")
            video_placeholder = st.empty()
        
        with col_dashboard:
            st.markdown("### Intelligence Dashboard")
            dashboard_placeholder = st.empty()
    else:
        # When not processing: Show dashboard in full width with compact video placeholder
        st.markdown("### Live Feed")
        video_placeholder = st.empty()
        video_placeholder.info("Click 'Start' to begin monitoring")
        
        st.markdown("---")
        st.markdown("### Intelligence Dashboard")
        dashboard_placeholder = st.container()
        
        # Show initial dashboard in full width
        update_dashboard(dashboard_placeholder)
    
    # Process video if started
    if st.session_state.processing and st.session_state.video_source:
        source_type, source_data = st.session_state.video_source
        
        if source_type == 'camera':
            process_webcam(video_placeholder, dashboard_placeholder, source_data)
        elif source_type == 'file':
            process_video_file(source_data, video_placeholder, dashboard_placeholder)
    
    # Analytics Section (below video feed)
    st.markdown("---")
    st.markdown("## Advanced Analytics")
    
    # Get current data
    data = get_dashboard_data()
    
    # Charts row 1: Species and Zone
    col1, col2 = st.columns(2)
    with col1:
        render_species_chart(data['species'])
    with col2:
        render_zone_chart(data['zones'])
    
    # Charts row 2: Timeline and Confidence
    col1, col2 = st.columns(2)
    with col1:
        render_detection_timeline()
    with col2:
        render_confidence_distribution()
    
    # Sightings Database Table
    st.markdown("---")
    st.markdown("## Sightings Database")
    render_sightings_table()
    
    # Footer
    st.markdown("""
    <div class="footer">
        Wildlife Intelligence Command Center • YOLOv8 • DeepSORT • ResNet50
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
