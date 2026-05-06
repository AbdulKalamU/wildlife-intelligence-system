"""
Wildlife Monitoring Dashboard - Consolidated Application

RECOVERED: All functionality from archived dashboards reconnected.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from wildlife_monitoring.dashboard.state import (
    get_app_state,
    initialize_system,
    clear_database,
    get_database_stats
)


# Page configuration
st.set_page_config(
    page_title="Wildlife Monitoring Platform",
    page_icon="🦌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    
    h1 {font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem;}
    h2 {font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;}
    h3 {font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;}
    
    .metric-container {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 0.5rem 0.75rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #212529;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #6c757d;
        text-transform: uppercase;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application with centralized state."""
    
    # Get centralized app state - SINGLE instance
    app_state = get_app_state()
    
    # DEBUG: Log state at entry
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[APP_MAIN] {timestamp} | AppState ID: {id(app_state)}, initialized: {app_state.initialized}")
    
    # Sidebar
    with st.sidebar:
        print(f"[SIDEBAR] {timestamp} | AppState ID: {id(app_state)}, initialized: {app_state.initialized}")
        st.title("Wildlife Monitoring Platform")
        st.markdown("---")
        
        # System status
        if app_state.initializing:
            st.info("Initializing system...")
            st.caption("Please wait...")
        elif not app_state.initialized:
            st.warning("System not initialized")
            if st.button("Initialize System", use_container_width=True):
                with st.spinner("Initializing components..."):
                    try:
                        initialize_system(app_state)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Initialization failed: {e}")
                        app_state.initializing = False
        else:
            st.success("System ready")
            st.caption(f"✓ Initialized")
        
        st.markdown("---")
        
        # Database stats
        if app_state.initialized:
            stats = get_database_stats(app_state)
            st.metric("Total Sightings", stats['total_sightings'])
            st.metric("Unique Species", stats['unique_species'])
            st.metric("Unique Tracks", stats['unique_tracks'])
        else:
            st.metric("Total Sightings", "0")
            st.metric("Unique Species", "0")
            st.metric("Unique Tracks", "0")
        
        st.markdown("---")
        
        # Actions
        if app_state.initialized:
            if st.button("Clear Database", use_container_width=True):
                clear_database(app_state)
                st.success("Database cleared")
                st.rerun()
    
    # Main content - Tabs (ALWAYS render, even if not initialized)
    tab1, tab2, tab3, tab4 = st.tabs([
        "Live Monitoring",
        "Analytics",
        "Sightings Database",
        "System Insights"
    ])
    
    with tab1:
        render_live_monitoring(app_state)
    
    with tab2:
        render_analytics(app_state)
    
    with tab3:
        render_sightings_database(app_state)
    
    with tab4:
        render_system_insights(app_state)


def render_live_monitoring(app_state):
    """Render live monitoring tab - RECOVERED functionality."""
    from wildlife_monitoring.dashboard.tabs import live_monitoring
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[RENDER_LIVE] {timestamp} | AppState ID: {id(app_state)}, initialized: {app_state.initialized}")
    
    # OVERRIDE: Remove the early return, always render UI
    if not app_state.initialized:
        print(f"[RENDER_LIVE] {timestamp} | Showing PREVIEW (not initialized)")
        st.header("Live Monitoring")
        st.warning("⚠️ System not initialized. Click 'Initialize System' in the sidebar to enable live monitoring.")
        
        # Show disabled UI preview
        st.markdown("---")
        st.subheader("Preview (Disabled)")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Animals", "0")
        with col2:
            st.metric("Species", "0")
        with col3:
            st.metric("Alerts", "0")
        with col4:
            st.metric("Active Zone", "-")
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.selectbox("Source", ["Webcam", "Upload"], disabled=True)
        with col2:
            st.number_input("Camera", 0, 10, 0, disabled=True)
        with col3:
            st.button("Start", disabled=True, use_container_width=True, key="live_start_disabled")
        with col4:
            st.button("Stop", disabled=True, use_container_width=True, key="live_stop_disabled")
        
        st.markdown("---")
        
        col_video, col_dashboard = st.columns([3, 2])
        with col_video:
            st.subheader("Live Feed")
            st.info("Initialize system to start monitoring")
        with col_dashboard:
            st.subheader("Insights")
            st.info("No data available")
        
        return
    
    # System initialized - render full functionality
    print(f"[RENDER_LIVE] {timestamp} | Calling live_monitoring.render() with initialized=True")
    live_monitoring.render(app_state)


def render_analytics(app_state):
    """Render analytics tab - RECOVERED functionality."""
    from wildlife_monitoring.dashboard.tabs import analytics
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[RENDER_ANALYTICS] {timestamp} | AppState ID: {id(app_state)}, initialized: {app_state.initialized}")
    
    # OVERRIDE: Remove the early return, always render UI
    if not app_state.initialized:
        print(f"[RENDER_ANALYTICS] {timestamp} | Showing PREVIEW (not initialized)")
        st.header("Analytics")
        st.warning("⚠️ System not initialized. Click 'Initialize System' in the sidebar to view analytics.")
        
        # Show disabled UI preview
        st.markdown("---")
        st.subheader("Preview (Disabled)")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.selectbox("Time Window", ["Last 60 minutes"], disabled=True)
        with col2:
            st.button("Refresh", disabled=True, use_container_width=True, key="analytics_refresh_disabled")
        
        st.markdown("---")
        st.subheader("Species Distribution")
        st.info("No data available - initialize system and start monitoring")
        
        st.subheader("Population Trends")
        st.info("No data available")
        
        st.subheader("Zone Activity")
        st.info("No data available")
        
        return
    
    # System initialized - render full functionality
    print(f"[RENDER_ANALYTICS] {timestamp} | Calling analytics.render() with initialized=True")
    analytics.render(app_state)


def render_sightings_database(app_state):
    """Render sightings database tab - RECOVERED functionality."""
    from wildlife_monitoring.dashboard.tabs import sightings_database
    
    # OVERRIDE: Remove the early return, always render UI
    if not app_state.initialized:
        st.header("Sightings Database")
        st.warning("⚠️ System not initialized. Click 'Initialize System' in the sidebar to access database.")
        
        # Show disabled UI preview
        st.markdown("---")
        st.subheader("Preview (Disabled)")
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            st.text_input("Search Species", placeholder="e.g., tiger", disabled=True)
        with col2:
            st.slider("Min Confidence", 0.0, 1.0, 0.0, 0.05, disabled=True)
        with col3:
            st.selectbox("Show Records", [50, 100, 500], disabled=True)
        with col4:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("Refresh", disabled=True, use_container_width=True, key="database_refresh_disabled")
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", "0")
        with col2:
            st.metric("Unique Species", "0")
        with col3:
            st.metric("Unique Tracks", "0")
        with col4:
            st.metric("Avg Confidence", "0.000")
        
        st.markdown("---")
        st.subheader("Sightings (0 records)")
        st.info("No sightings recorded - initialize system and start monitoring")
        
        return
    
    # System initialized - render full functionality
    sightings_database.render(app_state)


def render_system_insights(app_state):
    """Render system insights tab - RECOVERED functionality."""
    from wildlife_monitoring.dashboard.tabs import system_insights
    
    # OVERRIDE: Remove the early return, always render UI
    if not app_state.initialized:
        st.header("System Insights")
        st.warning("⚠️ System not initialized. Click 'Initialize System' in the sidebar to view insights.")
        
        # Show disabled UI preview
        st.markdown("---")
        st.subheader("Preview (Disabled)")
        
        st.selectbox("Analysis Period", ["Last 60 minutes"], disabled=True)
        
        st.markdown("---")
        st.subheader("Most Active Species")
        st.info("No data available")
        
        st.subheader("Most Active Zone")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Zone A", "0")
        with col2:
            st.metric("Zone B", "0")
        with col3:
            st.metric("Zone C", "0")
        with col4:
            st.metric("Zone D", "0")
        
        st.markdown("---")
        st.subheader("Declining Species")
        st.success("No declining species detected")
        
        st.markdown("---")
        st.subheader("High-Risk Alerts")
        st.success("No high-risk alerts")
        
        return
    
    # System initialized - render full functionality
    system_insights.render(app_state)


if __name__ == "__main__":
    main()
