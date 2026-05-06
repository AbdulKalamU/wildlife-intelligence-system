"""
Pipeline Module

Orchestrates the complete wildlife monitoring pipeline.
"""

from .orchestrator import WildlifePipeline, PipelineConfig, PipelineResult

__all__ = ["WildlifePipeline", "PipelineConfig", "PipelineResult"]
