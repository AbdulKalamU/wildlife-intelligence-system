# Modular Pipeline Architecture

## Overview

The modular pipeline provides a clean, maintainable architecture with separate functions for each processing stage:

```
Frame → Detection → Filter → Crop → Classification → Tracking
```

Each stage is independent, testable, and has clear inputs/outputs.

---

## Architecture

### Pipeline Flow

```
┌─────────────────┐
│  Input Frame    │  ← BGR image from OpenCV
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  STAGE 1: DETECTION                                      │
│  • Run YOLO on frame                                     │
│  • Detect all objects                                    │
│  • Output: List of detections                           │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  STAGE 2: FILTER                                         │
│  • Filter by allowed animal classes                      │
│  • Discard non-animals                                   │
│  • Output: Filtered detections                          │
└────────┬─────────────────────────────────────────────────┘
         │
         ├─────────────► No animals? → Return empty result
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  STAGE 3: CROP                                           │
│  • Extract bounding box regions                          │
│  • Validate crops                                        │
│  • Output: Cropped images + indices                     │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  STAGE 4: CLASSIFICATION                                 │
│  • Classify each cropped image                           │
│  • Get top-K predictions                                 │
│  • Output: Species + confidence                          │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  STAGE 5: TRACKING                                       │
│  • Assign persistent IDs                                 │
│  • Track across frames                                   │
│  • Output: Tracks with IDs                               │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Pipeline State │  ← Complete results from all stages
└─────────────────┘
```

---

## Quick Start

```python
from wildlife_monitoring.pipeline.modular_pipeline import (
    process_frame_modular,
    create_modular_pipeline
)
import cv2

# Define allowed animals
ALLOWED_ANIMALS = {
    "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
}

# Create pipeline components
detector, classifier, tracker = create_modular_pipeline(
    yolo_model_path="yolov8n.pt",
    detection_confidence=0.5,
    classification_enabled=True,
    allowed_animal_classes=ALLOWED_ANIMALS
)

# Load frame
frame = cv2.imread("wildlife.jpg")

# Process frame
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

# Access results
print(f"Detections: {len(state.filtered_detections)}")
print(f"Classifications: {len(state.classifications)}")
print(f"Tracks: {len(state.tracks)}")

# Display annotated frame
cv2.imshow("Result", state.annotated_frame)
cv2.waitKey(0)
```

---

## Stage Details

### Stage 1: Detection

**Purpose**: Detect all objects in frame using YOLO

**Function**: `stage_detection(frame, detector, apply_filter)`

**Input**:
- `frame`: BGR image from OpenCV
- `detector`: YOLODetector instance
- `apply_filter`: Whether to apply animal filtering

**Output**: `StageResult`
```python
{
    "success": True,
    "data": [
        {
            "bbox": [x1, y1, x2, y2],
            "confidence": 0.85,
            "class_id": 16,
            "class_name": "dog"
        },
        ...
    ],
    "message": "Detected 5 object(s)"
}
```

**Handles**:
- ✅ No objects detected → Returns empty list
- ✅ Detection errors → Returns success=False

### Stage 2: Filter

**Purpose**: Keep only allowed animal classes

**Function**: `stage_filter(detections, allowed_classes)`

**Input**:
- `detections`: List of detections from Stage 1
- `allowed_classes`: Set of allowed class names

**Output**: `StageResult`
```python
{
    "success": True,
    "data": [
        # Only animals in allowed_classes
    ],
    "message": "Filtered to 3 animal(s) from 5 detection(s)"
}
```

**Handles**:
- ✅ No animals match → Returns "No wildlife detected"
- ✅ All animals match → Returns all detections
- ✅ None filter (allowed_classes=None) → Returns all

### Stage 3: Crop

**Purpose**: Extract bounding box regions for classification

**Function**: `stage_crop(frame, detections, classifier)`

**Input**:
- `frame`: Original frame
- `detections`: Filtered detections from Stage 2
- `classifier`: SpeciesClassifier (for crop_bbox method)

**Output**: `StageResult`
```python
{
    "success": True,
    "data": (
        [cropped_img1, cropped_img2, ...],  # Cropped images
        [0, 1, ...]                          # Detection indices
    ),
    "message": "Cropped 3 bounding box(es)"
}
```

**Handles**:
- ✅ Invalid bboxes → Skips and continues
- ✅ Out of bounds → Clips to frame bounds
- ✅ No detections → Returns empty lists

### Stage 4: Classification

**Purpose**: Identify species for each cropped image

**Function**: `stage_classification(cropped_images, crop_indices, classifier)`

**Input**:
- `cropped_images`: List of cropped images from Stage 3
- `crop_indices`: Indices mapping crops to detections
- `classifier`: SpeciesClassifier instance

**Output**: `StageResult`
```python
{
    "success": True,
    "data": {
        0: {
            "species": "Red Fox",
            "confidence": 0.85,
            "is_unknown": False,
            "top_predictions": [...]
        },
        ...
    },
    "message": "Classified 3 animal(s)"
}
```

**Handles**:
- ✅ No images → Returns empty dict
- ✅ Classifier disabled → Returns empty dict
- ✅ Classification errors → Returns success=False

### Stage 5: Tracking

**Purpose**: Assign persistent IDs and track across frames

**Function**: `stage_tracking(detections, tracker)`

**Input**:
- `detections`: Filtered detections from Stage 2
- `tracker`: CentroidTracker instance

**Output**: `StageResult`
```python
{
    "success": True,
    "data": {
        1: {
            "bbox": [x1, y1, x2, y2],
            "centroid": (cx, cy)
        },
        ...
    },
    "message": "Tracking 3 object(s)"
}
```

**Handles**:
- ✅ No detections → Updates disappeared objects
- ✅ New objects → Assigns new IDs
- ✅ Disappeared objects → Removes after threshold

---

## Data Structures

### StageResult

Result from a single pipeline stage:

```python
@dataclass
class StageResult:
    success: bool      # Whether stage completed successfully
    data: Any          # Stage output data
    message: str       # Status message
```

### PipelineState

Complete state tracking all stages:

```python
@dataclass
class PipelineState:
    frame_number: int
    original_frame: np.ndarray
    
    # Stage outputs
    raw_detections: List[Dict]           # Stage 1
    filtered_detections: List[Dict]      # Stage 2
    cropped_images: List[np.ndarray]     # Stage 3
    crop_indices: List[int]              # Stage 3
    classifications: Dict[int, Dict]     # Stage 4
    tracks: Dict[int, Dict]              # Stage 5
    
    # Final output
    annotated_frame: Optional[np.ndarray]
```

---

## Handling Edge Cases

### No Animals Detected

```python
state = process_frame_modular(...)

if not state.filtered_detections:
    print("No wildlife detected")
    # Pipeline still completes successfully
    # Tracking updates disappeared objects
    # Annotated frame shows "No wildlife detected" message
```

### Classification Disabled

```python
detector, classifier, tracker = create_modular_pipeline(
    classification_enabled=False  # Skip classification
)

state = process_frame_modular(
    ...,
    classifier=None  # Or pass None
)

# state.classifications will be empty
# Other stages work normally
```

### Invalid Bounding Boxes

```python
# Stage 3 (Crop) handles invalid bboxes gracefully
# - Validates coordinates
# - Clips to frame bounds
# - Skips invalid crops
# - Continues with valid crops
```

---

## Usage Patterns

### Pattern 1: Full Pipeline

```python
# Process frame through all stages
state = process_frame_modular(
    frame=frame,
    frame_number=frame_num,
    detector=detector,
    classifier=classifier,
    tracker=tracker,
    allowed_classes=ALLOWED_ANIMALS,
    apply_filter=True,
    annotate=True
)
```

### Pattern 2: Stage-by-Stage

```python
# Run each stage separately for debugging
detection_result = stage_detection(frame, detector)
filter_result = stage_filter(detection_result.data, ALLOWED_ANIMALS)
crop_result = stage_crop(frame, filter_result.data, classifier)
# ... etc
```

### Pattern 3: Video Processing

```python
cap = cv2.VideoCapture("video.mp4")
frame_num = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_num += 1
    state = process_frame_modular(
        frame, frame_num, detector, classifier, tracker,
        ALLOWED_ANIMALS, True, True
    )
    
    cv2.imshow("Wildlife", state.annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
```

### Pattern 4: Batch Processing

```python
frames = [...]  # List of frames

for i, frame in enumerate(frames):
    state = process_frame_modular(
        frame, i, detector, classifier, tracker,
        ALLOWED_ANIMALS, True, False
    )
    
    # Process results
    for det_idx, cls in state.classifications.items():
        print(f"Frame {i}: {cls['species']}")
```

---

## Benefits

### 1. Modularity

Each stage is a separate function:
- Easy to test individually
- Easy to replace/upgrade
- Clear responsibilities

### 2. Maintainability

Clean code structure:
- Well-commented
- Clear data flow
- Easy to understand

### 3. Debuggability

Can inspect each stage:
```python
# Debug specific stage
result = stage_detection(frame, detector)
print(f"Detections: {result.data}")
print(f"Message: {result.message}")
```

### 4. Extensibility

Easy to add new stages:
```python
def stage_new_feature(input_data, ...):
    # Process data
    return StageResult(success=True, data=output, message="...")
```

### 5. Error Handling

Each stage handles errors gracefully:
- Returns success flag
- Provides error messages
- Doesn't crash pipeline

---

## Comparison with Original Pipeline

### Original Pipeline

```python
# Monolithic process_frame method
result = pipeline.process_frame(frame, annotate=True)
# Hard to debug
# Hard to test individual stages
# Tightly coupled
```

### Modular Pipeline

```python
# Separate stages
state = process_frame_modular(
    frame, frame_num, detector, classifier, tracker,
    ALLOWED_ANIMALS, True, True
)
# Easy to debug each stage
# Easy to test individually
# Loosely coupled
```

---

## Testing

### Test Individual Stages

```python
def test_stage_detection():
    detector = YOLODetector()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    result = stage_detection(frame, detector)
    
    assert result.success == True
    assert isinstance(result.data, list)
```

### Test Full Pipeline

```python
def test_full_pipeline():
    detector, classifier, tracker = create_modular_pipeline()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    state = process_frame_modular(
        frame, 1, detector, classifier, tracker,
        {"dog", "cat"}, True, False
    )
    
    assert isinstance(state, PipelineState)
    assert state.frame_number == 1
```

---

## Performance

### Optimization Tips

1. **Disable classification for speed**:
   ```python
   create_modular_pipeline(classification_enabled=False)
   ```

2. **Use batch classification**:
   ```python
   # Already done in stage_classification
   classifier.classify_batch(cropped_images)
   ```

3. **Skip annotation if not needed**:
   ```python
   process_frame_modular(..., annotate=False)
   ```

4. **Use GPU if available**:
   ```python
   create_modular_pipeline(device="cuda")
   ```

---

## Summary

✅ **Modular design** - Separate function per stage  
✅ **Clean data flow** - Clear inputs/outputs  
✅ **Error handling** - Graceful failure handling  
✅ **Well-commented** - Easy to understand  
✅ **Testable** - Each stage can be tested independently  
✅ **Maintainable** - Easy to modify and extend  

**Result**: Clean, professional pipeline architecture! 🚀
