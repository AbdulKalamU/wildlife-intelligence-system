"""
Example script to test the species classifier.

This script demonstrates how to use the SpeciesClassifier with a sample image.
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from wildlife_monitoring.classification import SpeciesClassifier


def test_classifier_with_random_image():
    """Test classifier with a random image."""
    print("=" * 60)
    print("Testing Species Classifier with Random Image")
    print("=" * 60)
    
    # Initialize classifier
    print("\n1. Initializing classifier...")
    classifier = SpeciesClassifier(
        model_name="resnet50",
        confidence_threshold=0.3
    )
    print(f"   Device: {classifier.device}")
    print(f"   Model: ResNet50 (ImageNet pretrained)")
    print(f"   Wildlife classes available: {len(classifier.wildlife_class_indices)}")
    
    # Create a random test image
    print("\n2. Creating test image (224x224x3)...")
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    # Classify
    print("\n3. Running classification...")
    result = classifier.classify(test_image)
    
    # Display results
    print("\n4. Classification Results:")
    print(f"   Species: {result['species']}")
    print(f"   Confidence: {result['confidence']:.4f}")
    
    if result['wildlife_predictions']:
        print("\n   Top Wildlife Predictions:")
        for i, pred in enumerate(result['wildlife_predictions'][:3], 1):
            print(f"   {i}. {pred['species']}: {pred['confidence']:.4f}")
    
    # Get top-k predictions
    print("\n5. Top-3 Overall Predictions:")
    top_3 = classifier.get_top_k_predictions(test_image, k=3)
    for i, (species, conf) in enumerate(top_3, 1):
        print(f"   {i}. {species}: {conf:.4f}")
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)


def test_classifier_with_image_file(image_path: str):
    """Test classifier with an actual image file."""
    print("=" * 60)
    print(f"Testing Species Classifier with Image: {image_path}")
    print("=" * 60)
    
    # Load image
    print("\n1. Loading image...")
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"   ERROR: Could not load image from {image_path}")
        return
    
    print(f"   Image shape: {image.shape}")
    
    # Initialize classifier
    print("\n2. Initializing classifier...")
    classifier = SpeciesClassifier(model_name="resnet50")
    print(f"   Device: {classifier.device}")
    
    # Classify
    print("\n3. Running classification...")
    result = classifier.classify(image)
    
    # Display results
    print("\n4. Classification Results:")
    print(f"   Species: {result['species']}")
    print(f"   Confidence: {result['confidence']:.4f}")
    
    if result['wildlife_predictions']:
        print("\n   Top Wildlife Predictions:")
        for i, pred in enumerate(result['wildlife_predictions'][:3], 1):
            print(f"   {i}. {pred['species']}: {pred['confidence']:.4f}")
    
    print("\n" + "=" * 60)


def test_batch_classification():
    """Test batch classification."""
    print("=" * 60)
    print("Testing Batch Classification")
    print("=" * 60)
    
    # Initialize classifier
    print("\n1. Initializing classifier...")
    classifier = SpeciesClassifier()
    
    # Create batch of test images
    print("\n2. Creating batch of 5 test images...")
    batch_images = [
        np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        for _ in range(5)
    ]
    
    # Classify batch
    print("\n3. Running batch classification...")
    results = classifier.classify_batch(batch_images)
    
    # Display results
    print("\n4. Batch Results:")
    for i, result in enumerate(results, 1):
        print(f"\n   Image {i}:")
        print(f"   - Species: {result['species']}")
        print(f"   - Confidence: {result['confidence']:.4f}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Test with random image
    test_classifier_with_random_image()
    
    print("\n\n")
    
    # Test batch classification
    test_batch_classification()
    
    # Uncomment to test with actual image file
    # test_classifier_with_image_file("path/to/your/image.jpg")
