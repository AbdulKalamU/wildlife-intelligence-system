"""
Species Classifier Module

Improved classification pipeline with proper preprocessing and top-K predictions.
Classifies detected wildlife into specific species using pretrained ResNet50.
"""

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import numpy as np
from typing import Dict, List, Tuple, Optional
from PIL import Image


class SpeciesClassifier:
    """
    Classifies wildlife species from detected objects using pretrained ResNet50.
    
    Features:
    - Proper bounding box cropping
    - ResNet50-compliant preprocessing (resize, normalize)
    - Top-K predictions with confidence scores
    - "Unknown species" handling for low confidence
    
    Attributes:
        model: ResNet50 model
        device: Computation device (cuda/cpu/mps)
        transform: Image preprocessing pipeline
        class_names: ImageNet class names
        confidence_threshold: Minimum confidence for classification
    """
    
    def __init__(
        self,
        model_name: str = "resnet50",
        confidence_threshold: float = 0.3,
        device: Optional[str] = None,
        top_k: int = 3
    ):
        """
        Initialize species classifier with pretrained model.
        
        Args:
            model_name: Model architecture (resnet50, resnet101, efficientnet_b0)
            confidence_threshold: Minimum confidence for valid classification
            device: Device to run model on (cuda/cpu/mps), auto-detect if None
            top_k: Number of top predictions to return
        """
        self.confidence_threshold = confidence_threshold
        self.top_k = top_k
        
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = torch.device("mps")  # Apple Silicon
            else:
                self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)
        
        # Load pretrained model
        self.model = self._load_model(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # Setup preprocessing (ResNet50 standard)
        self.transform = self._get_resnet_transform()
        
        # Load ImageNet class names
        self.class_names = self._load_imagenet_classes()
        
        # Map to wildlife-relevant classes
        self.wildlife_class_indices = self._get_wildlife_classes()
    
    def _load_model(self, model_name: str) -> nn.Module:
        """
        Load pretrained model.
        
        Args:
            model_name: Model architecture name
            
        Returns:
            Pretrained model
        """
        if model_name == "resnet50":
            model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        elif model_name == "resnet101":
            model = models.resnet101(weights=models.ResNet101_Weights.IMAGENET1K_V2)
        elif model_name == "efficientnet_b0":
            model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        else:
            # Default to ResNet50
            model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        
        return model
    
    def _get_resnet_transform(self) -> transforms.Compose:
        """
        Get ResNet50-compliant image preprocessing transform.
        
        ResNet50 requirements:
        1. Resize to 256x256
        2. Center crop to 224x224
        3. Convert to tensor [0, 1]
        4. Normalize with ImageNet mean/std
        
        Returns:
            Composed transforms
        """
        return transforms.Compose([
            transforms.Resize(256),                    # Resize shortest side to 256
            transforms.CenterCrop(224),                # Crop center 224x224
            transforms.ToTensor(),                     # Convert to tensor [0, 1]
            transforms.Normalize(                      # Normalize with ImageNet stats
                mean=[0.485, 0.456, 0.406],           # ImageNet mean (RGB)
                std=[0.229, 0.224, 0.225]             # ImageNet std (RGB)
            )
        ])
    
    def _load_imagenet_classes(self) -> List[str]:
        """
        Load ImageNet class names.
        
        Returns:
            List of class names (1000 classes)
        """
        try:
            # Try to get class names from model weights metadata
            weights = models.ResNet50_Weights.IMAGENET1K_V2
            return weights.meta["categories"]
        except:
            # Fallback to basic list
            return [f"class_{i}" for i in range(1000)]
    
    def _get_wildlife_classes(self) -> Dict[int, str]:
        """
        Get mapping of ImageNet indices to wildlife species.
        
        Returns:
            Dictionary mapping class index to species name
        """
        # Common wildlife animals in ImageNet (class_idx: name)
        wildlife_mapping = {
            # Mammals - Deer family
            144: "White-tailed Deer",
            145: "Mule Deer",
            146: "Axis Deer",
            147: "Elk",
            148: "Moose",
            # Canines - Foxes
            279: "Arctic Fox",
            280: "Grey Fox",
            281: "Red Fox",
            282: "Kit Fox",
            # Bears
            294: "Brown Bear",
            295: "American Black Bear",
            296: "Polar Bear",
            297: "Sloth Bear",
            # Wolves and wild canines
            248: "Eskimo Dog",
            249: "Malamute",
            250: "Siberian Husky",
            269: "Timber Wolf",
            270: "White Wolf",
            271: "Red Wolf",
            272: "Coyote",
            273: "Dingo",
            # Small mammals
            330: "Rabbit",
            331: "Hare",
            332: "Angora Rabbit",
            333: "Hamster",
            334: "Porcupine",
            335: "Fox Squirrel",
            336: "Marmot",
            337: "Beaver",
            338: "Guinea Pig",
            339: "Horse",
            340: "Zebra",
            341: "Giraffe",
            # Big cats
            282: "Tiger",
            283: "Jaguar",
            284: "Lion",
            285: "Cheetah",
            286: "Leopard",
            # Birds
            7: "Rooster",
            8: "Hen",
            9: "Ostrich",
            10: "Brambling",
            11: "Goldfinch",
            12: "House Finch",
            13: "Junco",
            14: "Indigo Bunting",
            15: "Robin",
            16: "Bulbul",
            17: "Jay",
            18: "Magpie",
            19: "Chickadee",
            20: "Water Ouzel",
            21: "Kite",
            22: "Bald Eagle",
            23: "Vulture",
            24: "Great Grey Owl",
            # Reptiles & Amphibians
            25: "European Fire Salamander",
            26: "Common Newt",
            27: "Eft",
            28: "Spotted Salamander",
            29: "Axolotl",
            30: "Bullfrog",
            31: "Tree Frog",
            32: "Tailed Frog",
        }
        
        return wildlife_mapping
    
    def crop_bbox(self, frame: np.ndarray, bbox: List[float]) -> np.ndarray:
        """
        Crop ONLY the bounding box region from frame.
        
        Args:
            frame: Full frame (BGR format from OpenCV)
            bbox: Bounding box [x1, y1, x2, y2]
            
        Returns:
            Cropped image region (BGR format)
        """
        x1, y1, x2, y2 = map(int, bbox)
        
        # Ensure coordinates are within frame bounds
        h, w = frame.shape[:2]
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))
        
        # Validate bbox
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"Invalid bounding box: [{x1}, {y1}, {x2}, {y2}]")
        
        # Crop the region
        cropped = frame[y1:y2, x1:x2].copy()
        
        return cropped
    
    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """
        Preprocess image for ResNet50 input.
        
        Steps:
        1. Convert BGR (OpenCV) to RGB (PIL/PyTorch)
        2. Convert to PIL Image
        3. Apply ResNet50 transforms (resize, crop, normalize)
        
        Args:
            image: Cropped image (BGR format from OpenCV)
            
        Returns:
            Preprocessed tensor ready for model input
        """
        # Convert BGR to RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = image[:, :, ::-1].copy()  # BGR -> RGB
        else:
            image_rgb = image
        
        # Convert to PIL Image (required by torchvision transforms)
        pil_image = Image.fromarray(image_rgb)
        
        # Apply ResNet50 preprocessing
        tensor = self.transform(pil_image)
        
        return tensor
    
    def classify(
        self,
        image: np.ndarray,
        return_top_k: bool = True
    ) -> Dict[str, any]:
        """
        Classify a single wildlife image with top-K predictions.
        
        Args:
            image: Cropped image of detected animal (BGR format from OpenCV)
            return_top_k: Whether to return top-K predictions
            
        Returns:
            Dictionary containing:
                - species: str (top species name or "Unknown species")
                - confidence: float (top confidence score)
                - top_predictions: List[Dict] (top-K predictions with scores)
                - all_predictions: Dict (all class probabilities)
        """
        # Preprocess image
        input_tensor = self.preprocess_image(image)
        input_batch = input_tensor.unsqueeze(0).to(self.device)
        
        # Run inference
        with torch.no_grad():
            output = self.model(input_batch)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
        
        # Get top-K predictions
        top_probs, top_indices = torch.topk(probabilities, k=self.top_k)
        
        # Convert to CPU and numpy
        top_probs = top_probs.cpu().numpy()
        top_indices = top_indices.cpu().numpy()
        
        # Build top-K predictions list
        top_predictions = []
        for idx, prob in zip(top_indices, top_probs):
            class_name = self.class_names[idx] if idx < len(self.class_names) else f"class_{idx}"
            
            # Use wildlife name if available
            if idx in self.wildlife_class_indices:
                class_name = self.wildlife_class_indices[idx]
            
            top_predictions.append({
                "species": class_name,
                "confidence": float(prob),
                "class_idx": int(idx)
            })
        
        # Determine final species (top prediction)
        top_species = top_predictions[0]["species"]
        top_confidence = top_predictions[0]["confidence"]
        
        # Mark as "Unknown species" if confidence below threshold
        if top_confidence < self.confidence_threshold:
            top_species = "Unknown species"
        
        # Build result
        result = {
            "species": top_species,
            "confidence": top_confidence,
            "top_predictions": top_predictions,
            "is_unknown": top_confidence < self.confidence_threshold
        }
        
        return result
    
    def classify_batch(
        self,
        images: List[np.ndarray],
        return_top_k: bool = True
    ) -> List[Dict[str, any]]:
        """
        Classify multiple wildlife images in batch.
        
        Args:
            images: List of cropped images (BGR format)
            return_top_k: Whether to return top-K predictions
            
        Returns:
            List of classification results
        """
        if not images:
            return []
        
        # Preprocess all images
        input_tensors = []
        for image in images:
            try:
                input_tensor = self.preprocess_image(image)
                input_tensors.append(input_tensor)
            except Exception as e:
                # Skip invalid images
                print(f"Warning: Failed to preprocess image: {e}")
                continue
        
        if not input_tensors:
            return []
        
        # Stack into batch
        input_batch = torch.stack(input_tensors).to(self.device)
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(input_batch)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
        
        # Process each result
        results = []
        for i in range(len(input_tensors)):
            probs = probabilities[i]
            top_probs, top_indices = torch.topk(probs, k=self.top_k)
            
            top_probs = top_probs.cpu().numpy()
            top_indices = top_indices.cpu().numpy()
            
            # Build top-K predictions
            top_predictions = []
            for idx, prob in zip(top_indices, top_probs):
                class_name = self.class_names[idx] if idx < len(self.class_names) else f"class_{idx}"
                
                # Use wildlife name if available
                if idx in self.wildlife_class_indices:
                    class_name = self.wildlife_class_indices[idx]
                
                top_predictions.append({
                    "species": class_name,
                    "confidence": float(prob),
                    "class_idx": int(idx)
                })
            
            # Determine final species
            top_species = top_predictions[0]["species"]
            top_confidence = top_predictions[0]["confidence"]
            
            # Mark as "Unknown species" if confidence below threshold
            if top_confidence < self.confidence_threshold:
                top_species = "Unknown species"
            
            result = {
                "species": top_species,
                "confidence": top_confidence,
                "top_predictions": top_predictions,
                "is_unknown": top_confidence < self.confidence_threshold
            }
            results.append(result)
        
        return results
    
    def get_top_k_predictions(
        self,
        image: np.ndarray,
        k: Optional[int] = None
    ) -> List[Tuple[str, float]]:
        """
        Get top-K species predictions as simple tuples.
        
        Args:
            image: Cropped image of detected animal
            k: Number of top predictions (uses self.top_k if None)
            
        Returns:
            List of (species_name, confidence) tuples
        """
        if k is None:
            k = self.top_k
        
        result = self.classify(image, return_top_k=True)
        
        return [
            (pred["species"], pred["confidence"])
            for pred in result["top_predictions"][:k]
        ]
