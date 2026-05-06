"""
Trend Analyzer Module

Analyzes trends in wildlife detection and tracking data.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime, timedelta


class TrendAnalyzer:
    """
    Analyzes trends in wildlife monitoring data.
    
    Attributes:
        detection_history: Historical detection data
        species_counts: Species count over time
    """
    
    def __init__(self):
        """Initialize trend analyzer."""
        self.detection_history = []
        self.species_counts = defaultdict(list)
        self.hourly_activity = defaultdict(list)
    
    def add_detection_data(
        self,
        timestamp: datetime,
        species: str,
        count: int,
        location: Tuple[float, float] = None
    ):
        """
        Add detection data point for trend analysis.
        
        Args:
            timestamp: Detection timestamp
            species: Species name
            count: Number of individuals detected
            location: Optional (x, y) location
        """
        entry = {
            "timestamp": timestamp,
            "species": species,
            "count": count,
            "location": location
        }
        
        self.detection_history.append(entry)
        self.species_counts[species].append((timestamp, count))
        
        # Track hourly activity
        hour = timestamp.hour
        self.hourly_activity[species].append(hour)
    
    def get_species_trend(
        self,
        species: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get trend analysis for a specific species.
        
        Args:
            species: Species name
            time_window_hours: Time window for analysis
            
        Returns:
            Dictionary with trend information
        """
        if species not in self.species_counts:
            return {"trend": "no_data", "change_rate": 0.0}
        
        data = self.species_counts[species]
        
        if len(data) < 2:
            return {"trend": "insufficient_data", "change_rate": 0.0}
        
        # Filter by time window
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        recent_data = [(ts, count) for ts, count in data if ts >= cutoff_time]
        
        if len(recent_data) < 2:
            return {"trend": "insufficient_recent_data", "change_rate": 0.0}
        
        # Calculate trend
        counts = [count for _, count in recent_data]
        
        # Simple linear trend
        x = np.arange(len(counts))
        coeffs = np.polyfit(x, counts, 1)
        slope = coeffs[0]
        
        # Determine trend direction
        if slope > 0.1:
            trend = "increasing"
        elif slope < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_rate": float(slope),
            "average_count": float(np.mean(counts)),
            "max_count": int(np.max(counts)),
            "min_count": int(np.min(counts)),
            "data_points": len(recent_data)
        }
    
    def get_peak_activity_hours(self, species: str) -> List[int]:
        """
        Get peak activity hours for a species.
        
        Args:
            species: Species name
            
        Returns:
            List of hours (0-23) with highest activity
        """
        if species not in self.hourly_activity:
            return []
        
        hours = self.hourly_activity[species]
        
        if not hours:
            return []
        
        # Count occurrences per hour
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        # Get top 3 hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, _ in sorted_hours[:3]]
    
    def get_species_diversity(self) -> Dict[str, Any]:
        """
        Calculate species diversity metrics.
        
        Returns:
            Dictionary with diversity metrics
        """
        unique_species = set(self.species_counts.keys())
        
        if not unique_species:
            return {
                "total_species": 0,
                "diversity_index": 0.0,
                "most_common": None
            }
        
        # Calculate total counts per species
        species_totals = {}
        for species, data in self.species_counts.items():
            species_totals[species] = sum(count for _, count in data)
        
        total_individuals = sum(species_totals.values())
        
        # Shannon diversity index
        diversity_index = 0.0
        if total_individuals > 0:
            for count in species_totals.values():
                if count > 0:
                    proportion = count / total_individuals
                    diversity_index -= proportion * np.log(proportion)
        
        # Most common species
        most_common = max(species_totals.items(), key=lambda x: x[1])[0] if species_totals else None
        
        return {
            "total_species": len(unique_species),
            "diversity_index": float(diversity_index),
            "most_common": most_common,
            "species_distribution": species_totals
        }
    
    def get_population_estimate(
        self,
        species: str,
        time_window_hours: int = 24
    ) -> int:
        """
        Estimate population for a species based on unique tracks.
        
        Args:
            species: Species name
            time_window_hours: Time window for estimation
            
        Returns:
            Estimated population count
        """
        if species not in self.species_counts:
            return 0
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        recent_data = [(ts, count) for ts, count in self.species_counts[species] if ts >= cutoff_time]
        
        if not recent_data:
            return 0
        
        # Use maximum count as population estimate
        return max(count for _, count in recent_data)
