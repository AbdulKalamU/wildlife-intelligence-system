"""
Tests for Classification Module
"""

import pytest
import numpy as np
import torch
from wildlife_monitoring.classification import SpeciesClassifier, extract_roi, prepare_for_classification


class TestSpeciesClassifier:
    """Tests for SpeciesClassifier class."""
    
    def test_classifier_initialization(self):
        """Test classifier initialization."""
        classifier = SpeciesClassifier(confidence_threshold=0.3)
        assert classifier.confidence_threshold == 0.3
        assert classifier.model is not None
        assert classifier.device is not None
    
    def test_classifier_device_detection(self):
        """Test device auto-detection."""
        classifier = SpeciesClassifier()
        
        # Should detect cuda, mps, or cpu
        assert classifier.device.type in ["cuda", "mps", "cpu"]
    
    def test_classify_returns_dict(self):
        """Test that classify returns proper dictionary."""
        classifier = SpeciesClassifier()
        image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        result = classifier.classify(image)
        assert "species" in result
        assert "confidence" in result
        assert "probabilities" in result
        assert "wildlife_predictions" in result
    
    def test_classify_with_real_image(self):
        """Test classification with properly sized image."""
        classifier = SpeciesClassifier()
        # Create a more realistic image
        image = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
        
        result = classifier.classify(image)
        
        # Should return valid result
        assert isinstance(result["species"], str)
        assert 0 <= result["confidence"] <= 1
        assert isinstance(result["probabilities"], dict)
    
    def test_get_top_k_predictions(self):
        """Test top-k predictions."""
        classifier = SpeciesClassifier()
        image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        top_3 = classifier.get_top_k_predictions(image, k=3)
        
        assert len(top_3) <= 3
        assert all(isinstance(pred, tuple) for pred in top_3)
        assert all(len(pred) == 2 for pred in top_3)
    
    def test_batch_classification(self):
        """Test batch classification."""
        classifier = SpeciesClassifier()
        images = [
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            for _ in range(3)
        ]
        
        results = classifier.classify_batch(images)
        
        assert len(results) == 3
        assert all("species" in r for r in results)
        assert all("confidence" in r for r in results)
    
    def test_wildlife_class_mapping(self):
        """Test wildlife class mapping exists."""
        classifier = SpeciesClassifier()
        
        assert len(classifier.wildlife_class_indices) > 0
        assert all(isinstance(k, int) for k in classifier.wildlife_class_indices.keys())
        assert all(isinstance(v, str) for v in classifier.wildlife_class_indices.values())


class TestClassifierUtils:
    """Tests for classifier utility functions."""
    
    def test_extract_roi(self):
        """Test ROI extraction."""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        bbox = [100, 100, 200, 200]
        
        roi = extract_roi(frame, bbox)
        assert roi.shape == (100, 100, 3)
    
    def test_extract_roi_boundary_handling(self):
        """Test ROI extraction with boundary cases."""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Bbox extending beyond frame
        bbox = [600, 400, 700, 500]
        roi = extract_roi(frame, bbox)
        
        # Should clip to frame boundaries
        assert roi.shape[0] <= 100
        assert roi.shape[1] <= 100
    
    def test_prepare_for_classification(self):
        """Test image preparation for classification."""
        image = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
        
        prepared = prepare_for_classification(image, target_size=(224, 224))
        assert prepared.shape == (224, 224, 3)
    
    def test_prepare_grayscale_image(self):
        """Test preparation of grayscale image."""
        image = np.random.randint(0, 255, (300, 400), dtype=np.uint8)
        
        prepared = prepare_for_classification(image, target_size=(224, 224))
        assert prepared.shape == (224, 224, 3)  # Should convert to RGB
