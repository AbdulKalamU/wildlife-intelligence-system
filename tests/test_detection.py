"""
Tests for Detection Module
"""

import pytest
import numpy as np
from wildlife_monitoring.detection import detection_utils, YOLODetector, DEFAULT_ANIMAL_CLASSES


class TestDetectionUtils:
    """Tests for detection utility functions."""
    
    def test_filter_detections_by_confidence(self):
        """Test filtering detections by confidence."""
        detections = [
            {"confidence": 0.8, "class_name": "deer"},
            {"confidence": 0.3, "class_name": "bear"},
            {"confidence": 0.6, "class_name": "fox"}
        ]
        
        filtered = detection_utils.filter_detections(detections, min_confidence=0.5)
        assert len(filtered) == 2
        assert all(d["confidence"] >= 0.5 for d in filtered)
    
    def test_filter_detections_by_class(self):
        """Test filtering detections by class."""
        detections = [
            {"confidence": 0.8, "class_name": "deer"},
            {"confidence": 0.7, "class_name": "bear"},
            {"confidence": 0.6, "class_name": "fox"}
        ]
        
        filtered = detection_utils.filter_detections(
            detections,
            allowed_classes=["deer", "bear"]
        )
        assert len(filtered) == 2
        assert all(d["class_name"] in ["deer", "bear"] for d in filtered)
    
    def test_calculate_iou(self):
        """Test IoU calculation."""
        bbox1 = [0, 0, 10, 10]
        bbox2 = [5, 5, 15, 15]
        
        iou = detection_utils.calculate_iou(bbox1, bbox2)
        assert 0 < iou < 1
        
        # Test identical boxes
        iou_identical = detection_utils.calculate_iou(bbox1, bbox1)
        assert iou_identical == 1.0
        
        # Test non-overlapping boxes
        bbox3 = [20, 20, 30, 30]
        iou_no_overlap = detection_utils.calculate_iou(bbox1, bbox3)
        assert iou_no_overlap == 0.0


class TestAnimalFiltering:
    """Tests for animal class filtering functionality."""
    
    def test_filter_detections_animals_only(self):
        """Test filtering to keep only animal classes."""
        # Mock detections with mixed classes
        detections = [
            {"confidence": 0.8, "class_name": "dog", "bbox": [0, 0, 10, 10]},
            {"confidence": 0.7, "class_name": "car", "bbox": [20, 20, 30, 30]},
            {"confidence": 0.6, "class_name": "cat", "bbox": [40, 40, 50, 50]},
            {"confidence": 0.5, "class_name": "person", "bbox": [60, 60, 70, 70]},
        ]
        
        allowed_animals = {"dog", "cat", "horse", "cow"}
        
        # Create detector with filtering
        detector = YOLODetector(allowed_classes=allowed_animals)
        filtered = detector._filter_detections(detections)
        
        # Should only keep dog and cat
        assert len(filtered) == 2
        assert all(d["class_name"] in allowed_animals for d in filtered)
        assert filtered[0]["class_name"] == "dog"
        assert filtered[1]["class_name"] == "cat"
    
    def test_no_animals_detected(self):
        """Test handling when no animals are detected."""
        detections = [
            {"confidence": 0.8, "class_name": "car", "bbox": [0, 0, 10, 10]},
            {"confidence": 0.7, "class_name": "person", "bbox": [20, 20, 30, 30]},
        ]
        
        allowed_animals = {"dog", "cat", "horse", "cow"}
        
        detector = YOLODetector(allowed_classes=allowed_animals)
        filtered = detector._filter_detections(detections)
        
        # Should return empty list
        assert len(filtered) == 0
        
        # Test summary message
        summary = detector.get_detection_summary(filtered)
        assert summary["total_detections"] == 0
        assert summary["message"] == "No wildlife detected"
    
    def test_all_animals_detected(self):
        """Test when all detections are valid animals."""
        detections = [
            {"confidence": 0.8, "class_name": "dog", "bbox": [0, 0, 10, 10]},
            {"confidence": 0.7, "class_name": "cat", "bbox": [20, 20, 30, 30]},
            {"confidence": 0.6, "class_name": "horse", "bbox": [40, 40, 50, 50]},
        ]
        
        allowed_animals = {"dog", "cat", "horse", "cow"}
        
        detector = YOLODetector(allowed_classes=allowed_animals)
        filtered = detector._filter_detections(detections)
        
        # Should keep all detections
        assert len(filtered) == 3
        assert filtered == detections
    
    def test_no_filtering_when_disabled(self):
        """Test that filtering can be disabled."""
        detections = [
            {"confidence": 0.8, "class_name": "dog", "bbox": [0, 0, 10, 10]},
            {"confidence": 0.7, "class_name": "car", "bbox": [20, 20, 30, 30]},
        ]
        
        # Create detector without allowed_classes (no filtering)
        detector = YOLODetector(allowed_classes=None)
        filtered = detector._filter_detections(detections)
        
        # Should keep all detections
        assert len(filtered) == 2
        assert filtered == detections
    
    def test_case_insensitive_filtering(self):
        """Test that filtering is case-insensitive."""
        detections = [
            {"confidence": 0.8, "class_name": "Dog", "bbox": [0, 0, 10, 10]},
            {"confidence": 0.7, "class_name": "CAT", "bbox": [20, 20, 30, 30]},
        ]
        
        allowed_animals = {"dog", "cat"}  # lowercase
        
        detector = YOLODetector(allowed_classes=allowed_animals)
        filtered = detector._filter_detections(detections)
        
        # Should match case-insensitively
        assert len(filtered) == 2
    
    def test_detection_summary(self):
        """Test detection summary generation."""
        detections = [
            {"confidence": 0.8, "class_name": "dog", "bbox": [0, 0, 10, 10]},
            {"confidence": 0.7, "class_name": "dog", "bbox": [20, 20, 30, 30]},
            {"confidence": 0.6, "class_name": "cat", "bbox": [40, 40, 50, 50]},
        ]
        
        detector = YOLODetector()
        summary = detector.get_detection_summary(detections)
        
        assert summary["total_detections"] == 3
        assert summary["message"] == "Detected 3 animal(s)"
        assert summary["classes"]["dog"] == 2
        assert summary["classes"]["cat"] == 1
    
    def test_default_animal_classes_constant(self):
        """Test that DEFAULT_ANIMAL_CLASSES is properly defined."""
        assert isinstance(DEFAULT_ANIMAL_CLASSES, set)
        assert len(DEFAULT_ANIMAL_CLASSES) > 0
        assert "dog" in DEFAULT_ANIMAL_CLASSES
        assert "cat" in DEFAULT_ANIMAL_CLASSES
        assert "elephant" in DEFAULT_ANIMAL_CLASSES
    
    def test_set_allowed_classes_dynamically(self):
        """Test dynamically updating allowed classes."""
        detector = YOLODetector(allowed_classes={"dog", "cat"})
        
        detections = [
            {"confidence": 0.8, "class_name": "dog", "bbox": [0, 0, 10, 10]},
            {"confidence": 0.7, "class_name": "horse", "bbox": [20, 20, 30, 30]},
        ]
        
        # Initially should only keep dog
        filtered = detector._filter_detections(detections)
        assert len(filtered) == 1
        
        # Update allowed classes
        detector.set_allowed_classes({"dog", "horse"})
        
        # Now should keep both
        filtered = detector._filter_detections(detections)
        assert len(filtered) == 2
