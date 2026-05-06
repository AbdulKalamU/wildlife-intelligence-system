"""
Sightings Database Tab

Browse, search, and export sightings data.

CRITICAL: ALWAYS use passed app_state - NEVER create new instance
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json


def render(app_state):
    """Render sightings database tab with centralized state."""
    # CRITICAL: Import and use global singleton
    from wildlife_monitoring.dashboard.state import get_app_state
    app_state = get_app_state()
    
    print(f"[DATABASE_TAB] AppState ID: {id(app_state)}, initialized: {app_state.initialized}")
    
    st.header("Sightings Database")
    
    # Debug info
    st.caption(f"State ID: {id(app_state)} | Initialized: {app_state.initialized}")
    
    # REMOVED EARLY RETURN - app.py handles preview/disabled state
    print(f"[DATABASE_TAB] Rendering content - AppState ID: {id(app_state)}")
    
    # Search and filter controls
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        search_species = st.text_input("Search Species", placeholder="e.g., tiger")
    
    with col2:
        min_confidence = st.slider("Min Confidence", 0.0, 1.0, 0.0, 0.05)
    
    with col3:
        limit = st.selectbox("Show Records", [50, 100, 500, 1000, 5000], index=1)
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Get sightings
    if search_species:
        sightings = app_state.database.get_sightings_by_species(
            species=search_species,
            limit=limit
        )
    else:
        sightings = app_state.database.get_recent_sightings(limit=limit)
    
    # Filter by confidence
    if min_confidence > 0:
        sightings = [s for s in sightings if s['confidence'] >= min_confidence]
    
    if not sightings:
        st.info("No sightings found matching criteria")
        return
    
    # Convert to DataFrame
    df_data = []
    for s in sightings:
        # Calculate zone from bbox
        zone = '-'
        bbox = s.get('bbox')
        if bbox:
            try:
                if isinstance(bbox, str):
                    bbox = json.loads(bbox)
                
                x1, y1, x2, y2 = bbox
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                frame_width = 640
                frame_height = 480
                mid_x = frame_width / 2
                mid_y = frame_height / 2
                
                if center_x < mid_x and center_y < mid_y:
                    zone = 'A'
                elif center_x >= mid_x and center_y < mid_y:
                    zone = 'B'
                elif center_x < mid_x and center_y >= mid_y:
                    zone = 'C'
                else:
                    zone = 'D'
            except:
                pass
        
        df_data.append({
            'ID': s['id'],
            'Species': s['species'].title(),
            'Confidence': f"{s['confidence']:.3f}",
            'Timestamp': s['timestamp'],
            'Track ID': s['track_id'],
            'Frame': s['frame_number'],
            'Zone': zone
        })
    
    df = pd.DataFrame(df_data)
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        unique_species = df['Species'].nunique()
        st.metric("Unique Species", unique_species)
    with col3:
        unique_tracks = df['Track ID'].nunique()
        st.metric("Unique Tracks", unique_tracks)
    with col4:
        avg_conf = pd.to_numeric(df['Confidence']).mean()
        st.metric("Avg Confidence", f"{avg_conf:.3f}")
    
    st.markdown("---")
    
    # Display table
    st.subheader(f"Sightings ({len(df)} records)")
    
    # Configure column display
    st.dataframe(
        df,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Export options
    st.markdown("---")
    st.subheader("Export Data")
    
    col1, col2, col3 = st.columns([2, 2, 4])
    
    with col1:
        # CSV export
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"sightings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON export
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"sightings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Species breakdown
    st.markdown("---")
    st.subheader("Species Breakdown")
    
    species_counts = df['Species'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Count by Species**")
        for species, count in species_counts.items():
            percentage = (count / len(df)) * 100
            st.text(f"{species}: {count} ({percentage:.1f}%)")
    
    with col2:
        st.markdown("**Zone Distribution**")
        zone_counts = df['Zone'].value_counts()
        for zone, count in zone_counts.items():
            if zone != '-':
                percentage = (count / len(df)) * 100
                st.text(f"Zone {zone}: {count} ({percentage:.1f}%)")
