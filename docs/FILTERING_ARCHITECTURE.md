# Animal Filtering Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Wildlife Monitoring Pipeline                  │
│                         (with Filtering)                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ Input Frame  │
│  (Webcam/    │
│   Video)     │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                      YOLO Detection                               │
│  • Detects ALL objects in frame                                  │
│  • Returns: cars, people, animals, furniture, etc.               │
│  • Example: 100 objects detected                                 │
└──────┬───────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    🔍 Animal Filtering                            │
│  • Check each detection against allowed_classes                  │
│  • Keep only: dog, cat, horse, cow, elephant, bear, zebra, etc.  │
│  • Discard: car, person, chair, phone, etc.                      │
│  • Example: 100 objects → 8 animals                              │
└──────┬───────────────────────────────────────────────────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
   ┌────────┐      ┌──────────┐
   │Animals │      │No Animals│
   │ Found  │      │  Found   │
   └───┬────┘      └────┬─────┘
       │                │
       │                ▼
       │           ┌──────────────────┐
       │           │ "No wildlife     │
       │           │  detected"       │
       │           │ • Return empty   │
       │           │ • Skip tracking  │
       │           └──────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Species Classification                         │
│  • Only process filtered animals (8 instead of 100)              │
│  • Crop bounding boxes                                           │
│  • Run ResNet50/EfficientNet                                     │
│  • Return species labels + confidence                            │
└──────┬───────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Object Tracking                                │
│  • Track only animals across frames                              │
│  • Assign persistent IDs                                         │
│  • Update track history                                          │
└──────┬───────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Pipeline Result                                │
│  • detections: List of animals only                              │
│  • classifications: Species labels                               │
│  • tracks: Track IDs and metadata                                │
│  • annotated_frame: Visualized output                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## Filtering Logic Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    _filter_detections()                          │
└─────────────────────────────────────────────────────────────────┘

Input: detections = [
    {"class_name": "dog", "confidence": 0.8, "bbox": [...]},
    {"class_name": "car", "confidence": 0.7, "bbox": [...]},
    {"class_name": "cat", "confidence": 0.6, "bbox": [...]},
    {"class_name": "person", "confidence": 0.5, "bbox": [...]}
]

allowed_classes = {"dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"}

┌─────────────────────────────────────────────────────────────────┐
│  For each detection:                                             │
│    1. Get class_name (lowercase)                                 │
│    2. Check if class_name in allowed_classes                     │
│    3. If YES → Keep detection                                    │
│    4. If NO  → Discard detection                                 │
└─────────────────────────────────────────────────────────────────┘

Output: filtered_detections = [
    {"class_name": "dog", "confidence": 0.8, "bbox": [...]},
    {"class_name": "cat", "confidence": 0.6, "bbox": [...]}
]

Result: 4 detections → 2 animals (50% reduction)
```

---

## Configuration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PipelineConfig                                │
└─────────────────────────────────────────────────────────────────┘

config = PipelineConfig(
    yolo_model_path="yolov8n.pt",
    detection_confidence=0.5,
    allowed_animal_classes={"dog", "cat", ...},  ← Define allowed classes
    filter_non_animals=True                      ← Enable filtering
)
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WildlifePipeline.__init__()                   │
└─────────────────────────────────────────────────────────────────┘

self.detector = YOLODetector(
    model_path=config.yolo_model_path,
    allowed_classes=config.allowed_animal_classes  ← Pass to detector
)
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    YOLODetector.__init__()                       │
└─────────────────────────────────────────────────────────────────┘

self.allowed_classes = allowed_classes  ← Store for filtering
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    process_frame()                               │
└─────────────────────────────────────────────────────────────────┘

detections = self.detector.detect(
    frame,
    filter_animals=self.config.filter_non_animals  ← Use config flag
)
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    YOLODetector.detect()                         │
└─────────────────────────────────────────────────────────────────┘

if filter_animals and self.allowed_classes is not None:
    detections = self._filter_detections(detections)  ← Apply filter
```

---

## Performance Comparison

### Without Filtering

```
┌──────────────┐
│ Frame Input  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ YOLO Detection   │  ← 100 objects detected
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Classification   │  ← Process ALL 100 objects
│ (SLOW)           │     • 100 crops
│                  │     • 100 ResNet50 inferences
│                  │     • High memory usage
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Tracking         │  ← Track ALL 100 objects
└──────┬───────────┘
       │
       ▼
Result: SLOW, HIGH MEMORY, NOISY DATA
```

### With Filtering

```
┌──────────────┐
│ Frame Input  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ YOLO Detection   │  ← 100 objects detected
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Animal Filter    │  ← Filter to 8 animals
│ (FAST)           │     • Simple string matching
│                  │     • Minimal overhead
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Classification   │  ← Process ONLY 8 animals
│ (FAST)           │     • 8 crops
│                  │     • 8 ResNet50 inferences
│                  │     • Low memory usage
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Tracking         │  ← Track ONLY 8 animals
└──────┬───────────┘
       │
       ▼
Result: FAST, LOW MEMORY, CLEAN DATA
```

**Performance Gain**: ~92% reduction in classification workload (8 vs 100 objects)

---

## Class Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOLODetector                                  │
├─────────────────────────────────────────────────────────────────┤
│ Attributes:                                                      │
│  • model: YOLO                                                   │
│  • confidence_threshold: float                                   │
│  • iou_threshold: float                                          │
│  • allowed_classes: Optional[Set[str]]  ← NEW                    │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                         │
│  • __init__(model_path, confidence, iou, allowed_classes)        │
│  • detect(frame, filter_animals) → List[Detection]              │
│  • detect_batch(frames, filter_animals) → List[List[Detection]] │
│  • _filter_detections(detections) → List[Detection]  ← NEW       │
│  • set_allowed_classes(classes)  ← NEW                           │
│  • get_detection_summary(detections) → Dict  ← NEW               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WildlifePipeline                              │
├─────────────────────────────────────────────────────────────────┤
│ Attributes:                                                      │
│  • config: PipelineConfig                                        │
│  • detector: YOLODetector  ← Configured with allowed_classes     │
│  • classifier: SpeciesClassifier                                 │
│  • tracker: CentroidTracker                                      │
├─────────────────────────────────────────────────────────────────┤
│ Methods:                                                         │
│  • process_frame(frame, annotate) → PipelineResult               │
│  • _classify_detections(frame, detections) → Dict                │
│  • _annotate_frame(...) → np.ndarray                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ configured by
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PipelineConfig                                │
├─────────────────────────────────────────────────────────────────┤
│ Attributes:                                                      │
│  • yolo_model_path: str                                          │
│  • detection_confidence: float                                   │
│  • classification_enabled: bool                                  │
│  • allowed_animal_classes: Optional[Set[str]]  ← NEW             │
│  • filter_non_animals: bool  ← NEW                               │
│  • ... (other config parameters)                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Detection Data Structure                      │
└─────────────────────────────────────────────────────────────────┘

detection = {
    "bbox": [x1, y1, x2, y2],      # Bounding box coordinates
    "confidence": 0.85,             # Detection confidence
    "class_id": 16,                 # YOLO class ID
    "class_name": "dog"             # Human-readable class name ← Used for filtering
}

┌─────────────────────────────────────────────────────────────────┐
│                    Filtering Decision                            │
└─────────────────────────────────────────────────────────────────┘

if detection["class_name"].lower() in allowed_classes:
    ✅ KEEP → Pass to classification
else:
    ❌ DISCARD → Skip classification

┌─────────────────────────────────────────────────────────────────┐
│                    Pipeline Result                               │
└─────────────────────────────────────────────────────────────────┘

result = PipelineResult(
    frame_number=42,
    detections=[...],              # Only filtered animals
    classifications={...},         # Only for filtered animals
    tracks={...},                  # Only for filtered animals
    annotated_frame=np.ndarray     # Visualized output
)
```

---

## Summary

**Key Points**:
1. Filtering happens **after YOLO detection** but **before classification**
2. Only **allowed animal classes** are kept
3. **Non-animals are discarded** early in the pipeline
4. **Classification only processes filtered animals** (performance boost)
5. **"No wildlife detected"** when no animals match allowed classes
6. **Modular design** allows easy enable/disable

**Benefits**:
- ⚡ **92% faster** classification (8 vs 100 objects)
- 🎯 **More accurate** results (focus on animals)
- 💾 **Less memory** usage (fewer objects tracked)
- 📊 **Cleaner data** (only relevant detections)
