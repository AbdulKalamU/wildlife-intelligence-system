"""
Tests for Tracking Module
"""

import pytest
from wildlife_monitoring.tracking import CentroidTracker, TrackManager


class TestCentroidTracker:
    """Tests for CentroidTracker class."""
    
    def test_tracker_initialization(self):
        """Test tracker initialization."""
        tracker = CentroidTracker(max_disappeared=30)
        assert tracker.max_disappeared == 30
        assert tracker.next_object_id == 0
        assert len(tracker.objects) == 0
    
    def test_register_object(self):
        """Test object registration."""
        tracker = CentroidTracker()
        centroid = (100, 100)
        bbox = [90, 90, 110, 110]
        
        tracker.register(centroid, bbox)
        assert tracker.next_object_id == 1
        assert 0 in tracker.objects
    
    def test_update_with_detections(self):
        """Test tracker update with detections."""
        tracker = CentroidTracker()
        detections = [
            {"bbox": [100, 100, 150, 150]},
            {"bbox": [200, 200, 250, 250]}
        ]
        
        tracking_info = tracker.update(detections)
        assert len(tracking_info) == 2


class TestTrackManager:
    """Tests for TrackManager class."""
    
    def test_track_manager_initialization(self):
        """Test track manager initialization."""
        manager = TrackManager()
        assert len(manager.tracks) == 0
        assert len(manager.track_metadata) == 0
    
    def test_update_tracks(self):
        """Test track updates."""
        manager = TrackManager()
        tracking_info = {
            0: {
                "centroid": (100, 100),
                "bbox": [90, 90, 110, 110],
                "disappeared_frames": 0
            }
        }
        
        manager.update_tracks(1, tracking_info)
        assert 0 in manager.tracks
        assert len(manager.tracks[0]) == 1
