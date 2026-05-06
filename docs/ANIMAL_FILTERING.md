# Animal Class Filtering Guide

## Overview

The wildlife monitoring system now supports **animal class filtering** to ensure only relevant wildlife detections are passed to the classification module. This improves performance and accuracy by filtering out non-animal objects (e.g., cars, people, furniture) detected by YOLO.

## Features

✅ **Pre-classification filtering**: Filter detections before expensive classification  
✅ **Configurable allowed classes**: Define which animal classes to detect  
✅ **"No wildlife detected" handling**: Clear messaging when no animals found  
✅ **Modular design**: Enable/disable filtering as needed  
✅ **Performance optimization**: Skip classification for non-animal objects  

---

## Quick Start

### 1. Basic Usage with Detector

```python
from wildlife_monitoring.detection import YOLODetector

# Define allowed animal classes
ALLOWED_ANIMALS = {
    "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
}

# Initialize detector with filtering
detector = YOLODetector(
    model_path="yolov8n.pt",
    confidence_threshold=0.5,
    allowed_classes=ALLOWED_ANIMALS
)

# Detect animals in frame
detections = detector.detect(frame, filter_animals=True)

# Check results
if not detections:
    print("No wildlife detected")
else:
    print(f"Detected {len(detections)} animal(s)")
    for det in detections:
        print(f"  - {det['class_name']} ({det['confidence']:.2f})")
```

### 2. Using with Pipeline

```python
from wildlife_monitoring import WildlifePipeline, PipelineConfig

# Define allowed animals
ALLOWED_ANIMALS = {
    "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
}

# Configure pipeline with filtering
config = PipelineConfig(
    yolo_model_path="yolov8n.pt",
    detection_confidence=0.5,
    classification_enabled=True,
    allowed_animal_classes=ALLOWED_ANIMALS,
    filter_non_animals=True  # Enable filtering
)

# Initialize and use pipeline
pipeline = WildlifePipeline(config)
result = pipeline.process_frame(frame, annotate=True)

# Only animals in ALLOWED_ANIMALS will be in result.detections
# Only those animals will be passed to classification
```

### 3. Webcam with Filtering

```python
import cv2
from wildlife_monitoring import WildlifePipeline, PipelineConfig

ALLOWED_ANIMALS = {"dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"}

config = PipelineConfig(
    allowed_animal_classes=ALLOWED_ANIMALS,
    filter_non_animals=True
)

pipeline = WildlifePipeline(config)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    result = pipeline.process_frame(frame, annotate=True)
    
    if not result.detections:
        print("No wildlife detected")
    else:
        print(f"Detected: {[d['class_name'] for d in result.detections]}")
    
    cv2.imshow("Wildlife", result.annotated_frame or frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## Configuration Options

### PipelineConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `allowed_animal_classes` | `Set[str]` or `None` | `None` | Set of allowed animal class names. `None` = all classes allowed |
| `filter_non_animals` | `bool` | `True` | Whether to filter out non-animal detections |

### YOLODetector Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `allowed_classes` | `Set[str]` or `None` | `None` | Set of allowed class names. `None` = no filtering |

---

## Allowed Animal Classes

### Default Classes (from requirements)

```python
ALLOWED_ANIMALS = {
    "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"
}
```

### Extended Wildlife Classes

```python
from wildlife_monitoring.detection import DEFAULT_ANIMAL_CLASSES

# Includes: dog, cat, horse, cow, elephant, bear, zebra, giraffe,
#           bird, sheep, deer, fox, wolf, lion, tiger, monkey, etc.
```

### Custom Classes

```python
# Define your own allowed classes
CUSTOM_ANIMALS = {
    "dog", "cat", "bird", "horse"
}

detector = YOLODetector(allowed_classes=CUSTOM_ANIMALS)
```

---

## Workflow

```
┌─────────────────┐
│  Input Frame    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  YOLO Detection │  ← Detects ALL objects
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Filter Animals │  ← Keep only allowed classes
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │ Animals │ No animals?
    │ Found?  ├──────────► "No wildlife detected"
    └────┬────┘
         │ Yes
         ▼
┌─────────────────┐
│  Classification │  ← Only process filtered animals
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tracking       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Result         │
└─────────────────┘
```

---

## Benefits

### 1. **Performance**
- Skip classification for non-animal objects
- Reduce computational overhead
- Faster frame processing

### 2. **Accuracy**
- Focus classification on relevant objects
- Reduce false positives
- Better species identification

### 3. **Clarity**
- Clear "No wildlife detected" messaging
- Only relevant detections in results
- Cleaner tracking data

---

## Examples

### Example 1: Strict Wildlife Only

```python
# Only detect large wildlife
WILDLIFE_ONLY = {"elephant", "bear", "zebra", "giraffe"}

config = PipelineConfig(
    allowed_animal_classes=WILDLIFE_ONLY,
    filter_non_animals=True
)
```

### Example 2: Domestic + Wildlife

```python
# Detect both domestic and wild animals
ALL_ANIMALS = {
    "dog", "cat", "horse", "cow",  # Domestic
    "elephant", "bear", "zebra", "giraffe"  # Wildlife
}

config = PipelineConfig(
    allowed_animal_classes=ALL_ANIMALS,
    filter_non_animals=True
)
```

### Example 3: Disable Filtering

```python
# Detect everything (no filtering)
config = PipelineConfig(
    allowed_animal_classes=None,  # No filter
    filter_non_animals=False
)
```

### Example 4: Dynamic Filtering

```python
detector = YOLODetector(allowed_classes={"dog", "cat"})

# Detect with filtering
animals = detector.detect(frame, filter_animals=True)

# Detect without filtering (all objects)
all_objects = detector.detect(frame, filter_animals=False)

# Update allowed classes dynamically
detector.set_allowed_classes({"horse", "cow"})
```

---

## API Reference

### YOLODetector.detect()

```python
def detect(
    self,
    frame: np.ndarray,
    filter_animals: bool = True
) -> List[Dict[str, Any]]
```

**Parameters:**
- `frame`: Input frame (BGR format)
- `filter_animals`: Whether to apply animal class filtering

**Returns:**
- List of detections (only animals if filtering enabled)

### YOLODetector.get_detection_summary()

```python
def get_detection_summary(
    self,
    detections: List[Dict[str, Any]]
) -> Dict[str, Any]
```

**Returns:**
```python
{
    "total_detections": int,
    "message": str,  # "No wildlife detected" or "Detected N animal(s)"
    "classes": Dict[str, int]  # Class name -> count
}
```

---

## Testing

Run the example script to test filtering:

```bash
# Activate virtual environment
source venv/bin/activate

# Run filtering examples
python examples/test_animal_filtering.py
```

---

## Troubleshooting

### Issue: All detections filtered out

**Cause**: Allowed classes don't match YOLO class names

**Solution**: Check YOLO class names (lowercase, e.g., "dog" not "Dog")

```python
# Print YOLO class names
detector = YOLODetector()
print(detector.model.names)  # {0: 'person', 1: 'bicycle', ...}
```

### Issue: "No wildlife detected" but animals visible

**Cause**: Animals not in allowed classes list

**Solution**: Add missing classes to allowed list

```python
# Add more animal classes
ALLOWED_ANIMALS = {
    "dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe",
    "bird", "sheep"  # Add these
}
```

---

## Best Practices

1. **Use lowercase class names**: YOLO returns lowercase names
2. **Test with your data**: Verify which animals YOLO detects in your videos
3. **Balance filtering**: Too strict = miss animals, too loose = process non-animals
4. **Monitor performance**: Check if filtering improves FPS
5. **Log filtered detections**: Track what's being filtered for debugging

---

## Summary

✅ **Filter before classification** to improve performance  
✅ **Configure allowed classes** based on your use case  
✅ **Handle "no wildlife" cases** gracefully  
✅ **Keep code modular** with enable/disable options  

**Result**: Faster, more accurate wildlife monitoring! 🦌🐻🦓
