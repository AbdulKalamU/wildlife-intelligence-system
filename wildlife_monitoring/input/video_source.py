"""
Video Source Module

Handles video file reading and camera stream input.
"""

import cv2
from typing import Optional, Union
from pathlib import Path


class VideoSource:
    """
    Manages video input from files or camera streams.
    
    Attributes:
        source: Path to video file or camera index
        capture: OpenCV VideoCapture object
        fps: Frames per second of the video source
        frame_count: Total number of frames (for video files)
    """
    
    def __init__(self, source: Union[str, int, Path]):
        """
        Initialize video source.
        
        Args:
            source: Path to video file (str/Path) or camera index (int)
        """
        self.source = source
        self.capture: Optional[cv2.VideoCapture] = None
        self.fps: float = 0.0
        self.frame_count: int = 0
        
    def open(self) -> bool:
        """
        Open the video source.
        
        Returns:
            True if successfully opened, False otherwise
        """
        self.capture = cv2.VideoCapture(str(self.source))
        
        if self.capture.isOpened():
            self.fps = self.capture.get(cv2.CAP_PROP_FPS)
            self.frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
            return True
        return False
    
    def read_frame(self) -> tuple[bool, Optional[any]]:
        """
        Read a single frame from the video source.
        
        Returns:
            Tuple of (success, frame) where success is bool and frame is numpy array
        """
        if self.capture is None:
            return False, None
        return self.capture.read()
    
    def release(self):
        """Release the video source."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
