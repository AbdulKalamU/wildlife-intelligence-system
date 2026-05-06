"""
Input Module

Handles camera feeds and video file input, frame extraction and preprocessing.
"""

from .video_source import VideoSource
from .frame_processor import FrameProcessor

__all__ = ["VideoSource", "FrameProcessor"]
