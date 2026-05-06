"""
Modular Pipeline

Clean, modular wildlife monitoring pipeline with separate stages:
Frame → Detection → Filter → Crop → Classification → Tracking

Each stage is a separate function with clear data flow.
"""

import numpy as np
import cv2
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from ..detection import YOLODetector
from ..classification import SpeciesClassifier
from ..tracking import CentroidTracker


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class StageResult:
    """
    Result from a single pipeline stage.
    
    Attributes:
        success: Whether the stage completed successfully
        data: Stage output data
        message: Optional message (e.g., "No animals detected")
    """
    success: bool
    data: Any
    message: str = ""


@dataclass
class PipelineState:
    """
    Complete pipeline state for a single frame.
    
    Tracks data flow through all stages:
    Frame → Detection → Filter → Crop → Classification → Tracking
    """
    frame_number: int
    original_frame: np.ndarray
    
    # Stage 1: Detection
    raw_detections: List[Dict[str, Any]] = field(default_factory=list)
    
    # Stage 2: Filter
    filtered_detections: List[Dict[str, Any]] = field(default_factory=list)
    
    # Stage 3: Crop
    cropped_images: List[np.ndarray] = field(default_factory=list)
    crop_indices: List[int] = field(default_factory=list)  # Maps crops to detections
    
    # Stage 4: Classification
    classifications: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    
    # Stage 5: Tracking
    tracks: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    
    # Final output
    annotated_frame: Optional[np.ndarray] = None


# ============================================================================
# STAGE 1: DETECTION
# ============================================================================

def stage_detection(
    frame: np.ndarray,
    detector: YOLODetector,
    apply_filter: bool = False
) -> StageResult:
    """
    Stage 1: Detect objects in frame using YOLO.
    
    This stage runs YOLO detection on the input frame to identify all objects.
    Optionally applies animal class filtering if enabled.
    
    Args:
        frame: Input frame (BGR format from OpenCV)
        detector: YOLODetector instance
        apply_filter: Whether to apply animal class filtering
        
    Returns:
        StageResult with:
            - success: True if detection ran (even if no objects found)
            - data: List of detections [{"bbox": [...], "confidence": ..., "class_name": ...}]
            - message: Status message
    """
    try:
        # Run YOLO detection
        detections = detector.detect(frame, filter_animals=apply_filter)
        
        # Prepare result message
        if not detections:
            message = "No objects detected"
        else:
            message = f"Detected {len(detections)} object(s)"
        
        return StageResult(
            success=True,
            data=detections,
            message=message
        )
    
    except Exception as e:
        return StageResult(
            success=False,
            data=[],
            message=f"Detection failed: {e}"
        )


# ============================================================================
# STAGE 2: FILTER
# ============================================================================

def stage_filter(
    detections: List[Dict[str, Any]],
    allowed_classes: Optional[set] = None
) -> StageResult:
    """
    Stage 2: Filter detections to keep only allowed animal classes.
    
    This stage filters the raw detections to keep only animals in the
    allowed classes list. Non-animal objects are discarded.
    
    Args:
        detections: Raw detections from YOLO
        allowed_classes: Set of allowed class names (None = keep all)
        
    Returns:
        StageResult with:
            - success: True if filtering completed
            - data: Filtered list of detections
            - message: "No wildlife detected" if empty, else count
    """
    # If no allowed classes specified, keep all detections
    if allowed_classes is None:
        return StageResult(
            success=True,
            data=detections,
            message=f"Kept all {len(detections)} detection(s)"
        )
    
    # Filter detections by allowed classes
    filtered = []
    for detection in detections:
        class_name = detection["class_name"].lower()
        if class_name in allowed_classes:
            filtered.append(detection)
    
    # Prepare result message
    if not filtered:
        message = "No wildlife detected"
    else:
        message = f"Filtered to {len(filtered)} animal(s) from {len(detections)} detection(s)"
    
    return StageResult(
        success=True,
        data=filtered,
        message=message
    )


# ============================================================================
# STAGE 3: CROP
# ============================================================================

def stage_crop(
    frame: np.ndarray,
    detections: List[Dict[str, Any]],
    classifier: Optional[SpeciesClassifier] = None
) -> StageResult:
    """
    Stage 3: Crop bounding boxes from frame for classification.
    
    This stage extracts the region of interest (ROI) for each detection
    by cropping the bounding box from the original frame. Only valid
    crops are kept.
    
    Args:
        frame: Original frame (BGR format)
        detections: Filtered detections with bounding boxes
        classifier: SpeciesClassifier instance (for crop_bbox method)
        
    Returns:
        StageResult with:
            - success: True if cropping completed
            - data: Tuple of (cropped_images, valid_indices)
            - message: Status message
    """
    if not detections:
        return StageResult(
            success=True,
            data=([], []),
            message="No detections to crop"
        )
    
    cropped_images = []
    valid_indices = []
    
    for i, detection in enumerate(detections):
        try:
            bbox = detection["bbox"]
            
            # Crop bounding box
            if classifier is not None:
                # Use classifier's crop method (with validation)
                cropped = classifier.crop_bbox(frame, bbox)
            else:
                # Manual crop (fallback)
                x1, y1, x2, y2 = map(int, bbox)
                h, w = frame.shape[:2]
                x1 = max(0, min(x1, w))
                y1 = max(0, min(y1, h))
                x2 = max(0, min(x2, w))
                y2 = max(0, min(y2, h))
                
                if x2 > x1 and y2 > y1:
                    cropped = frame[y1:y2, x1:x2].copy()
                else:
                    continue  # Skip invalid bbox
            
            # Validate crop
            if cropped.size > 0:
                cropped_images.append(cropped)
                valid_indices.append(i)
        
        except Exception as e:
            # Skip invalid crops
            continue
    
    # Prepare result message
    if not cropped_images:
        message = "No valid crops extracted"
    else:
        message = f"Cropped {len(cropped_images)} bounding box(es)"
    
    return StageResult(
        success=True,
        data=(cropped_images, valid_indices),
        message=message
    )


# ============================================================================
# STAGE 4: CLASSIFICATION
# ============================================================================

def stage_classification(
    cropped_images: List[np.ndarray],
    crop_indices: List[int],
    classifier: Optional[SpeciesClassifier] = None
) -> StageResult:
    """
    Stage 4: Classify cropped animal images to identify species.
    
    This stage runs species classification on each cropped image using
    ResNet50. Returns top-K predictions with confidence scores.
    
    Args:
        cropped_images: List of cropped bounding box images
        crop_indices: Indices mapping crops to original detections
        classifier: SpeciesClassifier instance
        
    Returns:
        StageResult with:
            - success: True if classification completed
            - data: Dict mapping detection index to classification result
            - message: Status message
    """
    if not cropped_images:
        return StageResult(
            success=True,
            data={},
            message="No images to classify"
        )
    
    if classifier is None:
        return StageResult(
            success=True,
            data={},
            message="Classification disabled"
        )
    
    try:
        # Batch classify all cropped images
        classification_results = classifier.classify_batch(
            cropped_images,
            return_top_k=True
        )
        
        # Map results back to detection indices
        classifications = {}
        for crop_idx, result in zip(crop_indices, classification_results):
            classifications[crop_idx] = result
        
        # Count unknown species
        unknown_count = sum(1 for r in classification_results if r.get("is_unknown", False))
        
        # Prepare result message
        message = f"Classified {len(classifications)} animal(s)"
        if unknown_count > 0:
            message += f" ({unknown_count} unknown)"
        
        return StageResult(
            success=True,
            data=classifications,
            message=message
        )
    
    except Exception as e:
        return StageResult(
            success=False,
            data={},
            message=f"Classification failed: {e}"
        )


# ============================================================================
# STAGE 5: TRACKING
# ============================================================================

def stage_tracking(
    detections: List[Dict[str, Any]],
    tracker: CentroidTracker
) -> StageResult:
    """
    Stage 5: Track detected animals across frames.
    
    This stage assigns persistent IDs to detected animals and tracks
    their movement across frames using centroid tracking.
    
    Args:
        detections: Filtered detections with bounding boxes
        tracker: CentroidTracker instance
        
    Returns:
        StageResult with:
            - success: True if tracking completed
            - data: Dict of tracks {track_id: {"bbox": ..., "centroid": ...}}
            - message: Status message
    """
    try:
        # Update tracker with current detections
        tracks = tracker.update(detections)
        
        # Prepare result message
        if not tracks:
            message = "No active tracks"
        else:
            message = f"Tracking {len(tracks)} object(s)"
        
        return StageResult(
            success=True,
            data=tracks,
            message=message
        )
    
    except Exception as e:
        return StageResult(
            success=False,
            data={},
            message=f"Tracking failed: {e}"
        )


# ============================================================================
# ANNOTATION
# ============================================================================

def annotate_frame(
    frame: np.ndarray,
    detections: List[Dict[str, Any]],
    classifications: Dict[int, Dict[str, Any]],
    tracks: Dict[int, Dict[str, Any]]
) -> np.ndarray:
    """
    Annotate frame with bounding boxes, species labels, and track IDs.
    
    Args:
        frame: Original frame to annotate
        detections: List of detections
        classifications: Classification results
        tracks: Tracking results
        
    Returns:
        Annotated frame
    """
    annotated = frame.copy()
    
    # Create mapping from track bbox to detection index
    def bbox_iou(bbox1, bbox2):
        """Calculate IoU between two bounding boxes."""
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
    
    # Map tracks to detections
    track_to_detection = {}
    for track_id, track_info in tracks.items():
        track_bbox = track_info["bbox"]
        best_iou = 0.0
        best_idx = None
        
        for i, det in enumerate(detections):
            iou = bbox_iou(track_bbox, det["bbox"])
            if iou > best_iou:
                best_iou = iou
                best_idx = i
        
        if best_iou > 0.5:  # Threshold
            track_to_detection[track_id] = best_idx
    
    # Draw annotations for each track
    for track_id, track_info in tracks.items():
        bbox = track_info["bbox"]
        x1, y1, x2, y2 = map(int, bbox)
        
        # Get classification if available
        det_idx = track_to_detection.get(track_id)
        species = "Unknown"
        confidence = 0.0
        is_unknown = False
        
        if det_idx is not None and det_idx in classifications:
            cls = classifications[det_idx]
            species = cls.get("species", "Unknown")
            confidence = cls.get("confidence", 0.0)
            is_unknown = cls.get("is_unknown", False)
        
        # Choose color based on classification
        if is_unknown:
            color = (0, 165, 255)  # Orange for unknown
        else:
            color = (0, 255, 0)  # Green for known species
        
        # Draw bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        # Prepare label
        label = f"ID:{track_id}"
        if species != "Unknown":
            label += f" {species}"
        if confidence > 0:
            label += f" {confidence:.2f}"
        
        # Draw label background
        (label_w, label_h), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        cv2.rectangle(
            annotated,
            (x1, y1 - label_h - 10),
            (x1 + label_w, y1),
            color,
            -1
        )
        
        # Draw label text
        cv2.putText(
            annotated,
            label,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
    
    return annotated


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def process_frame_modular(
    frame: np.ndarray,
    frame_number: int,
    detector: YOLODetector,
    classifier: Optional[SpeciesClassifier],
    tracker: CentroidTracker,
    allowed_classes: Optional[set] = None,
    apply_filter: bool = True,
    annotate: bool = False
) -> PipelineState:
    """
    Process a single frame through the modular pipeline.
    
    Pipeline Flow:
    1. Detection  → Detect objects with YOLO
    2. Filter     → Keep only allowed animal classes
    3. Crop       → Extract bounding box regions
    4. Classify   → Identify species with ResNet50
    5. Track      → Assign persistent IDs
    
    Args:
        frame: Input frame (BGR format)
        frame_number: Frame index
        detector: YOLODetector instance
        classifier: SpeciesClassifier instance (None = skip classification)
        tracker: CentroidTracker instance
        allowed_classes: Set of allowed animal classes (None = all)
        apply_filter: Whether to apply animal filtering
        annotate: Whether to annotate the frame
        
    Returns:
        PipelineState with results from all stages
    """
    # Initialize pipeline state
    state = PipelineState(
        frame_number=frame_number,
        original_frame=frame
    )
    
    # ========================================================================
    # STAGE 1: DETECTION
    # ========================================================================
    detection_result = stage_detection(frame, detector, apply_filter)
    state.raw_detections = detection_result.data
    
    # Early exit if no detections
    if not state.raw_detections:
        # Still run tracking to update disappeared objects
        tracking_result = stage_tracking([], tracker)
        state.tracks = tracking_result.data
        
        if annotate:
            state.annotated_frame = frame.copy()
        
        return state
    
    # ========================================================================
    # STAGE 2: FILTER
    # ========================================================================
    filter_result = stage_filter(state.raw_detections, allowed_classes)
    state.filtered_detections = filter_result.data
    
    # Early exit if no animals detected
    if not state.filtered_detections:
        # Still run tracking to update disappeared objects
        tracking_result = stage_tracking([], tracker)
        state.tracks = tracking_result.data
        
        if annotate:
            # Annotate with "No wildlife detected" message
            annotated = frame.copy()
            cv2.putText(
                annotated,
                "No wildlife detected",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2
            )
            state.annotated_frame = annotated
        
        return state
    
    # ========================================================================
    # STAGE 3: CROP
    # ========================================================================
    crop_result = stage_crop(frame, state.filtered_detections, classifier)
    state.cropped_images, state.crop_indices = crop_result.data
    
    # ========================================================================
    # STAGE 4: CLASSIFICATION
    # ========================================================================
    if classifier is not None and state.cropped_images:
        classification_result = stage_classification(
            state.cropped_images,
            state.crop_indices,
            classifier
        )
        state.classifications = classification_result.data
    
    # ========================================================================
    # STAGE 5: TRACKING
    # ========================================================================
    tracking_result = stage_tracking(state.filtered_detections, tracker)
    state.tracks = tracking_result.data
    
    # ========================================================================
    # ANNOTATION (OPTIONAL)
    # ========================================================================
    if annotate:
        state.annotated_frame = annotate_frame(
            frame,
            state.filtered_detections,
            state.classifications,
            state.tracks
        )
    
    return state


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def create_modular_pipeline(
    yolo_model_path: str = "yolov8n.pt",
    detection_confidence: float = 0.5,
    classification_model: str = "resnet50",
    classification_confidence: float = 0.3,
    classification_enabled: bool = True,
    allowed_animal_classes: Optional[set] = None,
    tracking_max_disappeared: int = 50,
    device: Optional[str] = None
) -> Tuple[YOLODetector, Optional[SpeciesClassifier], CentroidTracker]:
    """
    Create pipeline components with configuration.
    
    Args:
        yolo_model_path: Path to YOLO model
        detection_confidence: Detection confidence threshold
        classification_model: Classification model name
        classification_confidence: Classification confidence threshold
        classification_enabled: Whether to enable classification
        allowed_animal_classes: Set of allowed animal classes
        tracking_max_disappeared: Max frames before removing track
        device: Device for models (cuda/cpu/mps)
        
    Returns:
        Tuple of (detector, classifier, tracker)
    """
    # Create detector
    detector = YOLODetector(
        model_path=yolo_model_path,
        confidence_threshold=detection_confidence,
        allowed_classes=allowed_animal_classes
    )
    
    # Create classifier (optional)
    classifier = None
    if classification_enabled:
        classifier = SpeciesClassifier(
            model_name=classification_model,
            confidence_threshold=classification_confidence,
            device=device,
            top_k=3
        )
    
    # Create tracker
    tracker = CentroidTracker(max_disappeared=tracking_max_disappeared)
    
    return detector, classifier, tracker
