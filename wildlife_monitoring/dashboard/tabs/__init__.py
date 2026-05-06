"""
Dashboard tabs package.
"""

from . import live_monitoring
from . import analytics
from . import sightings_database
from . import system_insights

__all__ = [
    'live_monitoring',
    'analytics',
    'sightings_database',
    'system_insights'
]
