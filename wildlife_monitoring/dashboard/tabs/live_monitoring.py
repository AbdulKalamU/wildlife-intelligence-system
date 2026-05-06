"""
Live Monitoring Tab

Real-time wildlife detection and tracking.

CRITICAL: ALWAYS use get_app_state() - NEVER create AppState()
"""

import streamlit as st
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import tempfile
import time
from collections import deque
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from wildlife_monitoring.pipeline.modular_pipeline import process_frame_modular
from wildlife_monitoring.database.pipeline_integration import save_pipeline_results_to_db
from wildlife_monitoring.dashboard.state import get_app_state


MIN_CONFIDENCE = 0.5

ZONES = {
    'A': {'color': (200, 50, 50)},
    'B': {'color': (50, 200, 50)},
    'C': {'color': (50, 50, 200)},
    'D': {'color': (200, 200, 50)}
}


def get_zone_from_bbox(bbox, frame_width, frame_height):
    """Determine zone from bounding box center point."""
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    
    mid_x = frame_width / 2
    mid_y = frame_height / 2
    
    if center_x < mid_x and center_y < mid_y:
        return 'A'
    elif center_x >= mid_x and center_y < mid_y:
        return 'B'
    elif center_x < mid_x and center_y >= mid_y:
        return 'C'
    else:
        return 'D'


def draw_zones_and_tracks(frame, tracks, frame_width, frame_height):
    """Draw zone boundaries and track IDs."""
    annotated = frame.copy()
    
    mid_x = frame_width // 2
    mid_y = frame_height // 2
    
    # Draw zone boundaries
    cv2.line(annotated, (mid_x, 0), (mid_x, frame_height), (180, 180, 180), 1)
    cv2.line(annotated, (0, mid_y), (frame_width, mid_y), (180, 180, 180), 1)
    
    # Draw zone labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(annotated, "A", (10, 20), font, 0.5, (100, 100, 100), 1)
    cv2.putText(annotated, "B", (mid_x + 10, 20), font, 0.5, (100, 100, 100), 1)
    cv2.putText(annotated, "C", (10, mid_y + 20), font, 0.5, (100, 100, 100), 1)
    cv2.putText(annotated, "D", (mid_x + 10, mid_y + 20), font, 0.5, (100, 100, 100), 1)
    
    # Draw tracks
    for track_id, track_info in tracks.items():
        bbox = track_info['bbox']
        x1, y1, x2, y2 = map(int, bbox)
        
        zone = get_zone_from_bbox(bbox, frame_width, frame_height)
        zone_color = ZONES[zone]['color']
        
        cv2.rectangle(annotated, (x1, y1), (x2, y2), zone_color, 2)
        
        label = f"ID:{track_id} [{zone}]"
        label_size = cv2.getTextSize(label, font, 0.5, 1)[0]
        
        cv2.rectangle(
            annotated,
            (x1, y1 - label_size[1] - 6),
            (x1 + label_size[0] + 6, y1),
            zone_color,
            -1
        )
        
        cv2.putText(
            annotated,
            label,
            (x1 + 3, y1 - 3),
            font,
            0.5,
            (255, 255, 255),
            1
        )
    
    return annotated


def log_event(event_type, species, zone, track_id, old_zone=None):
    """Log meaningful events only."""
    app_state = get_app_state()
    timestamp = datetime.now()
    
    if event_type == "new_track":
        message = f"{species} entered Zone {zone}"
    elif event_type == "zone_transition":
        message = f"{species} moved Zone {old_zone} -> Zone {zone}"
    else:
        return
    
    event = {
        'timestamp': timestamp,
        'message': message,
        'track_id': track_id
    }
    
    app_state.event_log.appendleft(event)


def process_frame_and_update(frame, frame_number):
    """Process frame with proper filtering and event logging."""
    app_state = get_app_state()
    frame_height, frame_width = frame.shape[:2]
    
    state = process_frame_modular(
        frame=frame,
        frame_number=frame_number,
        detector=app_state.detector,
        classifier=app_state.classifier,
        tracker=app_state.tracker,
        allowed_classes=app_state.allowed_classes,
        apply_filter=True,
        annotate=False
    )
    
    # Filter out low confidence and unknown species
    valid_tracks = {}
    for track_id, track_info in state.tracks.items():
        species = None
        confidence = 0.0
        
        for det_idx, cls in state.classifications.items():
            if not cls.get('is_unknown', False) and cls.get('confidence', 0) >= MIN_CONFIDENCE:
                species = cls['species']
                confidence = cls['confidence']
                break
        
        if species and species.lower() != 'unknown':
            valid_tracks[track_id] = track_info
            
            zone = get_zone_from_bbox(track_info['bbox'], frame_width, frame_height)
            
            if track_id not in app_state.track_zones:
                log_event("new_track", species, zone, track_id)
                app_state.track_zones[track_id] = zone
            elif app_state.track_zones[track_id] != zone:
                old_zone = app_state.track_zones[track_id]
                log_event("zone_transition", species, zone, track_id, old_zone)
                app_state.track_zones[track_id] = zone
    
    state.tracks = valid_tracks
    
    if valid_tracks:
        annotated_frame = draw_zones_and_tracks(frame, valid_tracks, frame_width, frame_height)
    else:
        annotated_frame = frame.copy()
        mid_x = frame_width // 2
        mid_y = frame_height // 2
        cv2.line(annotated_frame, (mid_x, 0), (mid_x, frame_height), (180, 180, 180), 1)
        cv2.line(annotated_frame, (0, mid_y), (frame_width, mid_y), (180, 180, 180), 1)
    
    if len(valid_tracks) > 0:
        save_pipeline_results_to_db(app_state.database, state, timestamp=datetime.now())
    
    state.annotated_frame = annotated_frame
    return state


def get_dashboard_data():
    """Get dashboard data."""
    app_state = get_app_state()
    
    all_species = app_state.analytics.analyze_all_species(
        time_window_minutes=5,
        min_count=1
    )
    
    valid_species = [s for s in all_species if s.species.lower() != 'unknown']
    
    all_alerts = app_state.alerts.generate_alerts_for_all_species(
        time_window_minutes=5,
        min_count=1
    )
    
    meaningful_alerts = [
        a for a in all_alerts 
        if a.severity in ['high', 'medium'] and a.alert != 'stable' and a.species.lower() != 'unknown'
    ]
    
    zone_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for event in list(app_state.event_log)[:50]:
        message = event.get('message', '')
        for zone in ['A', 'B', 'C', 'D']:
            if f"Zone {zone}" in message:
                zone_counts[zone] += 1
                break
    
    total_animals = sum(s.count for s in valid_species)
    total_species = len(valid_species)
    total_alerts = len(meaningful_alerts)
    
    most_active_zone = max(zone_counts, key=zone_counts.get) if any(zone_counts.values()) else None
    
    critical_insight = None
    if meaningful_alerts:
        top_alert = meaningful_alerts[0]
        if top_alert.severity == 'high':
            critical_insight = f"Critical: {top_alert.species.title()} {top_alert.message.lower()}"
        elif most_active_zone and zone_counts[most_active_zone] > 10:
            critical_insight = f"High activity detected in Zone {most_active_zone}"
    
    return {
        'summary': {
            'total_animals': total_animals,
            'total_species': total_species,
            'total_alerts': total_alerts,
            'most_active_zone': most_active_zone
        },
        'species': valid_species,
        'zones': zone_counts,
        'alerts': meaningful_alerts,
        'critical_insight': critical_insight
    }


def process_webcam(video_placeholder, dashboard_placeholder, camera_index=0):
    """Process webcam feed."""
    app_state = get_app_state()
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        st.error(f"Failed to open camera {camera_index}")
        return
    
    try:
        while app_state.processing:
            ret, frame = cap.read()
            
            if not ret:
                st.error("Failed to read from camera")
                app_state.processing = False
                break
            
            app_state.frame_number += 1
            
            state = process_frame_and_update(frame, app_state.frame_number)
            
            if state.annotated_frame is not None:
                display_frame = cv2.cvtColor(state.annotated_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(display_frame, channels="RGB", use_container_width=True)
            
            if app_state.frame_number % 30 == 0:
                update_dashboard(dashboard_placeholder)
            
            time.sleep(0.03)
    
    finally:
        cap.release()


def process_video_file(video_file, video_placeholder, dashboard_placeholder):
    """Process uploaded video file."""
    app_state = get_app_state()
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(video_file.read())
    video_path = tfile.name
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        st.error("Failed to open video file")
        return
    
    try:
        while app_state.processing:
            ret, frame = cap.read()
            
            if not ret:
                app_state.processing = False
                st.success("Video processing complete")
                break
            
            app_state.frame_number += 1
            
            state = process_frame_and_update(frame, app_state.frame_number)
            
            if state.annotated_frame is not None:
                display_frame = cv2.cvtColor(state.annotated_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(display_frame, channels="RGB", use_container_width=True)
            
            if app_state.frame_number % 30 == 0:
                update_dashboard(dashboard_placeholder)
            
            time.sleep(0.01)
    
    finally:
        cap.release()
        Path(video_path).unlink(missing_ok=True)


def update_dashboard(dashboard_placeholder):
    """Update dashboard with latest data."""
    data = get_dashboard_data()
    
    with dashboard_placeholder.container():
        if data['critical_insight']:
            st.warning(data['critical_insight'])
        
        st.markdown("**Species Overview**")
        if data['species']:
            for species_data in data['species']:
                trend_symbol = "→"
                if species_data.trend == "increasing":
                    trend_symbol = "↑"
                elif species_data.trend == "decreasing":
                    trend_symbol = "↓"
                
                st.text(f"{species_data.species.title()}: {species_data.count} {trend_symbol}")
        else:
            st.info("No species detected")
        
        st.markdown("**Zone Distribution**")
        for zone_id in ['A', 'B', 'C', 'D']:
            count = data['zones'].get(zone_id, 0)
            st.text(f"Zone {zone_id}: {count}")
        
        st.markdown("**Alerts**")
        if data['alerts']:
            for alert in data['alerts'][:3]:
                st.text(f"- {alert.species.title()}: {alert.message}")
        else:
            st.success("No alerts")


def render(app_state):
    """Render live monitoring tab with centralized state."""
    from datetime import datetime
    
    # CRITICAL: Use global singleton - NEVER use session_state
    app_state = get_app_state()
    rerun_timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"[LIVE_TAB] Rerun at {rerun_timestamp} | AppState ID: {id(app_state)}, initialized: {app_state.initialized}")
    
    st.header("Live Monitoring")
    
    # Debug info
    st.caption(f"State ID: {id(app_state)} | Initialized: {app_state.initialized} | Rerun: {rerun_timestamp}")
    
    # REMOVED EARLY RETURN - app.py handles preview/disabled state
    print(f"[LIVE_TAB] Rendering content at {rerun_timestamp}")
    
    # Summary bar
    data = get_dashboard_data()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Animals", data['summary']['total_animals'])
    with col2:
        st.metric("Species", data['summary']['total_species'])
    with col3:
        st.metric("Alerts", data['summary']['total_alerts'])
    with col4:
        zone_text = data['summary']['most_active_zone'] or '-'
        st.metric("Active Zone", zone_text)
    
    st.markdown("---")
    
    # Controls
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        source_type = st.selectbox("Source", ["Webcam", "Upload"])
    
    with col2:
        if source_type == "Webcam":
            camera_index = st.number_input("Camera", 0, 10, 0)
            app_state.video_source = ('camera', camera_index)
        else:
            video_file = st.file_uploader("Video", type=["mp4", "avi", "mov"])
            if video_file:
                app_state.video_source = ('file', video_file)
    
    with col3:
        start_disabled = (app_state.video_source is None or app_state.processing)
        if st.button("Start", disabled=start_disabled, use_container_width=True):
            app_state.processing = True
            app_state.frame_number = 0
            app_state.event_log.clear()
            app_state.track_zones.clear()
            st.rerun()
    
    with col4:
        if st.button("Stop", disabled=not app_state.processing, use_container_width=True):
            app_state.processing = False
            st.rerun()
    
    st.markdown("---")
    
    # Main layout
    col_video, col_dashboard = st.columns([3, 2])
    
    with col_video:
        st.subheader("Live Feed")
        video_placeholder = st.empty()
        
        if not app_state.processing:
            video_placeholder.info("Click Start to begin monitoring")
    
    with col_dashboard:
        st.subheader("Insights")
        dashboard_placeholder = st.empty()
        
        if not app_state.processing:
            update_dashboard(dashboard_placeholder)
    
    # Event log
    st.markdown("---")
    st.subheader("Event Log")
    
    if app_state.event_log:
        for event in list(app_state.event_log)[:15]:
            time_str = event['timestamp'].strftime("%H:%M:%S")
            st.text(f"{time_str} - {event['message']}")
    else:
        st.info("No events logged")
    
    # Process video
    if app_state.processing and app_state.video_source:
        source_type, source_data = app_state.video_source
        
        if source_type == 'camera':
            process_webcam(video_placeholder, dashboard_placeholder, source_data)
        elif source_type == 'file':
            process_video_file(source_data, video_placeholder, dashboard_placeholder)
