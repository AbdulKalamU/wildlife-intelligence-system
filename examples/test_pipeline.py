"""
Example script to test the complete wildlife monitoring pipeline.

Demonstrates the orchestrator connecting all modules:
1. Frame reading
2. Detection (YOLO)
3. Classification (ResNet)
4. Tracking (Centroid)
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from wildlife_monitoring.pipeline import WildlifePipeline, PipelineConfig


def test_pipeline_single_frame():
    """Test pipeline with a single frame."""
    print("=" * 70)
    print("Testing Pipeline - Single Frame")
    print("=" * 70)
    
    # Configure pipeline
    print("\n1. Configuring pipeline...")
    config = PipelineConfig(
        yolo_model_path="yolov8n.pt",
        detection_confidence=0.5,
        classification_model="resnet50",
        classification_confidence=0.3,
        classification_enabled=True,
        tracking_max_disappeared=50,
        frame_skip=1
    )
    
    # Initialize pipeline
    print("2. Initializing pipeline...")
    pipeline = WildlifePipeline(config)
    print(f"   ✓ Detector loaded: YOLOv8")
    print(f"   ✓ Classifier loaded: ResNet50")
    print(f"   ✓ Tracker initialized")
    
    # Create test frame
    print("\n3. Creating test frame (640x480)...")
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Process frame
    print("\n4. Processing frame through pipeline...")
    result = pipeline.process_frame(frame, annotate=True)
    
    # Display results
    print("\n5. Pipeline Results:")
    print(f"   Frame number: {result.frame_number}")
    print(f"   Detections: {len(result.detections)}")
    print(f"   Classifications: {len(result.classifications)}")
    print(f"   Active tracks: {len(result.tracks)}")
    
    if result.detections:
        print("\n   Detection Details:")
        for i, det in enumerate(result.detections):
            print(f"   [{i}] {det['class_name']}: {det['confidence']:.2f}")
            
            if i in result.classifications:
                cls = result.classifications[i]
                print(f"       → Species: {cls['species']} ({cls['confidence']:.2f})")
    
    if result.tracks:
        print("\n   Track Details:")
        for track_id, track_info in result.tracks.items():
            print(f"   Track {track_id}:")
            print(f"     - Centroid: {track_info['centroid']}")
            print(f"     - Disappeared: {track_info['disappeared_frames']} frames")
    
    # Get statistics
    stats = pipeline.get_statistics()
    print("\n6. Pipeline Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 70)
    print("Single frame test completed!")
    print("=" * 70)


def test_pipeline_multiple_frames():
    """Test pipeline with multiple frames (simulated video)."""
    print("\n\n" + "=" * 70)
    print("Testing Pipeline - Multiple Frames")
    print("=" * 70)
    
    # Configure pipeline
    config = PipelineConfig(
        detection_confidence=0.5,
        classification_enabled=True,
        frame_skip=1
    )
    
    # Initialize pipeline
    print("\n1. Initializing pipeline...")
    pipeline = WildlifePipeline(config)
    
    # Simulate video frames
    print("\n2. Processing 10 simulated frames...")
    num_frames = 10
    
    for i in range(num_frames):
        # Create frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Process
        result = pipeline.process_frame(frame, annotate=False)
        
        print(f"   Frame {result.frame_number}: "
              f"{len(result.detections)} detections, "
              f"{len(result.tracks)} tracks")
    
    # Get track summaries
    print("\n3. Track Summaries:")
    summaries = pipeline.get_track_summaries()
    
    if summaries:
        for summary in summaries:
            print(f"\n   Track {summary['track_id']}:")
            print(f"     Duration: {summary['duration_seconds']:.2f}s")
            print(f"     Frames: {summary['total_frames']}")
            print(f"     Species: {summary['dominant_species']}")
    else:
        print("   No tracks detected")
    
    # Final statistics
    stats = pipeline.get_statistics()
    print("\n4. Final Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 70)
    print("Multiple frames test completed!")
    print("=" * 70)


def test_pipeline_with_video(video_path: str):
    """Test pipeline with actual video file."""
    print("\n\n" + "=" * 70)
    print(f"Testing Pipeline - Video File: {video_path}")
    print("=" * 70)
    
    # Check if video exists
    if not Path(video_path).exists():
        print(f"\n❌ Video file not found: {video_path}")
        print("   Skipping video test...")
        return
    
    # Configure pipeline
    config = PipelineConfig(
        detection_confidence=0.5,
        classification_enabled=True,
        frame_skip=2  # Process every 2nd frame for speed
    )
    
    # Initialize pipeline
    print("\n1. Initializing pipeline...")
    pipeline = WildlifePipeline(config)
    
    # Process video
    print("\n2. Processing video...")
    output_path = "output_annotated.mp4"
    
    try:
        results = pipeline.process_video(
            video_source=video_path,
            annotate=True,
            save_output=output_path
        )
        
        print(f"\n3. Processing complete!")
        print(f"   Total frames: {len(results)}")
        print(f"   Output saved to: {output_path}")
        
        # Analyze results
        total_detections = sum(len(r.detections) for r in results)
        frames_with_detections = sum(1 for r in results if r.detections)
        
        print(f"\n4. Analysis:")
        print(f"   Total detections: {total_detections}")
        print(f"   Frames with detections: {frames_with_detections}")
        print(f"   Detection rate: {frames_with_detections/len(results)*100:.1f}%")
        
        # Track summaries
        summaries = pipeline.get_track_summaries()
        print(f"\n5. Tracks: {len(summaries)}")
        
        for summary in summaries[:5]:  # Show first 5
            print(f"\n   Track {summary['track_id']}:")
            print(f"     Duration: {summary['duration_seconds']:.2f}s")
            print(f"     Frames: {summary['total_frames']}")
            print(f"     Species: {summary['dominant_species']}")
        
        if len(summaries) > 5:
            print(f"\n   ... and {len(summaries) - 5} more tracks")
        
    except Exception as e:
        print(f"\n❌ Error processing video: {e}")
    
    print("\n" + "=" * 70)


def test_pipeline_configuration():
    """Test different pipeline configurations."""
    print("\n\n" + "=" * 70)
    print("Testing Pipeline - Different Configurations")
    print("=" * 70)
    
    configs = [
        ("Fast (no classification)", PipelineConfig(
            classification_enabled=False,
            frame_skip=2
        )),
        ("Accurate (with classification)", PipelineConfig(
            classification_enabled=True,
            classification_model="resnet50",
            frame_skip=1
        )),
        ("Balanced", PipelineConfig(
            classification_enabled=True,
            classification_model="efficientnet_b0",
            frame_skip=2
        ))
    ]
    
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    for name, config in configs:
        print(f"\n{name}:")
        print(f"  Classification: {config.classification_enabled}")
        print(f"  Frame skip: {config.frame_skip}")
        
        pipeline = WildlifePipeline(config)
        result = pipeline.process_frame(frame)
        
        print(f"  Result: {len(result.detections)} detections, "
              f"{len(result.classifications)} classifications")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Test 1: Single frame
    test_pipeline_single_frame()
    
    # Test 2: Multiple frames
    test_pipeline_multiple_frames()
    
    # Test 3: Different configurations
    test_pipeline_configuration()
    
    # Test 4: Video file (if available)
    # Uncomment and provide path to test with actual video
    # test_pipeline_with_video("data/videos/wildlife.mp4")
    
    print("\n\n✅ All pipeline tests completed!")
