"""
Wildlife Monitoring System

An AI-powered wildlife monitoring system for detecting, classifying,
tracking, and analyzing wildlife from video feeds.
"""

__version__ = "0.1.0"
__author__ = "Wildlife Monitoring Team"

# Import main pipeline for easy access
from .pipeline import WildlifePipeline, PipelineConfig, PipelineResult

__all__ = ["WildlifePipeline", "PipelineConfig", "PipelineResult"]
