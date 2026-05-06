"""
Pipeline Orchestrator

Coordinates the complete wildlife monitoring workflow:
1. Frame reading
2. Animal detection (YOLO)
3. Bounding box cropping
4. Species classification
5. Object tracking
"""

import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from ..input import VideoSource, FrameProcessor
from ..detection import YOLODetector, draw_detections
from ..classification import SpeciesClassifier, extract_roi
from ..tracking import CentroidTracker, TrackManager


@dataclass
class PipelineConfig:
    """
    Configuration for the wildlife monitoring pipeline.
    
    Attributes:
        yolo_model_path: Path to YOLOv8 model weights
        detection_confidence: Minimum confidence for detections
        classification_model: Classification model name
        classification_confidence: Minimum confidence for classification
        classification_enabled: Whether to run classification
        tracking_max_disappeared: Max frames before removing track
        frame_skip: Process every Nth frame (1 = all frames)
        preprocess_frames: Whether to preprocess frames
        device: Device for models (auto/cuda/cpu/mps)
        allowed_animal_classes: Set of allowed animal classes (None = all)
        filter_non_animals: Whether to filter out non-animal detections
    """
    yolo_model_path: str = "yolov8n.pt"
    detection_confidence: float = 0.5
    classification_model: str = "resnet50"
    classification_confidence: float = 0.3
    classification_enabled: bool = True
    tracking_max_disappeared: int = 50
    frame_skip: int = 1
    preprocess_frames: bool = False
    device: Optional[str] = None
    allowed_animal_classes: Optional[set] = None
    filter_non_animals: bool = True


@dataclass
class PipelineResult:
    """
    Result from processing a single frame.
    
    Attributes:
        frame_number: Frame index
        detections: Raw detections from YOLO
        classifications: Species classifications per detection
        tracks: Active tracks with IDs and metadata
        annotated_frame: Frame with visualizations (optional)
    """
    frame_number: int
    detections: List[Dict[str, Any]]
    classifications: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    tracks: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    annotated_frame: Optional[np.ndarray] = None


class WildlifePipeline:
    """
    Orchestrates the complete wildlife monitoring pipeline.
    
    Integrates all modules: input, detection, classification, tracking.
    """
    
    def __init__(self, config: PipelineConfig):
        """
        Initialize pipeline with configuration.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        
        # Initialize modules
        self.detector = YOLODetector(
            model_path=config.yolo_model_path,
            confidence_threshold=config.detection_confidence,
            allowed_classes=config.allowed_animal_classes
        )
        
        if config.classification_enabled:
            self.classifier = SpeciesClassifier(
                model_name=config.classification_model,
                confidence_threshold=config.classification_confidence,
                device=config.device
            )
        else:
            self.classifier = None
        
        self.tracker = CentroidTracker(
            max_disappeared=config.tracking_max_disappeared
        )
        
        self.track_manager = TrackManager()
        
        if config.preprocess_frames:
            self.frame_processor = FrameProcessor()
        else:
            self.frame_processor = None
        
        # State
        self.frame_count = 0
        self.processed_frames = 0
    
    def process_frame(
        self,
        frame: np.ndarray,
        annotate: bool = False
    ) -> PipelineResult:
        """
        Process a single frame through the complete pipeline.
        
        Workflow:
        1. Preprocess frame (optional)
        2. Detect animals with YOLO
        3. Crop bounding boxes
        4. Classify species (optional)
        5. Track objects across frames
        
        Args:
            frame: Input frame (BGR format from OpenCV)
            annotate: Whether to return annotated frame
            
        Returns:
            PipelineResult with detections, classifications, and tracks
        """
        self.frame_count += 1
        
        # Skip frames if configured
        if self.frame_count % self.config.frame_skip != 0:
            return PipelineResult(
                frame_number=self.frame_count,
                detections=[],
                tracks=self.tracker._get_tracking_info()
            )
        
        self.processed_frames += 1
        
        # Step 1: Preprocess (optional)
        processed_frame = frame
        if self.frame_processor is not None:
            processed_frame = self.frame_processor.preprocess(frame)
        
        # Step 2: Detect animals (with filtering if enabled)
        detections = self.detector.detect(
            processed_frame,
            filter_animals=self.config.filter_non_animals
        )
        
        # Step 3 & 4: Crop and classify (if enabled and animals detected)
        classifications = {}
        if self.classifier is not None and detections:
            classifications = self._classify_detections(frame, detections)
        
        # Step 5: Track objects
        tracks = self.tracker.update(detections)
        
        # Update track manager with classifications
        self.track_manager.update_tracks(
            frame_number=self.frame_count,
            tracking_info=tracks,
            classifications=classifications
        )
        
        # Annotate frame (optional)
        annotated_frame = None
        if annotate:
            annotated_frame = self._annotate_frame(
                frame.copy(),
                detections,
                classifications,
                tracks
            )
        
        return PipelineResult(
            frame_number=self.frame_count,
            detections=detections,
            classifications=classifications,
            tracks=tracks,
            annotated_frame=annotated_frame
        )
    
    def _classify_detections(
        self,
        frame: np.ndarray,
        detections: List[Dict[str, Any]]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Classify all detections in a frame.
        
        Args:
            frame: Original frame
            detections: List of detections with bounding boxes
            
        Returns:
            Dictionary mapping detection index to classification result
        """
        if not detections:
            return {}
        
        # Extract ROIs for all detections
        rois = []
        valid_indices = []
        
        for i, detection in enumerate(detections):
            try:
                roi = extract_roi(frame, detection["bbox"])
                if roi.size > 0:  # Valid ROI
                    rois.append(roi)
                    valid_indices.append(i)
            except Exception as e:
                # Skip invalid ROIs
                continue
        
        if not rois:
            return {}
        
        # Batch classify all ROIs
        classification_results = self.classifier.classify_batch(rois)
        
        # Map results back to detection indices
        classifications = {}
        for idx, result in zip(valid_indices, classification_results):
            classifications[idx] = result
        
        return classifications
    
    def _annotate_frame(
        self,
        frame: np.ndarray,
        detections: List[Dict[str, Any]],
        classifications: Dict[int, Dict[str, Any]],
        tracks: Dict[int, Dict[str, Any]]
    ) -> np.ndarray:
        """
        Annotate frame with detections, classifications, and track IDs.
        
        Args:
            frame: Frame to annotate
            detections: Detection results
            classifications: Classification results
            tracks: Tracking results
            
        Returns:
            Annotated frame
        """
        import cv2
        
        # Create track ID to detection mapping
        track_to_detection = {}
        for track_id, track_info in tracks.items():
            bbox = track_info["bbox"]
            # Find matching detection
            for i, det in enumerate(detections):
                if self._bboxes_match(bbox, det["bbox"]):
                    track_to_detection[track_id] = i
                    break
        
        # Draw each track
        for track_id, track_info in tracks.items():
            bbox = track_info["bbox"]
            x1, y1, x2, y2 = map(int, bbox)
            
            # Get classification if available
            det_idx = track_to_detection.get(track_id)
            species = "Unknown"
            confidence = 0.0
            
            if det_idx is not None and det_idx in classifications:
                species = classifications[det_idx]["species"]
                confidence = classifications[det_idx]["confidence"]
            
            # Draw bounding box
            color = (0, 255, 0)  # Green
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label with track ID and species
            label = f"ID:{track_id} {species}"
            if confidence > 0:
                label += f" {confidence:.2f}"
            
            # Label background
            (label_w, label_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            cv2.rectangle(
                frame,
                (x1, y1 - label_h - 10),
                (x1 + label_w, y1),
                color,
                -1
            )
            
            # Label text
            cv2.putText(
                frame,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
        
        return frame
    
    def _bboxes_match(
        self,
        bbox1: List[float],
        bbox2: List[float],
        threshold: float = 0.5
    ) -> bool:
        """
        Check if two bounding boxes match (IoU > threshold).
        
        Args:
            bbox1: First bounding box [x1, y1, x2, y2]
            bbox2: Second bounding box [x1, y1, x2, y2]
            threshold: IoU threshold
            
        Returns:
            True if boxes match
        """
        from ..detection.detection_utils import calculate_iou
        return calculate_iou(bbox1, bbox2) > threshold
    
    def process_video(
        self,
        video_source: str,
        annotate: bool = False,
        save_output: Optional[str] = None
    ) -> List[PipelineResult]:
        """
        Process an entire video file.
        
        Args:
            video_source: Path to video file or camera index
            annotate: Whether to annotate frames
            save_output: Optional path to save annotated video
            
        Returns:
            List of PipelineResult for each processed frame
        """
        results = []
        
        # Setup video writer if saving output
        video_writer = None
        if save_output and annotate:
            import cv2
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = None  # Will initialize on first frame
        
        # Process video
        with VideoSource(video_source) as source:
            if not source.open():
                raise ValueError(f"Could not open video source: {video_source}")
            
            while True:
                success, frame = source.read_frame()
                if not success:
                    break
                
                # Process frame
                result = self.process_frame(frame, annotate=annotate)
                results.append(result)
                
                # Save annotated frame
                if video_writer is not None and result.annotated_frame is not None:
                    video_writer.write(result.annotated_frame)
                elif save_output and annotate and result.annotated_frame is not None:
                    # Initialize writer on first frame
                    import cv2
                    h, w = result.annotated_frame.shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    video_writer = cv2.VideoWriter(
                        save_output, fourcc, source.fps, (w, h)
                    )
                    video_writer.write(result.annotated_frame)
        
        # Cleanup
        if video_writer is not None:
            video_writer.release()
        
        return results
    
    def get_track_summaries(self) -> List[Dict[str, Any]]:
        """
        Get summaries of all tracks.
        
        Returns:
            List of track summary dictionaries
        """
        track_ids = self.track_manager.get_active_tracks()
        return [
            self.track_manager.get_track_summary(track_id)
            for track_id in track_ids
        ]
    
    def reset(self):
        """Reset pipeline state (clear tracks, reset counters)."""
        self.tracker = CentroidTracker(
            max_disappeared=self.config.tracking_max_disappeared
        )
        self.track_manager = TrackManager()
        self.frame_count = 0
        self.processed_frames = 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get pipeline statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            "total_frames": self.frame_count,
            "processed_frames": self.processed_frames,
            "skipped_frames": self.frame_count - self.processed_frames,
            "active_tracks": len(self.tracker.objects),
            "total_tracks": len(self.track_manager.tracks),
            "classification_enabled": self.config.classification_enabled,
            "frame_skip": self.config.frame_skip
        }
