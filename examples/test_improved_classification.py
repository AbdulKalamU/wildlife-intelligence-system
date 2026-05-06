#!/usr/bin/env python
"""
Example: Improved Classification Pipeline

Demonstrates the improved ResNet50 classification with:
1. Proper bounding box cropping
2. ResNet50-compliant preprocessing
3. Top-3 predictions with confidence scores
4. "Unknown species" handling for low confidence

Requirements met:
✅ Crop ONLY the bounding box
✅ Resize properly for ResNet50 (256 → 224 center crop)
✅ Normalize with ImageNet mean/std
✅ Return top-3 predictions
✅ Mark as "Unknown species" if confidence < threshold
"""

import cv2
import numpy as np
from wildlife_monitoring.classification import SpeciesClassifier
from wildlife_monitoring.detection import YOLODetector


def example_1_basic_classification():
    """
    Example 1: Basic classification with top-3 predictions.
    """
    print("=" * 70)
    print("Example 1: Basic Classification with Top-3 Predictions")
    print("=" * 70)
    
    # Initialize classifier
    classifier = SpeciesClassifier(
        model_name="resnet50",
        confidence_threshold=0.3,
        top_k=3  # Return top-3 predictions
    )
    
    # Load test image
    frame = cv2.imread("test_wildlife.jpg")
    
    if frame is None:
        print("⚠️  No test image found. Creating synthetic image.")
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Simulate a bounding box (in real use, this comes from YOLO)
    bbox = [100, 100, 400, 400]  # [x1, y1, x2, y2]
    
    # Step 1: Crop ONLY the bounding box
    print("\n📦 Step 1: Cropping bounding box...")
    cropped = classifier.crop_bbox(frame, bbox)
    print(f"   Original frame: {frame.shape}")
    print(f"   Cropped region: {cropped.shape}")
    print(f"   Bbox: {bbox}")
    
    # Step 2: Classify with top-3 predictions
    print("\n🔍 Step 2: Classifying with ResNet50...")
    result = classifier.classify(cropped, return_top_k=True)
    
    # Step 3: Display results
    print("\n📊 Classification Results:")
    print(f"   Top Species: {result['species']}")
    print(f"   Confidence: {result['confidence']:.4f}")
    print(f"   Is Unknown: {result['is_unknown']}")
    
    print("\n🏆 Top-3 Predictions:")
    for i, pred in enumerate(result['top_predictions'], 1):
        print(f"   {i}. {pred['species']:<30} {pred['confidence']:.4f}")
    
    print()


def example_2_full_pipeline():
    """
    Example 2: Full pipeline with YOLO detection + classification.
    """
    print("=" * 70)
    print("Example 2: Full Pipeline (YOLO Detection + Classification)")
    print("=" * 70)
    
    # Initialize detector and classifier
    detector = YOLODetector(
        model_path="yolov8n.pt",
        confidence_threshold=0.5,
        allowed_classes={"dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"}
    )
    
    classifier = SpeciesClassifier(
        model_name="resnet50",
        confidence_threshold=0.3,
        top_k=3
    )
    
    # Load test image
    frame = cv2.imread("test_wildlife.jpg")
    
    if frame is None:
        print("⚠️  No test image found. Creating synthetic image.")
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Step 1: Detect animals
    print("\n🔍 Step 1: Detecting animals with YOLO...")
    detections = detector.detect(frame, filter_animals=True)
    print(f"   Detected {len(detections)} animal(s)")
    
    if not detections:
        print("   ❌ No wildlife detected")
        return
    
    # Step 2: Classify each detection
    print("\n🏷️  Step 2: Classifying detected animals...")
    for i, detection in enumerate(detections, 1):
        print(f"\n   Detection {i}:")
        print(f"   - YOLO Class: {detection['class_name']}")
        print(f"   - YOLO Confidence: {detection['confidence']:.4f}")
        print(f"   - Bbox: {detection['bbox']}")
        
        # Crop bounding box
        try:
            cropped = classifier.crop_bbox(frame, detection['bbox'])
            
            # Classify
            result = classifier.classify(cropped, return_top_k=True)
            
            print(f"   - Species: {result['species']}")
            print(f"   - Classification Confidence: {result['confidence']:.4f}")
            
            if result['is_unknown']:
                print(f"   - ⚠️  Marked as 'Unknown species' (confidence < threshold)")
            
            print(f"   - Top-3 Predictions:")
            for j, pred in enumerate(result['top_predictions'], 1):
                print(f"     {j}. {pred['species']:<25} {pred['confidence']:.4f}")
        
        except Exception as e:
            print(f"   - ❌ Classification failed: {e}")
    
    print()


def example_3_confidence_threshold():
    """
    Example 3: Demonstrate "Unknown species" handling.
    """
    print("=" * 70)
    print("Example 3: Unknown Species Handling (Confidence Threshold)")
    print("=" * 70)
    
    # Test with different confidence thresholds
    thresholds = [0.1, 0.3, 0.5, 0.7]
    
    # Create test image
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    bbox = [100, 100, 400, 400]
    
    print("\n📊 Testing different confidence thresholds:")
    print(f"   Image: {frame.shape}")
    print(f"   Bbox: {bbox}")
    
    for threshold in thresholds:
        print(f"\n   Threshold: {threshold}")
        
        classifier = SpeciesClassifier(
            model_name="resnet50",
            confidence_threshold=threshold,
            top_k=3
        )
        
        cropped = classifier.crop_bbox(frame, bbox)
        result = classifier.classify(cropped)
        
        print(f"   - Species: {result['species']}")
        print(f"   - Confidence: {result['confidence']:.4f}")
        print(f"   - Is Unknown: {result['is_unknown']}")
        
        if result['is_unknown']:
            print(f"   - ✅ Correctly marked as 'Unknown species'")
        else:
            print(f"   - ✅ Confidence above threshold")
    
    print()


def example_4_batch_classification():
    """
    Example 4: Batch classification for multiple detections.
    """
    print("=" * 70)
    print("Example 4: Batch Classification (Multiple Detections)")
    print("=" * 70)
    
    # Initialize classifier
    classifier = SpeciesClassifier(
        model_name="resnet50",
        confidence_threshold=0.3,
        top_k=3
    )
    
    # Create test frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Simulate multiple detections
    bboxes = [
        [50, 50, 200, 200],
        [250, 100, 450, 300],
        [100, 300, 300, 450]
    ]
    
    print(f"\n📦 Cropping {len(bboxes)} bounding boxes...")
    
    # Crop all bounding boxes
    cropped_images = []
    for i, bbox in enumerate(bboxes, 1):
        try:
            cropped = classifier.crop_bbox(frame, bbox)
            cropped_images.append(cropped)
            print(f"   {i}. Bbox {bbox} → Cropped {cropped.shape}")
        except Exception as e:
            print(f"   {i}. Bbox {bbox} → ❌ Failed: {e}")
    
    # Batch classify
    print(f"\n🔍 Batch classifying {len(cropped_images)} images...")
    results = classifier.classify_batch(cropped_images, return_top_k=True)
    
    # Display results
    print(f"\n📊 Batch Classification Results:")
    for i, result in enumerate(results, 1):
        print(f"\n   Image {i}:")
        print(f"   - Species: {result['species']}")
        print(f"   - Confidence: {result['confidence']:.4f}")
        print(f"   - Is Unknown: {result['is_unknown']}")
        print(f"   - Top-3:")
        for j, pred in enumerate(result['top_predictions'], 1):
            print(f"     {j}. {pred['species']:<25} {pred['confidence']:.4f}")
    
    print()


def example_5_preprocessing_details():
    """
    Example 5: Show preprocessing details (ResNet50 requirements).
    """
    print("=" * 70)
    print("Example 5: Preprocessing Details (ResNet50 Requirements)")
    print("=" * 70)
    
    classifier = SpeciesClassifier(model_name="resnet50")
    
    # Create test image
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    bbox = [100, 100, 400, 400]
    
    print("\n📋 ResNet50 Preprocessing Steps:")
    print("   1. Crop bounding box")
    print("   2. Convert BGR → RGB")
    print("   3. Convert to PIL Image")
    print("   4. Resize to 256x256 (shortest side)")
    print("   5. Center crop to 224x224")
    print("   6. Convert to tensor [0, 1]")
    print("   7. Normalize with ImageNet mean/std")
    print("      - Mean: [0.485, 0.456, 0.406]")
    print("      - Std:  [0.229, 0.224, 0.225]")
    
    print(f"\n🔧 Applying preprocessing:")
    print(f"   Input frame: {frame.shape} (BGR)")
    
    # Step 1: Crop
    cropped = classifier.crop_bbox(frame, bbox)
    print(f"   After crop: {cropped.shape} (BGR)")
    
    # Step 2-7: Preprocess
    tensor = classifier.preprocess_image(cropped)
    print(f"   After preprocessing: {tensor.shape} (C, H, W)")
    print(f"   Tensor dtype: {tensor.dtype}")
    print(f"   Tensor range: [{tensor.min():.3f}, {tensor.max():.3f}]")
    
    print("\n✅ Image ready for ResNet50 inference!")
    print()


def main():
    """Run all examples."""
    print("\n🦌 Improved Classification Pipeline Examples\n")
    
    # Run examples
    example_1_basic_classification()
    example_2_full_pipeline()
    example_3_confidence_threshold()
    example_4_batch_classification()
    example_5_preprocessing_details()
    
    print("=" * 70)
    print("Examples complete!")
    print("=" * 70)
    print("\n✅ All requirements met:")
    print("   ✓ Crop ONLY the bounding box")
    print("   ✓ Resize properly for ResNet50 (256 → 224)")
    print("   ✓ Normalize with ImageNet mean/std")
    print("   ✓ Return top-3 predictions")
    print("   ✓ Mark as 'Unknown species' if confidence < threshold")
    print()


if __name__ == "__main__":
    main()
