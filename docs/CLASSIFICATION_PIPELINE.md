# Improved Classification Pipeline

## Overview

The improved classification pipeline provides proper ResNet50-based species classification with:

✅ **Precise bounding box cropping** - Extract ONLY the detected animal region  
✅ **ResNet50-compliant preprocessing** - Proper resize, crop, and normalization  
✅ **Top-K predictions** - Get top-3 species with confidence scores  
✅ **Unknown species handling** - Mark low-confidence predictions as "Unknown"  
✅ **Batch processing** - Efficient classification of multiple detections  

---

## Quick Start

```python
from wildlife_monitoring.classification import SpeciesClassifier
import cv2

# Initialize classifier
classifier = SpeciesClassifier(
    model_name="resnet50",
    confidence_threshold=0.3,
    top_k=3  # Return top-3 predictions
)

# Load frame and detection bbox
frame = cv2.imread("wildlife.jpg")
bbox = [100, 100, 400, 400]  # From YOLO detection

# Step 1: Crop ONLY the bounding box
cropped = classifier.crop_bbox(frame, bbox)

# Step 2: Classify with top-3 predictions
result = classifier.classify(cropped, return_top_k=True)

# Step 3: Check results
print(f"Species: {result['species']}")
print(f"Confidence: {result['confidence']:.4f}")

if result['is_unknown']:
    print("⚠️  Unknown species (low confidence)")

print("\nTop-3 Predictions:")
for i, pred in enumerate(result['top_predictions'], 1):
    print(f"{i}. {pred['species']}: {pred['confidence']:.4f}")
```

---

## Pipeline Steps

### 1. Bounding Box Cropping

**Purpose**: Extract ONLY the detected animal region

```python
cropped = classifier.crop_bbox(frame, bbox)
```

**What it does**:
- Takes full frame and bounding box `[x1, y1, x2, y2]`
- Validates coordinates are within frame bounds
- Crops the exact region: `frame[y1:y2, x1:x2]`
- Returns cropped image in BGR format

**Example**:
```python
frame.shape  # (480, 640, 3)
bbox = [100, 100, 400, 400]
cropped = classifier.crop_bbox(frame, bbox)
cropped.shape  # (300, 300, 3) - exact bbox size
```

### 2. Preprocessing for ResNet50

**Purpose**: Transform image to ResNet50 input format

```python
tensor = classifier.preprocess_image(cropped)
```

**Steps**:
1. **Convert BGR → RGB**: OpenCV uses BGR, PyTorch uses RGB
2. **Convert to PIL Image**: Required by torchvision transforms
3. **Resize to 256**: Resize shortest side to 256 pixels
4. **Center Crop to 224**: Extract center 224×224 region
5. **Convert to Tensor**: Scale to [0, 1] range
6. **Normalize**: Apply ImageNet mean/std

**Normalization**:
```python
mean = [0.485, 0.456, 0.406]  # ImageNet RGB mean
std  = [0.229, 0.224, 0.225]  # ImageNet RGB std

normalized = (tensor - mean) / std
```

**Result**:
```python
tensor.shape  # torch.Size([3, 224, 224])
tensor.dtype  # torch.float32
tensor.range  # Approximately [-2, 2] after normalization
```

### 3. Classification with Top-K

**Purpose**: Get species predictions with confidence scores

```python
result = classifier.classify(cropped, return_top_k=True)
```

**What it does**:
1. Preprocess image
2. Run ResNet50 inference
3. Apply softmax to get probabilities
4. Extract top-K predictions
5. Check confidence threshold
6. Return structured result

**Result Structure**:
```python
{
    "species": "Red Fox",              # Top prediction
    "confidence": 0.85,                # Top confidence
    "is_unknown": False,               # Below threshold?
    "top_predictions": [               # Top-K predictions
        {
            "species": "Red Fox",
            "confidence": 0.85,
            "class_idx": 281
        },
        {
            "species": "Grey Fox",
            "confidence": 0.10,
            "class_idx": 280
        },
        {
            "species": "Arctic Fox",
            "confidence": 0.03,
            "class_idx": 279
        }
    ]
}
```

### 4. Unknown Species Handling

**Purpose**: Mark low-confidence predictions as "Unknown"

```python
if result['confidence'] < confidence_threshold:
    result['species'] = "Unknown species"
    result['is_unknown'] = True
```

**Example**:
```python
# High confidence - valid species
result = {
    "species": "Red Fox",
    "confidence": 0.85,
    "is_unknown": False
}

# Low confidence - unknown species
result = {
    "species": "Unknown species",
    "confidence": 0.15,
    "is_unknown": True
}
```

---

## Full Pipeline Example

```python
from wildlife_monitoring import WildlifePipeline, PipelineConfig
import cv2

# Configure pipeline
config = PipelineConfig(
    yolo_model_path="yolov8n.pt",
    detection_confidence=0.5,
    classification_enabled=True,
    classification_model="resnet50",
    classification_confidence=0.3,
    allowed_animal_classes={"dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"},
    filter_non_animals=True
)

# Initialize pipeline
pipeline = WildlifePipeline(config)

# Process frame
frame = cv2.imread("wildlife.jpg")
result = pipeline.process_frame(frame, annotate=True)

# Check results
print(f"Detections: {len(result.detections)}")

for i, detection in enumerate(result.detections):
    print(f"\nDetection {i+1}:")
    print(f"  YOLO Class: {detection['class_name']}")
    print(f"  YOLO Confidence: {detection['confidence']:.4f}")
    
    if i in result.classifications:
        classification = result.classifications[i]
        print(f"  Species: {classification['species']}")
        print(f"  Classification Confidence: {classification['confidence']:.4f}")
        
        if classification['is_unknown']:
            print(f"  ⚠️  Unknown species (low confidence)")
        
        print(f"  Top-3 Predictions:")
        for j, pred in enumerate(classification['top_predictions'], 1):
            print(f"    {j}. {pred['species']}: {pred['confidence']:.4f}")
```

---

## Batch Classification

For multiple detections, use batch processing for efficiency:

```python
# Crop all bounding boxes
cropped_images = []
for detection in detections:
    cropped = classifier.crop_bbox(frame, detection['bbox'])
    cropped_images.append(cropped)

# Batch classify (faster than individual)
results = classifier.classify_batch(cropped_images, return_top_k=True)

# Process results
for i, result in enumerate(results):
    print(f"Detection {i+1}: {result['species']} ({result['confidence']:.4f})")
```

---

## Configuration Options

### SpeciesClassifier Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | `str` | `"resnet50"` | Model architecture (resnet50, resnet101, efficientnet_b0) |
| `confidence_threshold` | `float` | `0.3` | Minimum confidence for valid classification |
| `device` | `str` or `None` | `None` | Device (cuda/cpu/mps), auto-detect if None |
| `top_k` | `int` | `3` | Number of top predictions to return |

### Example Configurations

**High Precision** (fewer false positives):
```python
classifier = SpeciesClassifier(
    model_name="resnet101",  # More accurate
    confidence_threshold=0.7,  # High threshold
    top_k=5
)
```

**Fast Processing** (real-time):
```python
classifier = SpeciesClassifier(
    model_name="efficientnet_b0",  # Fastest
    confidence_threshold=0.3,
    top_k=3
)
```

**Balanced** (recommended):
```python
classifier = SpeciesClassifier(
    model_name="resnet50",  # Good accuracy
    confidence_threshold=0.3,  # Reasonable threshold
    top_k=3
)
```

---

## ResNet50 Preprocessing Details

### Input Requirements

- **Input Size**: 224×224 pixels
- **Color Format**: RGB (not BGR)
- **Value Range**: Normalized with ImageNet statistics
- **Data Type**: float32 tensor

### Preprocessing Transform

```python
transforms.Compose([
    transforms.Resize(256),           # Resize shortest side to 256
    transforms.CenterCrop(224),       # Crop center 224×224
    transforms.ToTensor(),            # Convert to [0, 1] tensor
    transforms.Normalize(             # Normalize with ImageNet stats
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
```

### Why These Steps?

1. **Resize to 256**: Maintains aspect ratio while standardizing size
2. **Center Crop to 224**: ResNet50 expects exactly 224×224 input
3. **ToTensor**: Converts PIL Image to PyTorch tensor [0, 1]
4. **Normalize**: Matches ImageNet training distribution

---

## API Reference

### SpeciesClassifier.crop_bbox()

```python
def crop_bbox(
    self,
    frame: np.ndarray,
    bbox: List[float]
) -> np.ndarray
```

**Parameters**:
- `frame`: Full frame (BGR format from OpenCV)
- `bbox`: Bounding box `[x1, y1, x2, y2]`

**Returns**:
- Cropped image region (BGR format)

**Raises**:
- `ValueError`: If bounding box is invalid

### SpeciesClassifier.preprocess_image()

```python
def preprocess_image(
    self,
    image: np.ndarray
) -> torch.Tensor
```

**Parameters**:
- `image`: Cropped image (BGR format)

**Returns**:
- Preprocessed tensor `[3, 224, 224]`

### SpeciesClassifier.classify()

```python
def classify(
    self,
    image: np.ndarray,
    return_top_k: bool = True
) -> Dict[str, any]
```

**Parameters**:
- `image`: Cropped image (BGR format)
- `return_top_k`: Whether to return top-K predictions

**Returns**:
```python
{
    "species": str,
    "confidence": float,
    "is_unknown": bool,
    "top_predictions": List[Dict]
}
```

### SpeciesClassifier.classify_batch()

```python
def classify_batch(
    self,
    images: List[np.ndarray],
    return_top_k: bool = True
) -> List[Dict[str, any]]
```

**Parameters**:
- `images`: List of cropped images
- `return_top_k`: Whether to return top-K predictions

**Returns**:
- List of classification results

### SpeciesClassifier.get_top_k_predictions()

```python
def get_top_k_predictions(
    self,
    image: np.ndarray,
    k: Optional[int] = None
) -> List[Tuple[str, float]]
```

**Parameters**:
- `image`: Cropped image
- `k`: Number of predictions (uses `self.top_k` if None)

**Returns**:
- List of `(species_name, confidence)` tuples

---

## Performance Tips

1. **Use batch classification** for multiple detections
2. **Use GPU** if available (CUDA/MPS)
3. **Use EfficientNet-B0** for real-time applications
4. **Adjust confidence threshold** based on your use case
5. **Cache classifier instance** - don't recreate for each frame

---

## Troubleshooting

### Issue: "Invalid bounding box" error

**Cause**: Bounding box coordinates are invalid

**Solution**: Validate bbox before cropping
```python
from wildlife_monitoring.classification import classifier_utils

if classifier_utils.validate_bbox(bbox, frame.shape[:2]):
    cropped = classifier.crop_bbox(frame, bbox)
else:
    print("Invalid bbox")
```

### Issue: Low confidence for all predictions

**Cause**: Image quality or species not in ImageNet

**Solution**: 
- Check image quality (blur, lighting)
- Lower confidence threshold
- Consider fine-tuning on wildlife dataset

### Issue: Slow classification

**Cause**: CPU inference or large model

**Solution**:
- Use GPU if available
- Switch to EfficientNet-B0
- Use batch classification
- Reduce frame rate

---

## Summary

✅ **Precise cropping** - Extract exact bounding box region  
✅ **Proper preprocessing** - ResNet50-compliant transforms  
✅ **Top-K predictions** - Get multiple species candidates  
✅ **Unknown handling** - Clear low-confidence marking  
✅ **Batch processing** - Efficient multi-detection classification  

**Result**: Accurate, efficient wildlife species classification! 🦌🦊🐻
