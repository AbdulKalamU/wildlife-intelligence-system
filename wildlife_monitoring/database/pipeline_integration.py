"""
Pipeline Integration Module

Helper functions to integrate database with wildlife monitoring pipeline.
"""

from datetime import datetime
from typing import Dict, Any, List
from .wildlife_db import WildlifeDatabase


def save_pipeline_results_to_db(
    db: WildlifeDatabase,
    pipeline_state: Any,  # PipelineState from modular_pipeline
    timestamp: datetime = None
) -> int:
    """
    Save pipeline results to database.
    
    For each tracked animal:
    - Extracts species and confidence from classifications
    - Inserts sighting record
    - Prevents duplicates automatically
    
    Args:
        db: WildlifeDatabase instance
        pipeline_state: PipelineState from process_frame_modular
        timestamp: Timestamp for sightings (defaults to now)
        
    Returns:
        Number of sightings inserted
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    inserted_count = 0
    
    # Map tracks to detections (for classification lookup)
    track_to_detection = _map_tracks_to_detections(
        pipeline_state.tracks,
        pipeline_state.filtered_detections
    )
    
    # Insert sighting for each track
    for track_id, track_info in pipeline_state.tracks.items():
        # Get detection index
        det_idx = track_to_detection.get(track_id)
        
        # Get classification if available
        species = "Unknown"
        confidence = 0.0
        
        if det_idx is not None:
            # Get YOLO class name
            if det_idx < len(pipeline_state.filtered_detections):
                species = pipeline_state.filtered_detections[det_idx]["class_name"]
                confidence = pipeline_state.filtered_detections[det_idx]["confidence"]
            
            # Override with classification if available
            if det_idx in pipeline_state.classifications:
                cls = pipeline_state.classifications[det_idx]
                species = cls["species"]
                confidence = cls["confidence"]
        
        # Insert into database
        sighting_id = db.insert_sighting(
            species=species,
            confidence=confidence,
            track_id=track_id,
            frame_number=pipeline_state.frame_number,
            timestamp=timestamp,
            bbox=track_info["bbox"]
        )
        
        if sighting_id is not None:
            inserted_count += 1
    
    return inserted_count


def _map_tracks_to_detections(
    tracks: Dict[int, Dict[str, Any]],
    detections: List[Dict[str, Any]],
    iou_threshold: float = 0.5
) -> Dict[int, int]:
    """
    Map track IDs to detection indices using IoU.
    
    Args:
        tracks: Dictionary of tracks {track_id: track_info}
        detections: List of detections
        iou_threshold: Minimum IoU for matching
        
    Returns:
        Dictionary mapping track_id to detection index
    """
    mapping = {}
    
    for track_id, track_info in tracks.items():
        track_bbox = track_info["bbox"]
        best_iou = 0.0
        best_idx = None
        
        for i, det in enumerate(detections):
            iou = _calculate_iou(track_bbox, det["bbox"])
            if iou > best_iou:
                best_iou = iou
                best_idx = i
        
        if best_iou > iou_threshold:
            mapping[track_id] = best_idx
    
    return mapping


def _calculate_iou(bbox1: List[float], bbox2: List[float]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.
    
    Args:
        bbox1: First bounding box [x1, y1, x2, y2]
        bbox2: Second bounding box [x1, y1, x2, y2]
        
    Returns:
        IoU value (0.0 to 1.0)
    """
    x1_min, y1_min, x1_max, y1_max = bbox1
    x2_min, y2_min, x2_max, y2_max = bbox2
    
    # Intersection
    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)
    
    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return 0.0
    
    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    
    # Union
    bbox1_area = (x1_max - x1_min) * (y1_max - y1_min)
    bbox2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = bbox1_area + bbox2_area - inter_area
    
    return inter_area / union_area if union_area > 0 else 0.0


def get_track_history(
    db: WildlifeDatabase,
    track_id: int
) -> Dict[str, Any]:
    """
    Get complete history for a track.
    
    Args:
        db: WildlifeDatabase instance
        track_id: Track ID
        
    Returns:
        Dictionary with track history:
            - track_id: Track ID
            - total_frames: Number of frames tracked
            - species: Most common species
            - avg_confidence: Average confidence
            - first_seen: First timestamp
            - last_seen: Last timestamp
            - sightings: List of all sightings
    """
    sightings = db.get_sightings_by_track(track_id)
    
    if not sightings:
        return {
            "track_id": track_id,
            "total_frames": 0,
            "species": None,
            "avg_confidence": 0.0,
            "first_seen": None,
            "last_seen": None,
            "sightings": []
        }
    
    # Calculate statistics
    species_counts = {}
    total_confidence = 0.0
    
    for s in sightings:
        species = s["species"]
        species_counts[species] = species_counts.get(species, 0) + 1
        total_confidence += s["confidence"]
    
    # Most common species
    most_common_species = max(species_counts, key=species_counts.get)
    
    # Average confidence
    avg_confidence = total_confidence / len(sightings)
    
    return {
        "track_id": track_id,
        "total_frames": len(sightings),
        "species": most_common_species,
        "avg_confidence": avg_confidence,
        "first_seen": sightings[0]["timestamp"],
        "last_seen": sightings[-1]["timestamp"],
        "sightings": sightings
    }
