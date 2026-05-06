"""
Detection Utilities

Helper functions for detection processing and visualization.
"""

import cv2
import numpy as np
from typing import List, Dict, Any


def filter_detections(
    detections: List[Dict[str, Any]],
    min_confidence: float = 0.5,
    allowed_classes: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter detections by confidence and class.
    
    Args:
        detections: List of detection dictionaries
        min_confidence: Minimum confidence threshold
        allowed_classes: List of allowed class names (None = all)
        
    Returns:
        Filtered list of detections
    """
    filtered = []
    
    for det in detections:
        # Check confidence
        if det["confidence"] < min_confidence:
            continue
        
        # Check class if specified
        if allowed_classes is not None and det["class_name"] not in allowed_classes:
            continue
        
        filtered.append(det)
    
    return filtered


def draw_detections(
    frame: np.ndarray,
    detections: List[Dict[str, Any]],
    color: tuple = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """
    Draw bounding boxes and labels on frame.
    
    Args:
        frame: Input frame
        detections: List of detections
        color: BGR color tuple for boxes
        thickness: Line thickness
        
    Returns:
        Frame with drawn detections
    """
    output = frame.copy()
    
    for det in detections:
        bbox = det["bbox"]
        x1, y1, x2, y2 = map(int, bbox)
        
        # Draw bounding box
        cv2.rectangle(output, (x1, y1), (x2, y2), color, thickness)
        
        # Prepare label
        label = f"{det['class_name']}: {det['confidence']:.2f}"
        
        # Draw label background
        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(output, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
        
        # Draw label text
        cv2.putText(
            output,
            label,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
    
    return output


def calculate_iou(bbox1: List[float], bbox2: List[float]) -> float:
    """
    Calculate Intersection over Union between two bounding boxes.
    
    Args:
        bbox1: [x1, y1, x2, y2]
        bbox2: [x1, y1, x2, y2]
        
    Returns:
        IoU value (0-1)
    """
    x1_1, y1_1, x2_1, y2_1 = bbox1
    x1_2, y1_2, x2_2, y2_2 = bbox2
    
    # Calculate intersection
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i < x1_i or y2_i < y1_i:
        return 0.0
    
    intersection = (x2_i - x1_i) * (y2_i - y1_i)
    
    # Calculate union
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0
