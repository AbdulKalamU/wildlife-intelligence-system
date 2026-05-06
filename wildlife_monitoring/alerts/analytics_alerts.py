"""
Analytics-Based Alert System

Alert system built on top of the sightings analytics module.

Features:
- Population risk alerts (decreasing trends)
- Low population alerts (below threshold)
- Anomaly alerts (sudden spikes)
- Configurable severity levels
- Rule-based triggering

Alert Types:
- population_risk: Decreasing trend detected
- low_population: Count below threshold
- anomaly: Sudden spike in activity
- stable: No alerts (informational)

Severity Levels:
- high: Decreasing + low count
- medium: Only decreasing or only low count
- low: Stable or minor issues
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class AlertType(Enum):
    """Alert type enumeration."""
    POPULATION_RISK = "population_risk"
    LOW_POPULATION = "low_population"
    ANOMALY = "anomaly"
    STABLE = "stable"
    NO_DATA = "no_data"


class Severity(Enum):
    """Alert severity enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class AlertConfig:
    """
    Configuration for alert rules.
    
    Attributes:
        low_count_threshold: Count below this triggers low population alert
        anomaly_spike_threshold: Percentage increase for anomaly (e.g., 100 = 100%)
        anomaly_min_count: Minimum count to trigger anomaly (avoid false positives)
        decreasing_threshold: Percentage decrease to consider significant (default: -10%)
    """
    low_count_threshold: int = 5
    anomaly_spike_threshold: float = 100.0  # 100% increase
    anomaly_min_count: int = 3
    decreasing_threshold: float = -10.0  # -10% or more


@dataclass
class Alert:
    """
    Alert data structure.
    
    Attributes:
        species: Species name
        alert: Alert type
        severity: Severity level
        count: Current count
        trend: Trend direction
        trend_percentage: Percentage change
        previous_count: Previous period count
        message: Human-readable alert message
        timestamp: When alert was generated
    """
    species: str
    alert: str
    severity: str
    count: int = 0
    trend: str = "unknown"
    trend_percentage: float = 0.0
    previous_count: int = 0
    message: str = ""
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "species": self.species,
            "alert": self.alert,
            "severity": self.severity,
            "count": self.count,
            "trend": self.trend,
            "trend_percentage": round(self.trend_percentage, 2),
            "previous_count": self.previous_count,
            "message": self.message,
            "timestamp": self.timestamp
        }
    
    def to_simple_dict(self) -> Dict[str, str]:
        """Convert to simple format (as requested)."""
        return {
            "species": self.species,
            "alert": self.alert,
            "severity": self.severity
        }


class AnalyticsAlertSystem:
    """
    Alert system built on top of sightings analytics.
    
    Evaluates analytics data and generates alerts based on configurable rules.
    """
    
    def __init__(
        self,
        analytics,  # SightingsAnalytics instance
        config: Optional[AlertConfig] = None
    ):
        """
        Initialize alert system.
        
        Args:
            analytics: SightingsAnalytics instance
            config: Alert configuration (uses defaults if None)
        """
        self.analytics = analytics
        self.config = config or AlertConfig()
    
    def check_alerts(
        self,
        species: str,
        time_window_minutes: int = 60
    ) -> Alert:
        """
        Check alerts for a specific species.
        
        Args:
            species: Species name
            time_window_minutes: Time window for analysis (default: 60)
        
        Returns:
            Alert object with alert type and severity
        """
        # Get analytics data
        analytics_data = self.analytics.analyze_species(
            species,
            time_window_minutes=time_window_minutes
        )
        
        # Extract key metrics
        count = analytics_data.count
        trend = analytics_data.trend
        trend_percentage = analytics_data.trend_percentage
        previous_count = analytics_data.previous_count
        
        # Evaluate alert rules
        alert_type, severity, message = self._evaluate_rules(
            count=count,
            trend=trend,
            trend_percentage=trend_percentage,
            previous_count=previous_count
        )
        
        # Create alert
        from datetime import datetime
        
        return Alert(
            species=species,
            alert=alert_type.value,
            severity=severity.value,
            count=count,
            trend=trend,
            trend_percentage=trend_percentage,
            previous_count=previous_count,
            message=message,
            timestamp=datetime.now().isoformat()
        )
    
    def generate_alerts_for_all_species(
        self,
        time_window_minutes: int = 60,
        min_count: int = 1
    ) -> List[Alert]:
        """
        Generate alerts for all species.
        
        Args:
            time_window_minutes: Time window for analysis (default: 60)
            min_count: Minimum count to include species (default: 1)
        
        Returns:
            List of Alert objects, sorted by severity (high to low)
        """
        # Get all species analytics
        all_analytics = self.analytics.analyze_all_species(
            time_window_minutes=time_window_minutes,
            min_count=min_count
        )
        
        # Generate alerts for each species
        alerts = []
        for analytics_data in all_analytics:
            # Evaluate rules
            alert_type, severity, message = self._evaluate_rules(
                count=analytics_data.count,
                trend=analytics_data.trend,
                trend_percentage=analytics_data.trend_percentage,
                previous_count=analytics_data.previous_count
            )
            
            # Create alert
            from datetime import datetime
            
            alert = Alert(
                species=analytics_data.species,
                alert=alert_type.value,
                severity=severity.value,
                count=analytics_data.count,
                trend=analytics_data.trend,
                trend_percentage=analytics_data.trend_percentage,
                previous_count=analytics_data.previous_count,
                message=message,
                timestamp=datetime.now().isoformat()
            )
            
            alerts.append(alert)
        
        # Sort by severity (high -> medium -> low -> info)
        severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
        alerts.sort(key=lambda a: severity_order.get(a.severity, 99))
        
        return alerts
    
    def get_critical_alerts(
        self,
        time_window_minutes: int = 60,
        severity_threshold: str = "medium"
    ) -> List[Alert]:
        """
        Get only critical alerts (high or medium severity).
        
        Args:
            time_window_minutes: Time window for analysis
            severity_threshold: Minimum severity to include ("high" or "medium")
        
        Returns:
            List of critical alerts
        """
        all_alerts = self.generate_alerts_for_all_species(time_window_minutes)
        
        # Filter by severity
        if severity_threshold == "high":
            return [a for a in all_alerts if a.severity == "high"]
        elif severity_threshold == "medium":
            return [a for a in all_alerts if a.severity in ["high", "medium"]]
        else:
            return all_alerts
    
    def get_alerts_by_type(
        self,
        alert_type: str,
        time_window_minutes: int = 60
    ) -> List[Alert]:
        """
        Get alerts of a specific type.
        
        Args:
            alert_type: Alert type ("population_risk", "low_population", "anomaly")
            time_window_minutes: Time window for analysis
        
        Returns:
            List of alerts matching the type
        """
        all_alerts = self.generate_alerts_for_all_species(time_window_minutes)
        return [a for a in all_alerts if a.alert == alert_type]
    
    def _evaluate_rules(
        self,
        count: int,
        trend: str,
        trend_percentage: float,
        previous_count: int
    ) -> tuple[AlertType, Severity, str]:
        """
        Evaluate alert rules and determine alert type and severity.
        
        Args:
            count: Current count
            trend: Trend direction
            trend_percentage: Percentage change
            previous_count: Previous period count
        
        Returns:
            Tuple of (AlertType, Severity, message)
        """
        # No data
        if count == 0 and previous_count == 0:
            return (
                AlertType.NO_DATA,
                Severity.INFO,
                "No sightings in current or previous period"
            )
        
        # Check for anomaly (sudden spike)
        is_anomaly = self._check_anomaly(count, trend_percentage)
        if is_anomaly:
            severity = Severity.MEDIUM
            message = f"Sudden spike detected: {trend_percentage:+.1f}% increase"
            return AlertType.ANOMALY, severity, message
        
        # Check for decreasing trend
        is_decreasing = trend == "decreasing" and trend_percentage <= self.config.decreasing_threshold
        
        # Check for low count
        is_low_count = count < self.config.low_count_threshold
        
        # Severity logic (as requested):
        # - decreasing + low count → high
        # - only decreasing → medium
        # - only low count → medium
        # - stable → low
        
        if is_decreasing and is_low_count:
            # HIGH: Both decreasing and low count
            return (
                AlertType.POPULATION_RISK,
                Severity.HIGH,
                f"Critical: Population decreasing ({trend_percentage:+.1f}%) and low count ({count})"
            )
        
        elif is_decreasing:
            # MEDIUM: Only decreasing
            return (
                AlertType.POPULATION_RISK,
                Severity.MEDIUM,
                f"Population decreasing: {trend_percentage:+.1f}% decline"
            )
        
        elif is_low_count:
            # MEDIUM: Only low count
            return (
                AlertType.LOW_POPULATION,
                Severity.MEDIUM,
                f"Low population: Only {count} sighting(s) detected"
            )
        
        else:
            # LOW: Stable or increasing
            if trend == "increasing":
                message = f"Population stable/increasing: {trend_percentage:+.1f}%"
            else:
                message = f"Population stable: {count} sighting(s)"
            
            return (
                AlertType.STABLE,
                Severity.LOW,
                message
            )
    
    def _check_anomaly(
        self,
        count: int,
        trend_percentage: float
    ) -> bool:
        """
        Check if current data represents an anomaly (sudden spike).
        
        Args:
            count: Current count
            trend_percentage: Percentage change
        
        Returns:
            True if anomaly detected
        """
        # Must have minimum count to avoid false positives
        if count < self.config.anomaly_min_count:
            return False
        
        # Check for sudden spike
        if trend_percentage >= self.config.anomaly_spike_threshold:
            return True
        
        return False
    
    def update_config(self, config: AlertConfig):
        """
        Update alert configuration.
        
        Args:
            config: New alert configuration
        """
        self.config = config
    
    def get_alert_summary(
        self,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get summary of all alerts.
        
        Args:
            time_window_minutes: Time window for analysis
        
        Returns:
            Dictionary with alert summary statistics
        """
        all_alerts = self.generate_alerts_for_all_species(time_window_minutes)
        
        # Count by severity
        severity_counts = {
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0
        }
        
        for alert in all_alerts:
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
        
        # Count by type
        type_counts = {}
        for alert in all_alerts:
            type_counts[alert.alert] = type_counts.get(alert.alert, 0) + 1
        
        # Get critical species
        critical_species = [
            a.species for a in all_alerts if a.severity in ["high", "medium"]
        ]
        
        return {
            "total_alerts": len(all_alerts),
            "severity_counts": severity_counts,
            "type_counts": type_counts,
            "critical_species": critical_species,
            "time_window_minutes": time_window_minutes
        }


# Convenience functions for quick usage

def check_alerts(
    analytics,
    species: str,
    time_window_minutes: int = 60,
    config: Optional[AlertConfig] = None
) -> Alert:
    """
    Quick function to check alerts for a species.
    
    Args:
        analytics: SightingsAnalytics instance
        species: Species name
        time_window_minutes: Time window for analysis
        config: Alert configuration (optional)
    
    Returns:
        Alert object
    """
    alert_system = AnalyticsAlertSystem(analytics, config)
    return alert_system.check_alerts(species, time_window_minutes)


def generate_alerts_for_all_species(
    analytics,
    time_window_minutes: int = 60,
    config: Optional[AlertConfig] = None
) -> List[Alert]:
    """
    Quick function to generate alerts for all species.
    
    Args:
        analytics: SightingsAnalytics instance
        time_window_minutes: Time window for analysis
        config: Alert configuration (optional)
    
    Returns:
        List of Alert objects
    """
    alert_system = AnalyticsAlertSystem(analytics, config)
    return alert_system.generate_alerts_for_all_species(time_window_minutes)
