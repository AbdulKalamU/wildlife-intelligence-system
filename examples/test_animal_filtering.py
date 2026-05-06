#!/usr/bin/env python
"""
Example: Animal Class Filtering

Demonstrates how to filter YOLO detections to only include specific animal classes
before passing to classification.

This example shows:
1. Setting up allowed animal classes
2. Detecting objects with filtering enabled
3. Handling "No wildlife detected" cases
4. Processing webcam frames with animal filtering
"""

import cv2
import numpy as np
from wildlife_monitoring import WildlifePipeline, PipelineConfig
from wildlife_monitoring.detection import YOLODetector, DEFAULT_ANIMAL_CLASSES


def example_1_basic_filtering():
    """
    Example 1: Basic animal class filtering with custom allowed classes.
    """
    print("=" * 60)
    print("Example 1: Basic Animal Class Filtering")
    print("=" * 60)
    
    # Define allowed animal classes (your requirement)
    ALLOWED_ANIMALS = {
        "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
    }
    
    # Initialize detector with filtering
    detector = YOLODetector(
        model_path="yolov8n.pt",
        confidence_threshold=0.5,
        allowed_classes=ALLOWED_ANIMALS
    )
    
    # Load a test image
    frame = cv2.imread("test_image.jpg")
    
    if frame is None:
        print("⚠️  No test image found. Using blank frame for demo.")
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
    
    # Detect with filtering enabled (default)
    detections = detector.detect(frame, filter_animals=True)
    
    # Get summary
    summary = detector.get_detection_summary(detections)
    
    print(f"\n{summary['message']}")
    if detections:
        print(f"Total detections: {summary['total_detections']}")
        print(f"Detected classes: {summary['classes']}")
        
        for i, det in enumerate(detections):
            print(f"  {i+1}. {det['class_name']} (confidence: {det['confidence']:.2f})")
    else:
        print("No wildlife detected")
    
    print()


def example_2_pipeline_with_filtering():
    """
    Example 2: Using pipeline with animal filtering.
    """
    print("=" * 60)
    print("Example 2: Pipeline with Animal Filtering")
    print("=" * 60)
    
    # Define allowed animal classes
    ALLOWED_ANIMALS = {
        "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
    }
    
    # Configure pipeline with filtering
    config = PipelineConfig(
        yolo_model_path="yolov8n.pt",
        detection_confidence=0.5,
        classification_enabled=True,
        classification_model="resnet50",
        classification_confidence=0.3,
        allowed_animal_classes=ALLOWED_ANIMALS,
        filter_non_animals=True  # Enable filtering
    )
    
    # Initialize pipeline
    pipeline = WildlifePipeline(config)
    
    # Load test frame
    frame = cv2.imread("test_image.jpg")
    
    if frame is None:
        print("⚠️  No test image found. Using blank frame for demo.")
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
    
    # Process frame
    result = pipeline.process_frame(frame, annotate=True)
    
    print(f"\nFrame {result.frame_number} processed:")
    print(f"  Detections: {len(result.detections)}")
    print(f"  Classifications: {len(result.classifications)}")
    print(f"  Active tracks: {len(result.tracks)}")
    
    if not result.detections:
        print("\n❌ No wildlife detected")
    else:
        print("\n✅ Wildlife detected:")
        for i, det in enumerate(result.detections):
            class_name = det['class_name']
            confidence = det['confidence']
            
            # Get classification if available
            if i in result.classifications:
                species = result.classifications[i]['species']
                species_conf = result.classifications[i]['confidence']
                print(f"  {i+1}. {class_name} → {species} ({species_conf:.2f})")
            else:
                print(f"  {i+1}. {class_name} ({confidence:.2f})")
    
    print()


def example_3_webcam_filtering():
    """
    Example 3: Real-time webcam with animal filtering.
    """
    print("=" * 60)
    print("Example 3: Webcam with Animal Filtering")
    print("=" * 60)
    print("Press 'q' to quit, 's' to toggle filtering")
    print()
    
    # Define allowed animal classes
    ALLOWED_ANIMALS = {
        "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
    }
    
    # Configure pipeline
    config = PipelineConfig(
        yolo_model_path="yolov8n.pt",
        detection_confidence=0.5,
        classification_enabled=False,  # Disable for speed
        allowed_animal_classes=ALLOWED_ANIMALS,
        filter_non_animals=True
    )
    
    pipeline = WildlifePipeline(config)
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Failed to open webcam")
        return
    
    filtering_enabled = True
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Toggle filtering based on state
            pipeline.config.filter_non_animals = filtering_enabled
            
            # Process frame
            result = pipeline.process_frame(frame, annotate=True)
            
            # Display info on frame
            info_text = f"Frame: {frame_count} | Detections: {len(result.detections)}"
            filter_text = f"Filtering: {'ON' if filtering_enabled else 'OFF'}"
            
            cv2.putText(
                result.annotated_frame if result.annotated_frame is not None else frame,
                info_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            cv2.putText(
                result.annotated_frame if result.annotated_frame is not None else frame,
                filter_text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0) if filtering_enabled else (0, 0, 255),
                2
            )
            
            # Show message if no wildlife
            if not result.detections and filtering_enabled:
                cv2.putText(
                    result.annotated_frame if result.annotated_frame is not None else frame,
                    "No wildlife detected",
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )
            
            # Display frame
            display_frame = result.annotated_frame if result.annotated_frame is not None else frame
            cv2.imshow("Wildlife Monitoring - Animal Filtering", display_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filtering_enabled = not filtering_enabled
                print(f"Filtering: {'ON' if filtering_enabled else 'OFF'}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    print(f"\nProcessed {frame_count} frames")


def example_4_compare_filtering():
    """
    Example 4: Compare detections with and without filtering.
    """
    print("=" * 60)
    print("Example 4: Compare With/Without Filtering")
    print("=" * 60)
    
    ALLOWED_ANIMALS = {
        "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
    }
    
    # Initialize detector
    detector = YOLODetector(
        model_path="yolov8n.pt",
        confidence_threshold=0.5,
        allowed_classes=ALLOWED_ANIMALS
    )
    
    # Load test frame
    frame = cv2.imread("test_image.jpg")
    
    if frame is None:
        print("⚠️  No test image found. Using blank frame for demo.")
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
    
    # Detect WITHOUT filtering
    print("\n1️⃣  WITHOUT filtering (all objects):")
    all_detections = detector.detect(frame, filter_animals=False)
    print(f"   Total detections: {len(all_detections)}")
    for det in all_detections:
        print(f"   - {det['class_name']} ({det['confidence']:.2f})")
    
    # Detect WITH filtering
    print("\n2️⃣  WITH filtering (animals only):")
    animal_detections = detector.detect(frame, filter_animals=True)
    print(f"   Total detections: {len(animal_detections)}")
    for det in animal_detections:
        print(f"   - {det['class_name']} ({det['confidence']:.2f})")
    
    # Summary
    filtered_out = len(all_detections) - len(animal_detections)
    print(f"\n📊 Summary:")
    print(f"   Total objects detected: {len(all_detections)}")
    print(f"   Animals detected: {len(animal_detections)}")
    print(f"   Non-animals filtered out: {filtered_out}")
    
    if not animal_detections:
        print("\n❌ No wildlife detected")
    
    print()


def main():
    """Run all examples."""
    print("\n🦌 Wildlife Monitoring - Animal Class Filtering Examples\n")
    
    # Run examples
    example_1_basic_filtering()
    example_2_pipeline_with_filtering()
    example_4_compare_filtering()
    
    # Uncomment to run webcam example
    # example_3_webcam_filtering()
    
    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
