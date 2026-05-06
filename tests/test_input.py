"""
Tests for Input Module
"""

import pytest
import numpy as np
from wildlife_monitoring.input import VideoSource, FrameProcessor


class TestVideoSource:
    """Tests for VideoSource class."""
    
    def test_video_source_initialization(self):
        """Test VideoSource initialization."""
        source = VideoSource("test.mp4")
        assert source.source == "test.mp4"
        assert source.capture is None
    
    def test_video_source_context_manager(self):
        """Test VideoSource as context manager."""
        # This test would require an actual video file
        # Placeholder for future implementation
        pass


class TestFrameProcessor:
    """Tests for FrameProcessor class."""
    
    def test_frame_processor_initialization(self):
        """Test FrameProcessor initialization."""
        processor = FrameProcessor(target_size=(640, 480))
        assert processor.target_size == (640, 480)
        assert processor.normalize is False
    
    def test_preprocess_frame(self):
        """Test frame preprocessing."""
        processor = FrameProcessor(target_size=(100, 100))
        frame = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        processed = processor.preprocess(frame)
        assert processed.shape == (100, 100, 3)
    
    def test_normalize_frame(self):
        """Test frame normalization."""
        processor = FrameProcessor(normalize=True)
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        processed = processor.preprocess(frame)
        assert processed.dtype == np.float32
        assert processed.max() <= 1.0
        assert processed.min() >= 0.0
