"""
Sightings Analytics Module

Analyzes stored wildlife sightings data to provide insights:
- Species counts
- Trend analysis (increasing/decreasing)
- Time-based grouping
- Comparative statistics

Uses SQLite queries and Python logic for efficient analysis.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class Trend(Enum):
    """Trend direction enumeration."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass
class SpeciesAnalytics:
    """
    Analytics result for a species.
    
    Attributes:
        species: Species name
        count: Total count in time window
        trend: Trend direction (increasing/decreasing/stable)
        avg_confidence: Average classification confidence
        unique_tracks: Number of unique tracks
        first_seen: First sighting timestamp
        last_seen: Last sighting timestamp
        previous_count: Count in previous time window (for trend)
        trend_percentage: Percentage change from previous period
    """
    species: str
    count: int
    trend: str
    avg_confidence: float = 0.0
    unique_tracks: int = 0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    previous_count: int = 0
    trend_percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "species": self.species,
            "count": self.count,
            "trend": self.trend,
            "avg_confidence": round(self.avg_confidence, 2),
            "unique_tracks": self.unique_tracks,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "previous_count": self.previous_count,
            "trend_percentage": round(self.trend_percentage, 2)
        }


class SightingsAnalytics:
    """
    Analytics engine for wildlife sightings data.
    
    Provides time-based analysis, trend detection, and species statistics.
    """
    
    def __init__(self, db_path: str = "wildlife_sightings.db"):
        """
        Initialize analytics engine.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.connection = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
    
    def analyze_species(
        self,
        species: str,
        time_window_minutes: int = 60,
        trend_comparison_minutes: Optional[int] = None
    ) -> SpeciesAnalytics:
        """
        Analyze a specific species within a time window.
        
        Args:
            species: Species name to analyze
            time_window_minutes: Time window in minutes (default: 60)
            trend_comparison_minutes: Previous period for trend comparison
                                     (defaults to same as time_window_minutes)
        
        Returns:
            SpeciesAnalytics object with analysis results
        """
        if trend_comparison_minutes is None:
            trend_comparison_minutes = time_window_minutes
        
        # Calculate time boundaries
        now = datetime.now()
        current_start = now - timedelta(minutes=time_window_minutes)
        previous_start = current_start - timedelta(minutes=trend_comparison_minutes)
        
        # Get current period statistics
        current_stats = self._get_species_stats(
            species,
            current_start.isoformat(),
            now.isoformat()
        )
        
        # Get previous period count for trend
        previous_count = self._get_species_count(
            species,
            previous_start.isoformat(),
            current_start.isoformat()
        )
        
        # Calculate trend
        trend, trend_percentage = self._calculate_trend(
            current_stats["count"],
            previous_count
        )
        
        return SpeciesAnalytics(
            species=species,
            count=current_stats["count"],
            trend=trend.value,
            avg_confidence=current_stats["avg_confidence"],
            unique_tracks=current_stats["unique_tracks"],
            first_seen=current_stats["first_seen"],
            last_seen=current_stats["last_seen"],
            previous_count=previous_count,
            trend_percentage=trend_percentage
        )
    
    def analyze_all_species(
        self,
        time_window_minutes: int = 60,
        trend_comparison_minutes: Optional[int] = None,
        min_count: int = 1
    ) -> List[SpeciesAnalytics]:
        """
        Analyze all species within a time window.
        
        Args:
            time_window_minutes: Time window in minutes (default: 60)
            trend_comparison_minutes: Previous period for trend comparison
            min_count: Minimum count to include in results (default: 1)
        
        Returns:
            List of SpeciesAnalytics objects, sorted by count (descending)
        """
        # Get all species in current time window
        now = datetime.now()
        current_start = now - timedelta(minutes=time_window_minutes)
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT species
            FROM sightings
            WHERE timestamp >= ?
        """, (current_start.isoformat(),))
        
        species_list = [row[0] for row in cursor.fetchall()]
        
        # Analyze each species
        results = []
        for species in species_list:
            analytics = self.analyze_species(
                species,
                time_window_minutes,
                trend_comparison_minutes
            )
            
            if analytics.count >= min_count:
                results.append(analytics)
        
        # Sort by count (descending)
        results.sort(key=lambda x: x.count, reverse=True)
        
        return results
    
    def get_species_count(
        self,
        species: str,
        time_window_minutes: int = 60
    ) -> int:
        """
        Get count of sightings for a species in time window.
        
        Args:
            species: Species name
            time_window_minutes: Time window in minutes
        
        Returns:
            Count of sightings
        """
        now = datetime.now()
        start_time = now - timedelta(minutes=time_window_minutes)
        
        return self._get_species_count(
            species,
            start_time.isoformat(),
            now.isoformat()
        )
    
    def get_all_species_counts(
        self,
        time_window_minutes: int = 60
    ) -> Dict[str, int]:
        """
        Get counts for all species in time window.
        
        Args:
            time_window_minutes: Time window in minutes
        
        Returns:
            Dictionary mapping species name to count
        """
        now = datetime.now()
        start_time = now - timedelta(minutes=time_window_minutes)
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT species, COUNT(*) as count
            FROM sightings
            WHERE timestamp >= ? AND timestamp <= ?
            GROUP BY species
            ORDER BY count DESC
        """, (start_time.isoformat(), now.isoformat()))
        
        return {row[0]: row[1] for row in cursor.fetchall()}
    
    def get_hourly_breakdown(
        self,
        species: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get hourly breakdown of sightings.
        
        Args:
            species: Species name (None = all species)
            hours: Number of hours to analyze
        
        Returns:
            List of dictionaries with hour and count
        """
        now = datetime.now()
        start_time = now - timedelta(hours=hours)
        
        cursor = self.connection.cursor()
        
        if species:
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                    COUNT(*) as count
                FROM sightings
                WHERE timestamp >= ? AND species = ?
                GROUP BY hour
                ORDER BY hour ASC
            """, (start_time.isoformat(), species))
        else:
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                    COUNT(*) as count
                FROM sightings
                WHERE timestamp >= ?
                GROUP BY hour
                ORDER BY hour ASC
            """, (start_time.isoformat(),))
        
        return [{"hour": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    def get_activity_summary(
        self,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get overall activity summary for time window.
        
        Args:
            time_window_minutes: Time window in minutes
        
        Returns:
            Dictionary with summary statistics
        """
        now = datetime.now()
        start_time = now - timedelta(minutes=time_window_minutes)
        
        cursor = self.connection.cursor()
        
        # Total sightings
        cursor.execute("""
            SELECT COUNT(*) FROM sightings
            WHERE timestamp >= ?
        """, (start_time.isoformat(),))
        total_sightings = cursor.fetchone()[0]
        
        # Unique species
        cursor.execute("""
            SELECT COUNT(DISTINCT species) FROM sightings
            WHERE timestamp >= ?
        """, (start_time.isoformat(),))
        unique_species = cursor.fetchone()[0]
        
        # Unique tracks
        cursor.execute("""
            SELECT COUNT(DISTINCT track_id) FROM sightings
            WHERE timestamp >= ?
        """, (start_time.isoformat(),))
        unique_tracks = cursor.fetchone()[0]
        
        # Average confidence
        cursor.execute("""
            SELECT AVG(confidence) FROM sightings
            WHERE timestamp >= ?
        """, (start_time.isoformat(),))
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # Most common species
        cursor.execute("""
            SELECT species, COUNT(*) as count
            FROM sightings
            WHERE timestamp >= ?
            GROUP BY species
            ORDER BY count DESC
            LIMIT 1
        """, (start_time.isoformat(),))
        
        most_common_row = cursor.fetchone()
        most_common_species = most_common_row[0] if most_common_row else None
        most_common_count = most_common_row[1] if most_common_row else 0
        
        return {
            "time_window_minutes": time_window_minutes,
            "start_time": start_time.isoformat(),
            "end_time": now.isoformat(),
            "total_sightings": total_sightings,
            "unique_species": unique_species,
            "unique_tracks": unique_tracks,
            "avg_confidence": round(avg_confidence, 2),
            "most_common_species": most_common_species,
            "most_common_count": most_common_count
        }
    
    def compare_time_periods(
        self,
        species: Optional[str] = None,
        period_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Compare current period with previous period.
        
        Args:
            species: Species name (None = all species)
            period_minutes: Period length in minutes
        
        Returns:
            Dictionary with comparison results
        """
        now = datetime.now()
        current_start = now - timedelta(minutes=period_minutes)
        previous_start = current_start - timedelta(minutes=period_minutes)
        
        # Current period count
        if species:
            current_count = self._get_species_count(
                species,
                current_start.isoformat(),
                now.isoformat()
            )
            previous_count = self._get_species_count(
                species,
                previous_start.isoformat(),
                current_start.isoformat()
            )
        else:
            current_count = self._get_total_count(
                current_start.isoformat(),
                now.isoformat()
            )
            previous_count = self._get_total_count(
                previous_start.isoformat(),
                current_start.isoformat()
            )
        
        # Calculate trend
        trend, trend_percentage = self._calculate_trend(current_count, previous_count)
        
        return {
            "species": species or "all",
            "current_period_count": current_count,
            "previous_period_count": previous_count,
            "trend": trend.value,
            "trend_percentage": round(trend_percentage, 2),
            "period_minutes": period_minutes
        }
    
    def _get_species_stats(
        self,
        species: str,
        start_time: str,
        end_time: str
    ) -> Dict[str, Any]:
        """
        Get statistics for a species in time range.
        
        Args:
            species: Species name
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
        
        Returns:
            Dictionary with statistics
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                AVG(confidence) as avg_confidence,
                COUNT(DISTINCT track_id) as unique_tracks,
                MIN(timestamp) as first_seen,
                MAX(timestamp) as last_seen
            FROM sightings
            WHERE species = ? AND timestamp >= ? AND timestamp <= ?
        """, (species, start_time, end_time))
        
        row = cursor.fetchone()
        
        return {
            "count": row[0] or 0,
            "avg_confidence": row[1] or 0.0,
            "unique_tracks": row[2] or 0,
            "first_seen": row[3],
            "last_seen": row[4]
        }
    
    def _get_species_count(
        self,
        species: str,
        start_time: str,
        end_time: str
    ) -> int:
        """
        Get count for a species in time range.
        
        Args:
            species: Species name
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
        
        Returns:
            Count of sightings
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM sightings
            WHERE species = ? AND timestamp >= ? AND timestamp <= ?
        """, (species, start_time, end_time))
        
        return cursor.fetchone()[0] or 0
    
    def _get_total_count(
        self,
        start_time: str,
        end_time: str
    ) -> int:
        """
        Get total count in time range.
        
        Args:
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
        
        Returns:
            Total count of sightings
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM sightings
            WHERE timestamp >= ? AND timestamp <= ?
        """, (start_time, end_time))
        
        return cursor.fetchone()[0] or 0
    
    def _calculate_trend(
        self,
        current_count: int,
        previous_count: int,
        stable_threshold: float = 0.1
    ) -> tuple[Trend, float]:
        """
        Calculate trend direction and percentage change.
        
        Args:
            current_count: Count in current period
            previous_count: Count in previous period
            stable_threshold: Threshold for stable trend (default: 10%)
        
        Returns:
            Tuple of (Trend, percentage_change)
        """
        # Insufficient data
        if current_count == 0 and previous_count == 0:
            return Trend.INSUFFICIENT_DATA, 0.0
        
        # Calculate percentage change
        if previous_count == 0:
            if current_count > 0:
                return Trend.INCREASING, 100.0
            else:
                return Trend.STABLE, 0.0
        
        percentage_change = ((current_count - previous_count) / previous_count) * 100
        
        # Determine trend
        if abs(percentage_change) < stable_threshold * 100:
            return Trend.STABLE, percentage_change
        elif percentage_change > 0:
            return Trend.INCREASING, percentage_change
        else:
            return Trend.DECREASING, percentage_change
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor - ensure connection is closed."""
        self.close()
