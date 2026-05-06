"""
Tracking Module

Centroid-based tracking of wildlife across video frames.
"""

from .centroid_tracker import CentroidTracker
from .track_manager import TrackManager

__all__ = ["CentroidTracker", "TrackManager"]
