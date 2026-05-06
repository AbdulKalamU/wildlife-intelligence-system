#!/usr/bin/env python
"""
Example: Modular Pipeline

Demonstrates the clean modular pipeline with separate stages:
Frame → Detection → Filter → Crop → Classification → Tracking

Each stage is a separate function with clear data flow.
"""

import cv2
import numpy as np
from wildlife_monitoring.pipeline.modular_pipeline import (
    process_frame_modular,
    create_modular_pipeline,
    stage_detection,
    stage_filter,
    stage_crop,
    stage_classification,
    stage_tracking
)


def example_1_full_pipeline():
    """
    Example 1: Full modular pipeline on a single frame.
    """
    print("=" * 70)
    print("Example 1: Full Modular Pipeline")
    print("=" * 70)
    
    # Define allowed animal classes
    ALLOWED_ANIMALS = {
        "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
    }
    
    # Create pipeline components
    print("\n📦 Creating pipeline components...")
    detector, classifier, tracker = create_modular_pipeline(
        yolo_model_path="yolov8n.pt",
        detection_confidence=0.5,
        classification_enabled=True,
        classification_model="resnet50",
        classification_confidence=0.3,
        allowed_animal_classes=ALLOWED_ANIMALS,
        tracking_max_disappeared=50
    )
    print("   ✅ Detector, Classifier, and Tracker initialized")
    
    # Load test frame
    frame = cv2.imread("test_wildlife.jpg")
    if frame is None:
        print("   ⚠️  No test image found. Creating synthetic frame.")
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    print(f"   Frame shape: {frame.shape}")
    
    # Process frame through modular pipeline
    print("\n🔄 Processing frame through pipeline...")
    state = process_frame_modular(
        frame=frame,
        frame_number=1,
        detector=detector,
        classifier=classifier,
        tracker=tracker,
        allowed_classes=ALLOWED_ANIMALS,
        apply_filter=True,
        annotate=True
    )
    
    # Display results from each stage
    print("\n📊 Pipeline Results:")
    print(f"   Stage 1 (Detection):     {len(state.raw_detections)} object(s) detected")
    print(f"   Stage 2 (Filter):        {len(state.filtered_detections)} animal(s) kept")
    print(f"   Stage 3 (Crop):          {len(state.cropped_images)} image(s) cropped")
    print(f"   Stage 4 (Classification): {len(state.classifications)} animal(s) classified")
    print(f"   Stage 5 (Tracking):      {len(state.tracks)} track(s) active")
    
    # Show detailed results
    if state.filtered_detections:
        print("\n🦌 Detected Animals:")
        for i, det in enumerate(state.filtered_detections):
            print(f"\n   Animal {i+1}:")
            print(f"   - YOLO Class: {det['class_name']}")
            print(f"   - YOLO Confidence: {det['confidence']:.4f}")
            print(f"   - Bbox: {det['bbox']}")
            
            if i in state.classifications:
                cls = state.classifications[i]
                print(f"   - Species: {cls['species']}")
                print(f"   - Classification Confidence: {cls['confidence']:.4f}")
                print(f"   - Is Unknown: {cls['is_unknown']}")
                
                if 'top_predictions' in cls:
                    print(f"   - Top-3 Predictions:")
                    for j, pred in enumerate(cls['top_predictions'], 1):
                        print(f"     {j}. {pred['species']}: {pred['confidence']:.4f}")
    else:
        print("\n   ❌ No wildlife detected")
    
    # Display annotated frame
    if state.annotated_frame is not None:
        print("\n🖼️  Annotated frame available")
        # cv2.imshow("Modular Pipeline", state.annotated_frame)
        # cv2.waitKey(0)
    
    print()


def example_2_stage_by_stage():
    """
    Example 2: Run each stage separately to show data flow.
    """
    print("=" * 70)
    print("Example 2: Stage-by-Stage Execution")
    print("=" * 70)
    
    ALLOWED_ANIMALS = {"dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"}
    
    # Create components
    detector, classifier, tracker = create_modular_pipeline(
        allowed_animal_classes=ALLOWED_ANIMALS
    )
    
    # Create test frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    print("\n" + "="*70)
    print("STAGE 1: DETECTION")
    print("="*70)
    detection_result = stage_detection(frame, detector, apply_filter=False)
    print(f"Success: {detection_result.success}")
    print(f"Message: {detection_result.message}")
    print(f"Detections: {len(detection_result.data)}")
    
    print("\n" + "="*70)
    print("STAGE 2: FILTER")
    print("="*70)
    filter_result = stage_filter(detection_result.data, ALLOWED_ANIMALS)
    print(f"Success: {filter_result.success}")
    print(f"Message: {filter_result.message}")
    print(f"Filtered: {len(filter_result.data)}")
    
    if filter_result.data:
        print("\n" + "="*70)
        print("STAGE 3: CROP")
        print("="*70)
        crop_result = stage_crop(frame, filter_result.data, classifier)
        cropped_images, crop_indices = crop_result.data
        print(f"Success: {crop_result.success}")
        print(f"Message: {crop_result.message}")
        print(f"Cropped: {len(cropped_images)}")
        
        if cropped_images:
            print("\n" + "="*70)
            print("STAGE 4: CLASSIFICATION")
            print("="*70)
            classification_result = stage_classification(
                cropped_images, crop_indices, classifier
            )
            print(f"Success: {classification_result.success}")
            print(f"Message: {classification_result.message}")
            print(f"Classifications: {len(classification_result.data)}")
        
        print("\n" + "="*70)
        print("STAGE 5: TRACKING")
        print("="*70)
        tracking_result = stage_tracking(filter_result.data, tracker)
        print(f"Success: {tracking_result.success}")
        print(f"Message: {tracking_result.message}")
        print(f"Tracks: {len(tracking_result.data)}")
    else:
        print("\n⚠️  No animals detected - skipping remaining stages")
    
    print()


def example_3_no_animals_detected():
    """
    Example 3: Handle case where no animals are detected.
    """
    print("=" * 70)
    print("Example 3: No Animals Detected (Graceful Handling)")
    print("=" * 70)
    
    ALLOWED_ANIMALS = {"dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"}
    
    # Create pipeline
    detector, classifier, tracker = create_modular_pipeline(
        allowed_animal_classes=ALLOWED_ANIMALS
    )
    
    # Create frame with no animals (blank frame)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    print("\n🔄 Processing frame with no animals...")
    state = process_frame_modular(
        frame=frame,
        frame_number=1,
        detector=detector,
        classifier=classifier,
        tracker=tracker,
        allowed_classes=ALLOWED_ANIMALS,
        apply_filter=True,
        annotate=True
    )
    
    print("\n📊 Results:")
    print(f"   Raw Detections: {len(state.raw_detections)}")
    print(f"   Filtered Detections: {len(state.filtered_detections)}")
    print(f"   Cropped Images: {len(state.cropped_images)}")
    print(f"   Classifications: {len(state.classifications)}")
    print(f"   Tracks: {len(state.tracks)}")
    
    if not state.filtered_detections:
        print("\n   ✅ Correctly handled: No wildlife detected")
        print("   ✅ Pipeline completed without errors")
        print("   ✅ Annotated frame shows 'No wildlife detected' message")
    
    print()


def example_4_video_processing():
    """
    Example 4: Process video with modular pipeline.
    """
    print("=" * 70)
    print("Example 4: Video Processing with Modular Pipeline")
    print("=" * 70)
    
    ALLOWED_ANIMALS = {"dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"}
    
    # Create pipeline
    detector, classifier, tracker = create_modular_pipeline(
        allowed_animal_classes=ALLOWED_ANIMALS,
        classification_enabled=False  # Disable for speed
    )
    
    # Open video (or webcam)
    video_path = "test_video.mp4"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"   ⚠️  Could not open video: {video_path}")
        print("   Using webcam instead (index 0)")
        cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("   ❌ Could not open video source")
        return
    
    print(f"\n🎥 Processing video...")
    print("   Press 'q' to quit")
    
    frame_count = 0
    total_detections = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process frame
            state = process_frame_modular(
                frame=frame,
                frame_number=frame_count,
                detector=detector,
                classifier=classifier,
                tracker=tracker,
                allowed_classes=ALLOWED_ANIMALS,
                apply_filter=True,
                annotate=True
            )
            
            total_detections += len(state.filtered_detections)
            
            # Display annotated frame
            if state.annotated_frame is not None:
                # Add frame info
                info_text = f"Frame: {frame_count} | Animals: {len(state.filtered_detections)} | Tracks: {len(state.tracks)}"
                cv2.putText(
                    state.annotated_frame,
                    info_text,
                    (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )
                
                cv2.imshow("Modular Pipeline - Video", state.annotated_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    print(f"\n📊 Video Processing Summary:")
    print(f"   Total Frames: {frame_count}")
    print(f"   Total Detections: {total_detections}")
    print(f"   Average Detections/Frame: {total_detections/frame_count if frame_count > 0 else 0:.2f}")
    
    print()


def example_5_data_flow_visualization():
    """
    Example 5: Visualize data flow through pipeline stages.
    """
    print("=" * 70)
    print("Example 5: Data Flow Visualization")
    print("=" * 70)
    
    ALLOWED_ANIMALS = {"dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"}
    
    # Create pipeline
    detector, classifier, tracker = create_modular_pipeline(
        allowed_animal_classes=ALLOWED_ANIMALS
    )
    
    # Create test frame
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Process frame
    state = process_frame_modular(
        frame=frame,
        frame_number=1,
        detector=detector,
        classifier=classifier,
        tracker=tracker,
        allowed_classes=ALLOWED_ANIMALS,
        apply_filter=True,
        annotate=False
    )
    
    # Visualize data flow
    print("\n📊 Data Flow Through Pipeline:")
    print()
    print("   ┌─────────────────┐")
    print("   │  Input Frame    │")
    print(f"   │  {frame.shape}  │")
    print("   └────────┬────────┘")
    print("            │")
    print("            ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │  Stage 1: Detection             │")
    print(f"   │  Output: {len(state.raw_detections)} detection(s)           │")
    print("   └────────┬────────────────────────┘")
    print("            │")
    print("            ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │  Stage 2: Filter                │")
    print(f"   │  Output: {len(state.filtered_detections)} animal(s)              │")
    print("   └────────┬────────────────────────┘")
    print("            │")
    print("            ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │  Stage 3: Crop                  │")
    print(f"   │  Output: {len(state.cropped_images)} cropped image(s)       │")
    print("   └────────┬────────────────────────┘")
    print("            │")
    print("            ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │  Stage 4: Classification        │")
    print(f"   │  Output: {len(state.classifications)} classification(s)      │")
    print("   └────────┬────────────────────────┘")
    print("            │")
    print("            ▼")
    print("   ┌─────────────────────────────────┐")
    print("   │  Stage 5: Tracking              │")
    print(f"   │  Output: {len(state.tracks)} track(s)                │")
    print("   └─────────────────────────────────┘")
    print()


def main():
    """Run all examples."""
    print("\n🦌 Modular Pipeline Examples\n")
    
    # Run examples
    example_1_full_pipeline()
    example_2_stage_by_stage()
    example_3_no_animals_detected()
    example_5_data_flow_visualization()
    
    # Uncomment to run video example
    # example_4_video_processing()
    
    print("=" * 70)
    print("Examples complete!")
    print("=" * 70)
    print("\n✅ Modular Pipeline Features:")
    print("   ✓ Separate function for each stage")
    print("   ✓ Clean data flow between stages")
    print("   ✓ Handles 'no animals detected' gracefully")
    print("   ✓ Well-commented code")
    print("   ✓ Easy to debug and extend")
    print()


if __name__ == "__main__":
    main()
