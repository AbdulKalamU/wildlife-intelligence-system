"""
Centroid Tracker Module

Implements centroid-based object tracking algorithm.
"""

import numpy as np
from scipy.spatial import distance as dist
from collections import OrderedDict
from typing import List, Dict, Tuple, Any


class CentroidTracker:
    """
    Tracks objects using centroid distance matching.
    
    Attributes:
        next_object_id: Counter for assigning unique IDs
        objects: Dictionary mapping object ID to centroid
        disappeared: Dictionary tracking frames since object was last seen
        max_disappeared: Maximum frames before removing a track
    """
    
    def __init__(self, max_disappeared: int = 50):
        """
        Initialize centroid tracker.
        
        Args:
            max_disappeared: Maximum frames an object can be missing before removal
        """
        self.next_object_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.bboxes = OrderedDict()  # Store bounding boxes
    
    def register(self, centroid: np.ndarray, bbox: List[float]):
        """
        Register a new object with unique ID.
        
        Args:
            centroid: (x, y) centroid coordinates
            bbox: Bounding box [x1, y1, x2, y2]
        """
        self.objects[self.next_object_id] = centroid
        self.bboxes[self.next_object_id] = bbox
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1
    
    def deregister(self, object_id: int):
        """
        Remove an object from tracking.
        
        Args:
            object_id: ID of object to remove
        """
        del self.objects[object_id]
        del self.bboxes[object_id]
        del self.disappeared[object_id]
    
    def update(self, detections: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """
        Update tracker with new detections.
        
        Args:
            detections: List of detection dictionaries with 'bbox' key
            
        Returns:
            Dictionary mapping object ID to tracking info:
                - centroid: (x, y)
                - bbox: [x1, y1, x2, y2]
                - disappeared_frames: int
        """
        # If no detections, mark all as disappeared
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            
            return self._get_tracking_info()
        
        # Calculate centroids from detections
        input_centroids = np.zeros((len(detections), 2), dtype="float")
        input_bboxes = []
        
        for i, det in enumerate(detections):
            bbox = det["bbox"]
            input_bboxes.append(bbox)
            
            # Calculate centroid
            x1, y1, x2, y2 = bbox
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            input_centroids[i] = (cx, cy)
        
        # If no existing objects, register all
        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(input_centroids[i], input_bboxes[i])
        else:
            # Match existing objects to new detections
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            # Compute distance matrix
            D = dist.cdist(np.array(object_centroids), input_centroids)
            
            # Find minimum distance matches
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                # Update existing object
                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.bboxes[object_id] = input_bboxes[col]
                self.disappeared[object_id] = 0
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Handle unmatched existing objects
            unused_rows = set(range(D.shape[0])) - used_rows
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            
            # Register new detections
            unused_cols = set(range(D.shape[1])) - used_cols
            for col in unused_cols:
                self.register(input_centroids[col], input_bboxes[col])
        
        return self._get_tracking_info()
    
    def _get_tracking_info(self) -> Dict[int, Dict[str, Any]]:
        """
        Get current tracking information for all objects.
        
        Returns:
            Dictionary mapping object ID to tracking info
        """
        tracking_info = {}
        
        for object_id in self.objects.keys():
            tracking_info[object_id] = {
                "centroid": self.objects[object_id],
                "bbox": self.bboxes[object_id],
                "disappeared_frames": self.disappeared[object_id]
            }
        
        return tracking_info
