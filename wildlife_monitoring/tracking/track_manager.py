"""
Track Manager Module

Manages track lifecycle and history.
"""

from typing import Dict, List, Any
from collections import defaultdict
import time


class TrackManager:
    """
    Manages tracking history and metadata for all tracked objects.
    
    Attributes:
        tracks: Dictionary storing complete track history
        track_metadata: Additional metadata for each track
    """
    
    def __init__(self):
        """Initialize track manager."""
        self.tracks = defaultdict(list)
        self.track_metadata = {}
        self.track_start_times = {}
        self.track_classifications = defaultdict(list)
    
    def update_tracks(
        self,
        frame_number: int,
        tracking_info: Dict[int, Dict[str, Any]],
        classifications: Dict[int, Dict[str, Any]] = None
    ):
        """
        Update track history with new frame data.
        
        Args:
            frame_number: Current frame number
            tracking_info: Tracking info from CentroidTracker
            classifications: Optional classification results per track ID
        """
        current_time = time.time()
        
        for track_id, info in tracking_info.items():
            # Initialize track if new
            if track_id not in self.track_start_times:
                self.track_start_times[track_id] = current_time
                self.track_metadata[track_id] = {
                    "first_seen_frame": frame_number,
                    "last_seen_frame": frame_number,
                    "total_frames": 0
                }
            
            # Update track history
            track_entry = {
                "frame": frame_number,
                "centroid": info["centroid"],
                "bbox": info["bbox"],
                "timestamp": current_time
            }
            
            self.tracks[track_id].append(track_entry)
            
            # Update metadata
            self.track_metadata[track_id]["last_seen_frame"] = frame_number
            self.track_metadata[track_id]["total_frames"] += 1
            
            # Store classification if provided
            if classifications and track_id in classifications:
                self.track_classifications[track_id].append(classifications[track_id])
    
    def get_track_history(self, track_id: int) -> List[Dict[str, Any]]:
        """
        Get complete history for a track.
        
        Args:
            track_id: Track ID
            
        Returns:
            List of track entries
        """
        return self.tracks.get(track_id, [])
    
    def get_track_duration(self, track_id: int) -> float:
        """
        Get duration of a track in seconds.
        
        Args:
            track_id: Track ID
            
        Returns:
            Duration in seconds
        """
        if track_id not in self.tracks or len(self.tracks[track_id]) == 0:
            return 0.0
        
        first_timestamp = self.tracks[track_id][0]["timestamp"]
        last_timestamp = self.tracks[track_id][-1]["timestamp"]
        
        return last_timestamp - first_timestamp
    
    def get_track_path(self, track_id: int) -> List[tuple]:
        """
        Get movement path (centroids) for a track.
        
        Args:
            track_id: Track ID
            
        Returns:
            List of (x, y) centroid tuples
        """
        return [entry["centroid"] for entry in self.tracks.get(track_id, [])]
    
    def get_dominant_species(self, track_id: int) -> str:
        """
        Get most common species classification for a track.
        
        Args:
            track_id: Track ID
            
        Returns:
            Most common species name
        """
        classifications = self.track_classifications.get(track_id, [])
        
        if not classifications:
            return "Unknown"
        
        # Count species occurrences
        species_counts = defaultdict(int)
        for classification in classifications:
            species = classification.get("species", "Unknown")
            species_counts[species] += 1
        
        # Return most common
        return max(species_counts.items(), key=lambda x: x[1])[0]
    
    def get_active_tracks(self) -> List[int]:
        """
        Get list of all active track IDs.
        
        Returns:
            List of track IDs
        """
        return list(self.tracks.keys())
    
    def get_track_summary(self, track_id: int) -> Dict[str, Any]:
        """
        Get summary statistics for a track.
        
        Args:
            track_id: Track ID
            
        Returns:
            Dictionary with track summary
        """
        if track_id not in self.tracks:
            return {}
        
        metadata = self.track_metadata.get(track_id, {})
        
        return {
            "track_id": track_id,
            "duration_seconds": self.get_track_duration(track_id),
            "total_frames": metadata.get("total_frames", 0),
            "first_seen_frame": metadata.get("first_seen_frame", 0),
            "last_seen_frame": metadata.get("last_seen_frame", 0),
            "dominant_species": self.get_dominant_species(track_id),
            "path_length": len(self.tracks[track_id])
        }
