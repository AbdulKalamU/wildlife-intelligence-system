#!/usr/bin/env python
"""
Example: Database Integration

Demonstrates SQLite database integration with wildlife monitoring pipeline.

Features:
- Automatic table creation
- Insert sightings for tracked animals
- Duplicate prevention
- Query utilities
"""

import cv2
import numpy as np
from datetime import datetime
from wildlife_monitoring.database import WildlifeDatabase
from wildlife_monitoring.pipeline.modular_pipeline import (
    process_frame_modular,
    create_modular_pipeline
)


def example_1_basic_database_operations():
    """
    Example 1: Basic database operations.
    """
    print("=" * 70)
    print("Example 1: Basic Database Operations")
    print("=" * 70)
    
    # Initialize database
    print("\n📦 Initializing database...")
    db = WildlifeDatabase("wildlife_test.db")
    print("   ✅ Database initialized: wildlife_test.db")
    print("   ✅ Table 'sightings' created")
    
    # Insert a sighting
    print("\n📝 Inserting sighting...")
    sighting_id = db.insert_sighting(
        species="Red Fox",
        confidence=0.85,
        track_id=1,
        frame_number=100,
        timestamp=datetime.now(),
        bbox=[100, 100, 300, 300],
        location="Forest Area A"
    )
    print(f"   ✅ Inserted sighting with ID: {sighting_id}")
    
    # Try to insert duplicate (same track_id and frame_number)
    print("\n🔄 Attempting duplicate insert...")
    duplicate_id = db.insert_sighting(
        species="Red Fox",
        confidence=0.85,
        track_id=1,
        frame_number=100,  # Same track_id and frame_number
        timestamp=datetime.now()
    )
    if duplicate_id is None:
        print("   ✅ Duplicate prevented (returned None)")
    else:
        print(f"   ❌ Duplicate inserted: {duplicate_id}")
    
    # Insert another sighting (different frame)
    print("\n📝 Inserting another sighting (different frame)...")
    sighting_id_2 = db.insert_sighting(
        species="Red Fox",
        confidence=0.82,
        track_id=1,
        frame_number=101,  # Different frame
        timestamp=datetime.now(),
        bbox=[105, 105, 305, 305]
    )
    print(f"   ✅ Inserted sighting with ID: {sighting_id_2}")
    
    # Query sightings
    print("\n🔍 Querying sightings by track ID...")
    sightings = db.get_sightings_by_track(track_id=1)
    print(f"   Found {len(sightings)} sighting(s) for track 1:")
    for s in sightings:
        print(f"   - Frame {s['frame_number']}: {s['species']} ({s['confidence']:.2f})")
    
    # Get statistics
    print("\n📊 Database statistics:")
    stats = db.get_statistics()
    print(f"   Total sightings: {stats['total_sightings']}")
    print(f"   Unique tracks: {stats['unique_tracks']}")
    print(f"   Unique species: {stats['unique_species']}")
    
    # Close database
    db.close()
    print("\n✅ Database closed")
    print()


def example_2_pipeline_integration():
    """
    Example 2: Integrate database with pipeline.
    """
    print("=" * 70)
    print("Example 2: Pipeline Integration with Database")
    print("=" * 70)
    
    ALLOWED_ANIMALS = {
        "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
    }
    
    # Initialize database
    print("\n📦 Initializing database...")
    db = WildlifeDatabase("wildlife_pipeline.db")
    
    # Create pipeline
    print("\n🔧 Creating pipeline...")
    detector, classifier, tracker = create_modular_pipeline(
        yolo_model_path="yolov8n.pt",
        classification_enabled=True,
        allowed_animal_classes=ALLOWED_ANIMALS
    )
    
    # Load test frame
    frame = cv2.imread("test_wildlife.jpg")
    if frame is None:
        print("   ⚠️  No test image found. Creating synthetic frame.")
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Process frame
    print("\n🔄 Processing frame...")
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
    
    print(f"   Detected {len(state.filtered_detections)} animal(s)")
    print(f"   Classified {len(state.classifications)} animal(s)")
    print(f"   Tracking {len(state.tracks)} object(s)")
    
    # Insert sightings into database
    print("\n💾 Saving sightings to database...")
    inserted_count = 0
    
    for track_id, track_info in state.tracks.items():
        # Find corresponding detection and classification
        det_idx = None
        for i, det in enumerate(state.filtered_detections):
            # Match by bbox (simple IoU check)
            if _bboxes_similar(track_info["bbox"], det["bbox"]):
                det_idx = i
                break
        
        # Get classification if available
        species = "Unknown"
        confidence = 0.0
        
        if det_idx is not None and det_idx in state.classifications:
            cls = state.classifications[det_idx]
            species = cls["species"]
            confidence = cls["confidence"]
        
        # Insert into database
        sighting_id = db.insert_sighting(
            species=species,
            confidence=confidence,
            track_id=track_id,
            frame_number=state.frame_number,
            timestamp=datetime.now(),
            bbox=track_info["bbox"]
        )
        
        if sighting_id is not None:
            inserted_count += 1
            print(f"   ✅ Inserted: Track {track_id} - {species} ({confidence:.2f})")
        else:
            print(f"   ⚠️  Skipped duplicate: Track {track_id}")
    
    print(f"\n📊 Inserted {inserted_count} sighting(s)")
    
    # Query results
    print("\n🔍 Querying database...")
    recent = db.get_recent_sightings(limit=10)
    print(f"   Recent sightings: {len(recent)}")
    for s in recent:
        print(f"   - Track {s['track_id']}: {s['species']} ({s['confidence']:.2f})")
    
    db.close()
    print()


def example_3_video_with_database():
    """
    Example 3: Process video and save all sightings to database.
    """
    print("=" * 70)
    print("Example 3: Video Processing with Database")
    print("=" * 70)
    
    ALLOWED_ANIMALS = {
        "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
    }
    
    # Initialize database
    db = WildlifeDatabase("wildlife_video.db")
    
    # Create pipeline
    detector, classifier, tracker = create_modular_pipeline(
        yolo_model_path="yolov8n.pt",
        classification_enabled=False,  # Disable for speed
        allowed_animal_classes=ALLOWED_ANIMALS
    )
    
    # Open video
    video_path = "test_video.mp4"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"   ⚠️  Could not open video: {video_path}")
        print("   Using webcam instead")
        cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("   ❌ Could not open video source")
        db.close()
        return
    
    print(f"\n🎥 Processing video...")
    print("   Press 'q' to quit")
    
    frame_count = 0
    total_inserted = 0
    
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
                annotate=False
            )
            
            # Insert sightings for each track
            for track_id, track_info in state.tracks.items():
                sighting_id = db.insert_sighting(
                    species="Animal",  # Generic since classification disabled
                    confidence=1.0,
                    track_id=track_id,
                    frame_number=frame_count,
                    timestamp=datetime.now(),
                    bbox=track_info["bbox"]
                )
                
                if sighting_id is not None:
                    total_inserted += 1
            
            # Display progress every 30 frames
            if frame_count % 30 == 0:
                print(f"   Frame {frame_count}: {len(state.tracks)} tracks, {total_inserted} sightings saved")
            
            # Check for quit (only if displaying)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            
            # Limit for demo
            if frame_count >= 100:
                break
    
    finally:
        cap.release()
    
    print(f"\n📊 Video Processing Complete:")
    print(f"   Frames processed: {frame_count}")
    print(f"   Sightings saved: {total_inserted}")
    
    # Show statistics
    stats = db.get_statistics()
    print(f"\n📈 Database Statistics:")
    print(f"   Total sightings: {stats['total_sightings']}")
    print(f"   Unique tracks: {stats['unique_tracks']}")
    
    db.close()
    print()


def example_4_query_operations():
    """
    Example 4: Advanced query operations.
    """
    print("=" * 70)
    print("Example 4: Advanced Query Operations")
    print("=" * 70)
    
    # Initialize database with some test data
    db = WildlifeDatabase("wildlife_query_test.db")
    
    # Insert test data
    print("\n📝 Inserting test data...")
    test_data = [
        ("Red Fox", 0.85, 1, 100),
        ("Red Fox", 0.82, 1, 101),
        ("Grey Fox", 0.78, 2, 100),
        ("Deer", 0.92, 3, 100),
        ("Deer", 0.90, 3, 101),
        ("Deer", 0.88, 3, 102),
    ]
    
    for species, conf, track_id, frame_num in test_data:
        db.insert_sighting(
            species=species,
            confidence=conf,
            track_id=track_id,
            frame_number=frame_num,
            timestamp=datetime.now()
        )
    
    print(f"   ✅ Inserted {len(test_data)} test sightings")
    
    # Query by species
    print("\n🔍 Query: All 'Deer' sightings")
    deer_sightings = db.get_sightings_by_species("Deer")
    print(f"   Found {len(deer_sightings)} sighting(s):")
    for s in deer_sightings:
        print(f"   - Track {s['track_id']}, Frame {s['frame_number']}: {s['confidence']:.2f}")
    
    # Query by track
    print("\n🔍 Query: All sightings for Track 1")
    track_sightings = db.get_sightings_by_track(1)
    print(f"   Found {len(track_sightings)} sighting(s):")
    for s in track_sightings:
        print(f"   - Frame {s['frame_number']}: {s['species']} ({s['confidence']:.2f})")
    
    # Species count
    print("\n📊 Species Count:")
    species_counts = db.get_species_count()
    for species, count in species_counts.items():
        print(f"   {species}: {count}")
    
    # Check duplicate
    print("\n🔍 Check duplicate:")
    is_dup = db.check_duplicate(track_id=1, frame_number=100)
    print(f"   Track 1, Frame 100 exists: {is_dup}")
    
    is_dup = db.check_duplicate(track_id=1, frame_number=999)
    print(f"   Track 1, Frame 999 exists: {is_dup}")
    
    # Statistics
    print("\n📈 Statistics:")
    stats = db.get_statistics()
    print(f"   Total sightings: {stats['total_sightings']}")
    print(f"   Unique tracks: {stats['unique_tracks']}")
    print(f"   Unique species: {stats['unique_species']}")
    
    db.close()
    print()


def example_5_context_manager():
    """
    Example 5: Using database with context manager.
    """
    print("=" * 70)
    print("Example 5: Context Manager Usage")
    print("=" * 70)
    
    print("\n📦 Using 'with' statement for automatic cleanup...")
    
    with WildlifeDatabase("wildlife_context.db") as db:
        # Insert sighting
        sighting_id = db.insert_sighting(
            species="Brown Bear",
            confidence=0.95,
            track_id=1,
            frame_number=1,
            timestamp=datetime.now()
        )
        
        print(f"   ✅ Inserted sighting: {sighting_id}")
        
        # Query
        stats = db.get_statistics()
        print(f"   Total sightings: {stats['total_sightings']}")
    
    print("   ✅ Database automatically closed")
    print()


def _bboxes_similar(bbox1, bbox2, threshold=0.5):
    """Check if two bounding boxes are similar (simple IoU)."""
    x1_min, y1_min, x1_max, y1_max = bbox1
    x2_min, y2_min, x2_max, y2_max = bbox2
    
    # Intersection
    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)
    
    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return False
    
    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    
    # Union
    bbox1_area = (x1_max - x1_min) * (y1_max - y1_min)
    bbox2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = bbox1_area + bbox2_area - inter_area
    
    iou = inter_area / union_area if union_area > 0 else 0.0
    return iou > threshold


def main():
    """Run all examples."""
    print("\n🦌 Wildlife Database Examples\n")
    
    # Run examples
    example_1_basic_database_operations()
    example_2_pipeline_integration()
    example_4_query_operations()
    example_5_context_manager()
    
    # Uncomment to run video example
    # example_3_video_with_database()
    
    print("=" * 70)
    print("Examples complete!")
    print("=" * 70)
    print("\n✅ Database Features:")
    print("   ✓ Automatic table creation")
    print("   ✓ Duplicate prevention (UNIQUE constraint)")
    print("   ✓ Thread-safe operations")
    print("   ✓ Query utilities")
    print("   ✓ Context manager support")
    print()


if __name__ == "__main__":
    main()
