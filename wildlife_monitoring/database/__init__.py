"""
Database Module

SQLite database layer for wildlife monitoring system.
"""

from .wildlife_db import WildlifeDatabase, SightingRecord
from .pipeline_integration import save_pipeline_results_to_db, get_track_history

__all__ = [
    "WildlifeDatabase",
    "SightingRecord",
    "save_pipeline_results_to_db",
    "get_track_history"
]
