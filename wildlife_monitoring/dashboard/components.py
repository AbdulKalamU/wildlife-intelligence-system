"""
Dashboard Components Module

Reusable UI components for the dashboard.
"""

import streamlit as st
from typing import Dict, List, Any
from datetime import datetime


class DashboardComponents:
    """
    Reusable dashboard UI components.
    """
    
    @staticmethod
    def display_detection_card(detection: Dict[str, Any]):
        """
        Display a detection information card.
        
        Args:
            detection: Detection dictionary
        """
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{detection['class_name']}**")
            with col2:
                st.write(f"Conf: {detection['confidence']:.2f}")
            with col3:
                bbox = detection['bbox']
                st.write(f"Pos: ({int(bbox[0])}, {int(bbox[1])})")
    
    @staticmethod
    def display_alert_card(alert: Dict[str, Any]):
        """
        Display an alert card.
        
        Args:
            alert: Alert dictionary
        """
        priority = alert.get("priority", "low")
        
        # Color based on priority
        if priority == "critical":
            st.error(f"🚨 **{alert['message']}**")
        elif priority == "high":
            st.warning(f"⚠️ **{alert['message']}**")
        elif priority == "medium":
            st.info(f"ℹ️ **{alert['message']}**")
        else:
            st.success(f"✅ **{alert['message']}**")
        
        # Display timestamp
        timestamp = alert.get("timestamp", datetime.now())
        st.caption(f"Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    @staticmethod
    def display_statistics_panel(stats: Dict[str, Any]):
        """
        Display statistics panel.
        
        Args:
            stats: Statistics dictionary
        """
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Detections",
                stats.get("total_detections", 0)
            )
        
        with col2:
            st.metric(
                "Active Tracks",
                stats.get("active_tracks", 0)
            )
        
        with col3:
            st.metric(
                "Species Count",
                stats.get("species_count", 0)
            )
        
        with col4:
            st.metric(
                "Active Alerts",
                stats.get("active_alerts", 0)
            )
    
    @staticmethod
    def display_track_info(track_summary: Dict[str, Any]):
        """
        Display track information.
        
        Args:
            track_summary: Track summary dictionary
        """
        with st.expander(f"Track #{track_summary['track_id']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Species:** {track_summary.get('dominant_species', 'Unknown')}")
                st.write(f"**Duration:** {track_summary.get('duration_seconds', 0):.1f}s")
            
            with col2:
                st.write(f"**Frames:** {track_summary.get('total_frames', 0)}")
                st.write(f"**Path Length:** {track_summary.get('path_length', 0)}")
    
    @staticmethod
    def display_trend_chart(species: str, trend_data: Dict[str, Any]):
        """
        Display trend information for a species.
        
        Args:
            species: Species name
            trend_data: Trend analysis data
        """
        st.subheader(f"Trend: {species}")
        
        trend = trend_data.get("trend", "unknown")
        change_rate = trend_data.get("change_rate", 0.0)
        
        # Display trend indicator
        if trend == "increasing":
            st.success(f"📈 Increasing (rate: {change_rate:.2f})")
        elif trend == "decreasing":
            st.error(f"📉 Decreasing (rate: {change_rate:.2f})")
        else:
            st.info(f"➡️ Stable (rate: {change_rate:.2f})")
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average", f"{trend_data.get('average_count', 0):.1f}")
        with col2:
            st.metric("Max", trend_data.get('max_count', 0))
        with col3:
            st.metric("Min", trend_data.get('min_count', 0))
    
    @staticmethod
    def display_risk_summary(risk_summary: Dict[str, Any]):
        """
        Display risk assessment summary.
        
        Args:
            risk_summary: Risk summary dictionary
        """
        highest_risk = risk_summary.get("highest_risk", "low")
        
        # Display overall risk level
        if highest_risk == "critical":
            st.error(f"🚨 Overall Risk: CRITICAL")
        elif highest_risk == "high":
            st.warning(f"⚠️ Overall Risk: HIGH")
        elif highest_risk == "medium":
            st.info(f"ℹ️ Overall Risk: MEDIUM")
        else:
            st.success(f"✅ Overall Risk: LOW")
        
        # Display risk distribution
        st.write("**Risk Distribution:**")
        risk_dist = risk_summary.get("risk_distribution", {})
        
        for level, count in risk_dist.items():
            if count > 0:
                st.write(f"- {level.upper()}: {count}")
    
    @staticmethod
    def display_settings_panel():
        """Display settings configuration panel."""
        with st.expander("⚙️ Advanced Settings"):
            st.slider(
                "Max Disappeared Frames",
                min_value=10,
                max_value=100,
                value=50,
                help="Maximum frames before removing a track"
            )
            
            st.slider(
                "Alert Threshold",
                min_value=1,
                max_value=10,
                value=5,
                help="Minimum detections before generating alert"
            )
            
            st.checkbox(
                "Enable Auto-Classification",
                value=True,
                help="Automatically classify detected wildlife"
            )
            
            st.checkbox(
                "Enable Risk Assessment",
                value=True,
                help="Perform real-time risk assessment"
            )
