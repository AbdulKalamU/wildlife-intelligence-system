"""
System Insights Tab

High-level system intelligence and alerts.

CRITICAL: ALWAYS use passed app_state - NEVER create new instance
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def render(app_state):
    """Render system insights tab with centralized state."""
    # CRITICAL: Import and use global singleton
    from wildlife_monitoring.dashboard.state import get_app_state
    app_state = get_app_state()
    
    print(f"[INSIGHTS_TAB] AppState ID: {id(app_state)}, initialized: {app_state.initialized}")
    
    st.header("System Insights")
    
    # Debug info
    st.caption(f"State ID: {id(app_state)} | Initialized: {app_state.initialized}")
    
    # REMOVED EARLY RETURN - app.py handles preview/disabled state
    print(f"[INSIGHTS_TAB] Rendering content - AppState ID: {id(app_state)}")
    
    # Time window selector
    time_window = st.selectbox(
        "Analysis Period",
        [5, 15, 30, 60, 120, 360],
        index=3,
        format_func=lambda x: f"Last {x} minutes" if x < 60 else f"Last {x//60} hours"
    )
    
    st.markdown("---")
    
    # Get analytics data
    all_species = app_state.analytics.analyze_all_species(
        time_window_minutes=time_window,
        min_count=1
    )
    
    valid_species = [s for s in all_species if s.species.lower() != 'unknown']
    
    # Get alerts
    all_alerts = app_state.alerts.generate_alerts_for_all_species(
        time_window_minutes=time_window,
        min_count=1
    )
    
    meaningful_alerts = [
        a for a in all_alerts 
        if a.severity in ['high', 'medium'] and a.alert != 'stable' and a.species.lower() != 'unknown'
    ]
    
    # Most Active Species
    st.subheader("Most Active Species")
    
    if valid_species:
        sorted_species = sorted(valid_species, key=lambda x: x.count, reverse=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top 5 by Count**")
            for i, species in enumerate(sorted_species[:5], 1):
                trend_symbol = "→"
                if species.trend == "increasing":
                    trend_symbol = "↑"
                elif species.trend == "decreasing":
                    trend_symbol = "↓"
                
                st.text(f"{i}. {species.species.title()}: {species.count} {trend_symbol}")
        
        with col2:
            st.markdown("**Trend Analysis**")
            increasing = [s for s in valid_species if s.trend == "increasing"]
            decreasing = [s for s in valid_species if s.trend == "decreasing"]
            stable = [s for s in valid_species if s.trend == "stable"]
            
            st.text(f"Increasing: {len(increasing)}")
            st.text(f"Decreasing: {len(decreasing)}")
            st.text(f"Stable: {len(stable)}")
    else:
        st.info(f"No activity in the last {time_window} minutes")
    
    st.markdown("---")
    
    # Most Active Zone
    st.subheader("Most Active Zone")
    
    recent_sightings = app_state.database.get_recent_sightings(limit=1000)
    
    if recent_sightings:
        zone_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for sighting in recent_sightings:
            bbox = sighting.get('bbox')
            if bbox:
                try:
                    if isinstance(bbox, str):
                        import json
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
                    
                    zone_counts[zone] += 1
                except:
                    pass
        
        most_active = max(zone_counts, key=zone_counts.get)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Zone A", zone_counts['A'])
        with col2:
            st.metric("Zone B", zone_counts['B'])
        with col3:
            st.metric("Zone C", zone_counts['C'])
        with col4:
            st.metric("Zone D", zone_counts['D'])
        
        if zone_counts[most_active] > 0:
            st.success(f"Most active: Zone {most_active} ({zone_counts[most_active]} detections)")
    else:
        st.info("No zone data available")
    
    st.markdown("---")
    
    # Declining Species
    st.subheader("Declining Species")
    
    declining_species = [s for s in valid_species if s.trend == "decreasing"]
    
    if declining_species:
        sorted_declining = sorted(declining_species, key=lambda x: x.trend_percentage)
        
        for species in sorted_declining[:5]:
            st.warning(
                f"{species.species.title()}: {species.count} sightings "
                f"({species.trend_percentage:+.1f}% change)"
            )
    else:
        st.success("No declining species detected")
    
    st.markdown("---")
    
    # High-Risk Alerts
    st.subheader("High-Risk Alerts")
    
    high_alerts = [a for a in meaningful_alerts if a.severity == 'high']
    
    if high_alerts:
        for alert in high_alerts:
            if alert.alert == "population_risk":
                message = f"{alert.species.title()} population decreased by {abs(alert.trend_percentage):.0f}%"
            elif alert.alert == "low_population":
                message = f"{alert.species.title()} count is critically low ({alert.count} detected)"
            elif alert.alert == "anomaly":
                message = f"{alert.species.title()} activity increased significantly ({alert.trend_percentage:+.0f}%)"
            else:
                message = alert.message
            
            st.error(f"HIGH: {message}")
    else:
        st.success("No high-risk alerts")
    
    # Medium Alerts
    medium_alerts = [a for a in meaningful_alerts if a.severity == 'medium']
    
    if medium_alerts:
        st.markdown("**Medium Priority Alerts**")
        for alert in medium_alerts[:5]:
            if alert.alert == "population_risk":
                message = f"{alert.species.title()} population showing declining trend"
            elif alert.alert == "low_population":
                message = f"{alert.species.title()} count below threshold ({alert.count} detected)"
            elif alert.alert == "anomaly":
                message = f"{alert.species.title()} activity spike detected"
            else:
                message = alert.message
            
            st.warning(f"MEDIUM: {message}")
    
    st.markdown("---")
    
    # Model Statistics
    st.subheader("Model Statistics")
    
    db_stats = app_state.database.get_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Sightings", db_stats['total_sightings'])
        st.metric("Unique Species", db_stats['unique_species'])
    
    with col2:
        st.metric("Unique Tracks", db_stats['unique_tracks'])
        if db_stats['total_sightings'] > 0:
            avg_per_track = db_stats['total_sightings'] / db_stats['unique_tracks']
            st.metric("Avg Sightings/Track", f"{avg_per_track:.1f}")
    
    with col3:
        if db_stats['first_sighting']:
            st.text(f"First: {db_stats['first_sighting'][:19]}")
        if db_stats['last_sighting']:
            st.text(f"Last: {db_stats['last_sighting'][:19]}")
    
    # Species distribution
    if valid_species:
        st.markdown("---")
        st.subheader("Species Distribution")
        
        species_counts = app_state.database.get_species_count()
        
        # Filter out unknown
        species_counts = {k: v for k, v in species_counts.items() if k.lower() != 'unknown'}
        
        if species_counts:
            total = sum(species_counts.values())
            
            for species, count in sorted(species_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total) * 100
                st.text(f"{species.title()}: {count} ({percentage:.1f}%)")
