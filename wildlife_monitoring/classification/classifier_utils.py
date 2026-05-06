"""
Classifier Utilities

Helper functions for classification preprocessing.
"""

import cv2
import numpy as np
from typing import List, Tuple


def extract_roi(frame: np.ndarray, bbox: List[float]) -> np.ndarray:
    """
    Extract region of interest (ROI) from frame based on bounding box.
    
    Crops ONLY the bounding box region for classification.
    
    Args:
        frame: Input frame (BGR format from OpenCV)
        bbox: Bounding box [x1, y1, x2, y2]
        
    Returns:
        Cropped image region (BGR format)
        
    Raises:
        ValueError: If bounding box is invalid
    """
    x1, y1, x2, y2 = map(int, bbox)
    
    # Ensure coordinates are within frame bounds
    h, w = frame.shape[:2]
    x1 = max(0, min(x1, w))
    y1 = max(0, min(y1, h))
    x2 = max(0, min(x2, w))
    y2 = max(0, min(y2, h))
    
    # Validate bbox dimensions
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"Invalid bounding box: [{x1}, {y1}, {x2}, {y2}]")
    
    # Crop the region (copy to avoid modifying original)
    cropped = frame[y1:y2, x1:x2].copy()
    
    return cropped


def prepare_for_classification(
    image: np.ndarray,
    target_size: Tuple[int, int] = (224, 224),
    normalize: bool = True
) -> np.ndarray:
    """
    Prepare image for classification model input.
    
    Note: This is a legacy function. For ResNet50, use the classifier's
    built-in preprocessing which handles resize, crop, and normalization.
    
    Args:
        image: Input image
        target_size: Target size (width, height)
        normalize: Whether to normalize to [0, 1]
        
    Returns:
        Preprocessed image
    """
    # Resize
    resized = cv2.resize(image, target_size)
    
    # Convert to RGB if needed
    if len(resized.shape) == 2:
        resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
    elif resized.shape[2] == 4:
        resized = cv2.cvtColor(resized, cv2.COLOR_BGRA2RGB)
    else:
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    
    # Normalize
    if normalize:
        resized = resized.astype(np.float32) / 255.0
    
    return resized


def validate_bbox(bbox: List[float], frame_shape: Tuple[int, int]) -> bool:
    """
    Validate if bounding box is within frame bounds and has valid dimensions.
    
    Args:
        bbox: Bounding box [x1, y1, x2, y2]
        frame_shape: Frame shape (height, width)
        
    Returns:
        True if bbox is valid, False otherwise
    """
    x1, y1, x2, y2 = bbox
    h, w = frame_shape
    
    # Check if coordinates are within bounds
    if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
        return False
    
    # Check if bbox has valid dimensions
    if x2 <= x1 or y2 <= y1:
        return False
    
    return True


def augment_image(image: np.ndarray) -> List[np.ndarray]:
    """
    Create augmented versions of image for robust classification.
    
    Args:
        image: Input image
        
    Returns:
        List of augmented images including original
    """
    augmented = [image]
    
    # Horizontal flip
    augmented.append(cv2.flip(image, 1))
    
    # Brightness adjustment
    bright = cv2.convertScaleAbs(image, alpha=1.2, beta=10)
    augmented.append(bright)
    
    # Slight rotation
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, 5, 1.0)
    rotated = cv2.warpAffine(image, matrix, (w, h))
    augmented.append(rotated)
    
    return augmented
