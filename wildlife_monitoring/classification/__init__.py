"""
Classification Module

Species classification for detected wildlife.
"""

from .species_classifier import SpeciesClassifier
from .classifier_utils import extract_roi, prepare_for_classification

__all__ = ["SpeciesClassifier", "extract_roi", "prepare_for_classification"]
