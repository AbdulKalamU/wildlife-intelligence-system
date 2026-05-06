"""
State management for wildlife monitoring dashboard.

This module provides a single global state singleton that persists
across Streamlit reruns.
"""

from .global_state import (
    AppState,
    get_app_state,
    initialize_system,
    reset_monitoring_state,
    clear_database,
    get_database_stats
)

__all__ = [
    'AppState',
    'get_app_state',
    'initialize_system',
    'reset_monitoring_state',
    'clear_database',
    'get_database_stats'
]
