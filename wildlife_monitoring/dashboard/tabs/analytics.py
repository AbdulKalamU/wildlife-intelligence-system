"""
Analytics Tab

Species distribution, trends, and zone activity charts.

CRITICAL: ALWAYS use passed app_state - NEVER create new instance
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def render(app_state):
    """Render analytics tab with centralized state."""
    # CRITICAL: Import and use global singleton
    from wildlife_monitoring.dashboard.state import get_app_state
    app_state = get_app_state()
    
    print(f"[ANALYTICS_TAB] AppState ID: {id(app_state)}, initialized: {app_state.initialized}")
    
    st.header("Analytics")
    
    # Debug info
    st.caption(f"State ID: {id(app_state)} | Initialized: {app_state.initialized}")
    
    # REMOVED EARLY RETURN - app.py handles preview/disabled state
    print(f"[ANALYTICS_TAB] Rendering content - AppState ID: {id(app_state)}")
    
    # Time window selector
    col1, col2 = st.columns([3, 1])
    
    with col1:
        time_window = st.selectbox(
            "Time Window",
            [5, 15, 30, 60, 120, 360, 720, 1440],
            index=3,
            format_func=lambda x: f"Last {x} minutes" if x < 60 else f"Last {x//60} hours"
        )
    
    with col2:
        if st.button("Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Get analytics data
    all_species = app_state.analytics.analyze_all_species(
        time_window_minutes=time_window,
        min_count=1
    )
    
    valid_species = [s for s in all_species if s.species.lower() != 'unknown']
    
    if not valid_species:
        st.info(f"No sightings in the last {time_window} minutes")
        return
    
    # Species Distribution Bar Chart
    st.subheader("Species Distribution")
    
    species_data = pd.DataFrame([
        {
            'Species': s.species.title(),
            'Count': s.count,
            'Trend': s.trend
        }
        for s in valid_species
    ])
    
    fig_species = px.bar(
        species_data,
        x='Species',
        y='Count',
        color='Trend',
        color_discrete_map={
            'increasing': '#28a745',
            'decreasing': '#dc3545',
            'stable': '#6c757d'
        },
        title=f"Species Counts (Last {time_window} min)"
    )
    fig_species.update_layout(
        showlegend=True,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_species, use_container_width=True)
    
    # Population Trend Line Chart
    st.subheader("Population Trends")
    
    trend_data = []
    for species in valid_species:
        hourly = app_state.analytics.get_hourly_breakdown(
            species=species.species,
            hours=min(24, time_window // 60 + 1)
        )
        for entry in hourly:
            trend_data.append({
                'Hour': entry['hour'],
                'Count': entry['count'],
                'Species': species.species.title()
            })
    
    if trend_data:
        trend_df = pd.DataFrame(trend_data)
        
        fig_trend = px.line(
            trend_df,
            x='Hour',
            y='Count',
            color='Species',
            title=f"Population Over Time (Last {min(24, time_window // 60 + 1)} hours)"
        )
        fig_trend.update_layout(
            showlegend=True,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Not enough data for trend analysis")
    
    # Zone Activity Chart
    st.subheader("Zone Activity")
    
    # Get zone data from recent sightings
    recent_sightings = app_state.database.get_recent_sightings(limit=1000)
    
    if recent_sightings:
        # Calculate zones from bounding boxes
        zone_data = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for sighting in recent_sightings:
            bbox = sighting.get('bbox')
            if bbox:
                # Parse bbox string if needed
                if isinstance(bbox, str):
                    import json
                    bbox = json.loads(bbox)
                
                # Calculate zone
                x1, y1, x2, y2 = bbox
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                # Assume frame size (this is approximate)
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
                
                zone_data[zone] += 1
        
        zone_df = pd.DataFrame([
            {'Zone': zone, 'Count': count}
            for zone, count in zone_data.items()
        ])
        
        fig_zone = px.bar(
            zone_df,
            x='Zone',
            y='Count',
            title="Activity by Zone",
            color='Zone',
            color_discrete_map={
                'A': '#dc3545',
                'B': '#28a745',
                'C': '#007bff',
                'D': '#ffc107'
            }
        )
        fig_zone.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_zone, use_container_width=True)
    else:
        st.info("No zone data available")
    
    # Detections Over Time
    st.subheader("Detections Over Time")
    
    hourly_all = app_state.analytics.get_hourly_breakdown(
        species=None,
        hours=min(24, time_window // 60 + 1)
    )
    
    if hourly_all:
        hourly_df = pd.DataFrame(hourly_all)
        
        fig_hourly = px.area(
            hourly_df,
            x='hour',
            y='count',
            title=f"Total Detections (Last {min(24, time_window // 60 + 1)} hours)"
        )
        fig_hourly.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
    else:
        st.info("No detection data available")
    
    # Summary Statistics
    st.markdown("---")
    st.subheader("Summary Statistics")
    
    summary = app_state.analytics.get_activity_summary(
        time_window_minutes=time_window
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sightings", summary['total_sightings'])
    with col2:
        st.metric("Unique Species", summary['unique_species'])
    with col3:
        st.metric("Unique Tracks", summary['unique_tracks'])
    with col4:
        st.metric("Avg Confidence", f"{summary['avg_confidence']:.2f}")
    
    if summary['most_common_species']:
        st.info(f"Most common: {summary['most_common_species'].title()} ({summary['most_common_count']} sightings)")
