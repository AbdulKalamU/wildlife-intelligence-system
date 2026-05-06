"""
YOLO Detector Module

YOLOv8 integration for wildlife detection with animal class filtering.
"""

from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Any, Optional, Set
from pathlib import Path


# Default allowed animal classes for wildlife monitoring
DEFAULT_ANIMAL_CLASSES = {
    "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe",
    "bird", "sheep", "deer", "fox", "wolf", "lion", "tiger", "monkey"
}


class YOLODetector:
    """
    Wildlife detector using YOLOv8 with animal class filtering.
    
    Attributes:
        model: YOLOv8 model instance
        confidence_threshold: Minimum confidence for detections
        iou_threshold: IoU threshold for NMS
        allowed_classes: Set of allowed animal class names (None = all classes)
    """
    
    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        allowed_classes: Optional[Set[str]] = None
    ):
        """
        Initialize YOLO detector.
        
        Args:
            model_path: Path to YOLOv8 model weights
            confidence_threshold: Minimum confidence score (0-1)
            iou_threshold: IoU threshold for non-maximum suppression
            allowed_classes: Set of allowed class names (None = all classes)
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.allowed_classes = allowed_classes
        
    def set_allowed_classes(self, classes: Optional[Set[str]]):
        """
        Update the allowed animal classes filter.
        
        Args:
            classes: Set of allowed class names (None = disable filtering)
        """
        self.allowed_classes = classes
    
    def _filter_detections(
        self,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Filter detections to only include allowed animal classes.
        
        Args:
            detections: List of all detections
            
        Returns:
            Filtered list containing only allowed animal classes
        """
        if self.allowed_classes is None:
            return detections
        
        filtered = []
        for detection in detections:
            class_name = detection["class_name"].lower()
            if class_name in self.allowed_classes:
                filtered.append(detection)
        
        return filtered
    
    def detect(
        self,
        frame: np.ndarray,
        filter_animals: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Detect wildlife in a frame.
        
        Args:
            frame: Input frame as numpy array
            filter_animals: Whether to apply animal class filtering
            
        Returns:
            List of detections, each containing:
                - bbox: [x1, y1, x2, y2]
                - confidence: float
                - class_id: int
                - class_name: str
        """
        results = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False
        )
        
        detections = []
        
        if len(results) > 0:
            result = results[0]
            boxes = result.boxes
            
            for box in boxes:
                detection = {
                    "bbox": box.xyxy[0].cpu().numpy().tolist(),
                    "confidence": float(box.conf[0]),
                    "class_id": int(box.cls[0]),
                    "class_name": result.names[int(box.cls[0])]
                }
                detections.append(detection)
        
        # Apply animal class filtering
        if filter_animals and self.allowed_classes is not None:
            detections = self._filter_detections(detections)
        
        return detections
    
    def detect_batch(
        self,
        frames: List[np.ndarray],
        filter_animals: bool = True
    ) -> List[List[Dict[str, Any]]]:
        """
        Detect wildlife in multiple frames (batch processing).
        
        Args:
            frames: List of frames
            filter_animals: Whether to apply animal class filtering
            
        Returns:
            List of detection lists, one per frame
        """
        results = self.model.predict(
            frames,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False
        )
        
        all_detections = []
        
        for result in results:
            frame_detections = []
            boxes = result.boxes
            
            for box in boxes:
                detection = {
                    "bbox": box.xyxy[0].cpu().numpy().tolist(),
                    "confidence": float(box.conf[0]),
                    "class_id": int(box.cls[0]),
                    "class_name": result.names[int(box.cls[0])]
                }
                frame_detections.append(detection)
            
            # Apply animal class filtering
            if filter_animals and self.allowed_classes is not None:
                frame_detections = self._filter_detections(frame_detections)
            
            all_detections.append(frame_detections)
        
        return all_detections
    
    def get_detection_summary(
        self,
        detections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get summary statistics for detections.
        
        Args:
            detections: List of detections
            
        Returns:
            Dictionary with summary statistics
        """
        if not detections:
            return {
                "total_detections": 0,
                "message": "No wildlife detected",
                "classes": {}
            }
        
        # Count detections per class
        class_counts = {}
        for detection in detections:
            class_name = detection["class_name"]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        return {
            "total_detections": len(detections),
            "message": f"Detected {len(detections)} animal(s)",
            "classes": class_counts
        }
