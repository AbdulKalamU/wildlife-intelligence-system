"""
Tests for Pipeline Module
"""

import pytest
import numpy as np
from wildlife_monitoring.pipeline import WildlifePipeline, PipelineConfig, PipelineResult


class TestPipelineConfig:
    """Tests for PipelineConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = PipelineConfig()
        
        assert config.yolo_model_path == "yolov8n.pt"
        assert config.detection_confidence == 0.5
        assert config.classification_enabled is True
        assert config.frame_skip == 1
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = PipelineConfig(
            detection_confidence=0.7,
            classification_enabled=False,
            frame_skip=2
        )
        
        assert config.detection_confidence == 0.7
        assert config.classification_enabled is False
        assert config.frame_skip == 2


class TestWildlifePipeline:
    """Tests for WildlifePipeline."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        config = PipelineConfig(classification_enabled=False)
        pipeline = WildlifePipeline(config)
        
        assert pipeline.detector is not None
        assert pipeline.tracker is not None
        assert pipeline.track_manager is not None
        assert pipeline.classifier is None  # Disabled
    
    def test_pipeline_with_classification(self):
        """Test pipeline with classification enabled."""
        config = PipelineConfig(classification_enabled=True)
        pipeline = WildlifePipeline(config)
        
        assert pipeline.classifier is not None
    
    def test_process_single_frame(self):
        """Test processing a single frame."""
        config = PipelineConfig(classification_enabled=False)
        pipeline = WildlifePipeline(config)
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result = pipeline.process_frame(frame)
        
        assert isinstance(result, PipelineResult)
        assert result.frame_number == 1
        assert isinstance(result.detections, list)
        assert isinstance(result.tracks, dict)
    
    def test_process_frame_with_annotation(self):
        """Test processing frame with annotation."""
        config = PipelineConfig(classification_enabled=False)
        pipeline = WildlifePipeline(config)
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result = pipeline.process_frame(frame, annotate=True)
        
        assert result.annotated_frame is not None
        assert result.annotated_frame.shape == frame.shape
    
    def test_frame_skip(self):
        """Test frame skipping."""
        config = PipelineConfig(
            classification_enabled=False,
            frame_skip=2
        )
        pipeline = WildlifePipeline(config)
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Frame 1: processed
        result1 = pipeline.process_frame(frame)
        assert result1.frame_number == 1
        
        # Frame 2: skipped
        result2 = pipeline.process_frame(frame)
        assert result2.frame_number == 2
        
        # Frame 3: processed
        result3 = pipeline.process_frame(frame)
        assert result3.frame_number == 3
        
        # Check processed count
        stats = pipeline.get_statistics()
        assert stats["total_frames"] == 3
        assert stats["processed_frames"] == 2
        assert stats["skipped_frames"] == 1
    
    def test_get_statistics(self):
        """Test getting pipeline statistics."""
        config = PipelineConfig(classification_enabled=True)
        pipeline = WildlifePipeline(config)
        
        stats = pipeline.get_statistics()
        
        assert "total_frames" in stats
        assert "processed_frames" in stats
        assert "active_tracks" in stats
        assert "classification_enabled" in stats
        assert stats["classification_enabled"] is True
    
    def test_reset(self):
        """Test pipeline reset."""
        config = PipelineConfig(classification_enabled=False)
        pipeline = WildlifePipeline(config)
        
        # Process some frames
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        pipeline.process_frame(frame)
        pipeline.process_frame(frame)
        
        assert pipeline.frame_count == 2
        
        # Reset
        pipeline.reset()
        
        assert pipeline.frame_count == 0
        assert pipeline.processed_frames == 0
        assert len(pipeline.tracker.objects) == 0
    
    def test_get_track_summaries(self):
        """Test getting track summaries."""
        config = PipelineConfig(classification_enabled=False)
        pipeline = WildlifePipeline(config)
        
        summaries = pipeline.get_track_summaries()
        
        assert isinstance(summaries, list)


class TestPipelineResult:
    """Tests for PipelineResult."""
    
    def test_result_creation(self):
        """Test creating a pipeline result."""
        result = PipelineResult(
            frame_number=1,
            detections=[{"bbox": [0, 0, 10, 10]}],
            classifications={0: {"species": "deer", "confidence": 0.9}},
            tracks={0: {"centroid": (5, 5), "bbox": [0, 0, 10, 10]}}
        )
        
        assert result.frame_number == 1
        assert len(result.detections) == 1
        assert len(result.classifications) == 1
        assert len(result.tracks) == 1
    
    def test_result_defaults(self):
        """Test result with default values."""
        result = PipelineResult(
            frame_number=1,
            detections=[]
        )
        
        assert result.classifications == {}
        assert result.tracks == {}
        assert result.annotated_frame is None
