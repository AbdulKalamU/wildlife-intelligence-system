"""
Detection Module

YOLOv8-based wildlife detection in video frames with animal class filtering.
"""

from .yolo_detector import YOLODetector, DEFAULT_ANIMAL_CLASSES
from .detection_utils import filter_detections, draw_detections

__all__ = ["YOLODetector", "DEFAULT_ANIMAL_CLASSES", "filter_detections", "draw_detections"]
