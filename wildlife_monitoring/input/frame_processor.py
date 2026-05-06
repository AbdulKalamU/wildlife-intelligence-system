"""
Frame Processor Module

Handles frame extraction and preprocessing for detection pipeline.
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class FrameProcessor:
    """
    Processes video frames for detection and classification.
    
    Attributes:
        target_size: Target size for frame resizing (width, height)
        normalize: Whether to normalize pixel values
    """
    
    def __init__(self, target_size: Optional[Tuple[int, int]] = None, normalize: bool = False):
        """
        Initialize frame processor.
        
        Args:
            target_size: Optional target size (width, height) for resizing
            normalize: Whether to normalize pixel values to [0, 1]
        """
        self.target_size = target_size
        self.normalize = normalize
    
    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess a frame for detection.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            Preprocessed frame
        """
        processed = frame.copy()
        
        # Resize if target size specified
        if self.target_size is not None:
            processed = cv2.resize(processed, self.target_size)
        
        # Normalize if requested
        if self.normalize:
            processed = processed.astype(np.float32) / 255.0
        
        return processed
    
    def enhance_contrast(self, frame: np.ndarray) -> np.ndarray:
        """
        Enhance frame contrast using CLAHE.
        
        Args:
            frame: Input frame
            
        Returns:
            Contrast-enhanced frame
        """
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        enhanced = cv2.merge([l, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    def denoise(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply denoising to frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Denoised frame
        """
        return cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
