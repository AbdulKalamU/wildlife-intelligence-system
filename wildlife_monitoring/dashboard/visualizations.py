"""
Visualizations Module

Chart and graph generation for the dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px


class Visualizations:
    """
    Visualization components for wildlife monitoring dashboard.
    """
    
    @staticmethod
    def plot_species_distribution(species_counts: Dict[str, int]):
        """
        Plot species distribution pie chart.
        
        Args:
            species_counts: Dictionary mapping species to counts
        """
        if not species_counts:
            st.info("No species data available")
            return
        
        fig = go.Figure(data=[go.Pie(
            labels=list(species_counts.keys()),
            values=list(species_counts.values()),
            hole=0.3
        )])
        
        fig.update_layout(
            title="Species Distribution",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def plot_detection_timeline(detections: List[Dict[str, Any]]):
        """
        Plot detection timeline.
        
        Args:
            detections: List of detection dictionaries with timestamps
        """
        if not detections:
            st.info("No detection data available")
            return
        
        df = pd.DataFrame(detections)
        
        if 'timestamp' not in df.columns:
            st.warning("No timestamp data available")
            return
        
        # Group by time intervals
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_grouped = df.groupby(pd.Grouper(key='timestamp', freq='1min')).size()
        
        fig = go.Figure(data=[go.Scatter(
            x=df_grouped.index,
            y=df_grouped.values,
            mode='lines+markers',
            name='Detections'
        )])
        
        fig.update_layout(
            title="Detection Timeline",
            xaxis_title="Time",
            yaxis_title="Number of Detections",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def plot_track_paths(tracks: Dict[int, List[tuple]]):
        """
        Plot movement paths for tracked objects.
        
        Args:
            tracks: Dictionary mapping track ID to list of (x, y) positions
        """
        if not tracks:
            st.info("No track data available")
            return
        
        fig = go.Figure()
        
        for track_id, path in tracks.items():
            if len(path) < 2:
                continue
            
            x_coords = [p[0] for p in path]
            y_coords = [p[1] for p in path]
            
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines+markers',
                name=f'Track {track_id}',
                line=dict(width=2),
                marker=dict(size=4)
            ))
        
        fig.update_layout(
            title="Track Movement Paths",
            xaxis_title="X Position",
            yaxis_title="Y Position",
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def plot_hourly_activity(hourly_data: Dict[int, int]):
        """
        Plot hourly activity distribution.
        
        Args:
            hourly_data: Dictionary mapping hour (0-23) to activity count
        """
        if not hourly_data:
            st.info("No hourly activity data available")
            return
        
        hours = list(range(24))
        counts = [hourly_data.get(h, 0) for h in hours]
        
        fig = go.Figure(data=[go.Bar(
            x=hours,
            y=counts,
            marker_color='lightblue'
        )])
        
        fig.update_layout(
            title="Hourly Activity Distribution",
            xaxis_title="Hour of Day",
            yaxis_title="Activity Count",
            height=400,
            xaxis=dict(tickmode='linear', tick0=0, dtick=2)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def plot_trend_comparison(trends: Dict[str, Dict[str, Any]]):
        """
        Plot trend comparison for multiple species.
        
        Args:
            trends: Dictionary mapping species to trend data
        """
        if not trends:
            st.info("No trend data available")
            return
        
        species_list = list(trends.keys())
        change_rates = [trends[s].get('change_rate', 0) for s in species_list]
        
        colors = ['green' if r > 0 else 'red' for r in change_rates]
        
        fig = go.Figure(data=[go.Bar(
            x=species_list,
            y=change_rates,
            marker_color=colors
        )])
        
        fig.update_layout(
            title="Species Trend Comparison",
            xaxis_title="Species",
            yaxis_title="Change Rate",
            height=400
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def plot_risk_heatmap(risk_data: List[Dict[str, Any]]):
        """
        Plot risk assessment heatmap.
        
        Args:
            risk_data: List of risk assessment dictionaries
        """
        if not risk_data:
            st.info("No risk data available")
            return
        
        df = pd.DataFrame(risk_data)
        
        if 'timestamp' not in df.columns or 'overall_risk' not in df.columns:
            st.warning("Insufficient risk data for heatmap")
            return
        
        # Convert risk levels to numeric
        risk_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        df['risk_numeric'] = df['overall_risk'].map(risk_map)
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['date'] = df['timestamp'].dt.date
        
        # Create pivot table
        pivot = df.pivot_table(
            values='risk_numeric',
            index='date',
            columns='hour',
            aggfunc='max',
            fill_value=0
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale='RdYlGn_r',
            colorbar=dict(
                title="Risk Level",
                tickvals=[1, 2, 3, 4],
                ticktext=['Low', 'Medium', 'High', 'Critical']
            )
        ))
        
        fig.update_layout(
            title="Risk Assessment Heatmap",
            xaxis_title="Hour of Day",
            yaxis_title="Date",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def plot_confidence_distribution(detections: List[Dict[str, Any]]):
        """
        Plot confidence score distribution.
        
        Args:
            detections: List of detection dictionaries
        """
        if not detections:
            st.info("No detection data available")
            return
        
        confidences = [d.get('confidence', 0) for d in detections]
        
        fig = go.Figure(data=[go.Histogram(
            x=confidences,
            nbinsx=20,
            marker_color='lightgreen'
        )])
        
        fig.update_layout(
            title="Detection Confidence Distribution",
            xaxis_title="Confidence Score",
            yaxis_title="Frequency",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
