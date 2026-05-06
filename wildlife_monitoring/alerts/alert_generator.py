"""
Alert Generator Module

Generates alerts based on detection and analytics data.
"""

from typing import Dict, List, Any
from datetime import datetime
from enum import Enum
import uuid


class AlertPriority(Enum):
    """Alert priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertGenerator:
    """
    Generates and manages alerts for wildlife monitoring events.
    
    Attributes:
        alerts: List of generated alerts
        alert_history: Historical alerts
    """
    
    def __init__(self):
        """Initialize alert generator."""
        self.alerts = []
        self.alert_history = []
        self.alert_callbacks = []
    
    def generate_alert(
        self,
        alert_type: str,
        priority: AlertPriority,
        message: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a new alert.
        
        Args:
            alert_type: Type of alert (e.g., "endangered_species", "unusual_activity")
            priority: Alert priority level
            message: Human-readable alert message
            metadata: Additional alert metadata
            
        Returns:
            Generated alert dictionary
        """
        alert = {
            "id": str(uuid.uuid4()),
            "type": alert_type,
            "priority": priority.value,
            "message": message,
            "timestamp": datetime.now(),
            "acknowledged": False,
            "metadata": metadata or {}
        }
        
        self.alerts.append(alert)
        self.alert_history.append(alert)
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            callback(alert)
        
        return alert
    
    def generate_species_alert(
        self,
        species: str,
        count: int,
        location: tuple = None,
        is_endangered: bool = False
    ) -> Dict[str, Any]:
        """
        Generate alert for species detection.
        
        Args:
            species: Species name
            count: Number of individuals
            location: Optional (x, y) location
            is_endangered: Whether species is endangered
            
        Returns:
            Generated alert
        """
        if is_endangered:
            priority = AlertPriority.HIGH
            alert_type = "endangered_species_detected"
            message = f"ENDANGERED: {species} detected ({count} individual{'s' if count > 1 else ''})"
        else:
            priority = AlertPriority.LOW
            alert_type = "species_detected"
            message = f"{species} detected ({count} individual{'s' if count > 1 else ''})"
        
        metadata = {
            "species": species,
            "count": count,
            "location": location,
            "is_endangered": is_endangered
        }
        
        return self.generate_alert(alert_type, priority, message, metadata)
    
    def generate_trend_alert(
        self,
        species: str,
        trend: str,
        change_rate: float
    ) -> Dict[str, Any]:
        """
        Generate alert for trend changes.
        
        Args:
            species: Species name
            trend: Trend direction ("increasing", "decreasing", "stable")
            change_rate: Rate of change
            
        Returns:
            Generated alert
        """
        if trend == "decreasing" and change_rate < -0.5:
            priority = AlertPriority.MEDIUM
            message = f"ALERT: {species} population declining rapidly (rate: {change_rate:.2f})"
        elif trend == "increasing" and change_rate > 1.0:
            priority = AlertPriority.LOW
            message = f"INFO: {species} population increasing (rate: {change_rate:.2f})"
        else:
            priority = AlertPriority.LOW
            message = f"INFO: {species} population {trend}"
        
        metadata = {
            "species": species,
            "trend": trend,
            "change_rate": change_rate
        }
        
        return self.generate_alert("trend_change", priority, message, metadata)
    
    def generate_risk_alert(
        self,
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate alert from risk assessment.
        
        Args:
            risk_assessment: Risk assessment dictionary
            
        Returns:
            Generated alert
        """
        risk_level = risk_assessment.get("overall_risk", "low")
        
        if risk_level == "critical":
            priority = AlertPriority.CRITICAL
        elif risk_level == "high":
            priority = AlertPriority.HIGH
        elif risk_level == "medium":
            priority = AlertPriority.MEDIUM
        else:
            priority = AlertPriority.LOW
        
        risk_factors = risk_assessment.get("risk_factors", [])
        factor_descriptions = [f["description"] for f in risk_factors]
        
        message = f"Risk Level: {risk_level.upper()}"
        if factor_descriptions:
            message += f" - {'; '.join(factor_descriptions)}"
        
        return self.generate_alert("risk_assessment", priority, message, risk_assessment)
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Mark an alert as acknowledged.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if acknowledged, False if not found
        """
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now()
                return True
        return False
    
    def get_active_alerts(self, priority: AlertPriority = None) -> List[Dict[str, Any]]:
        """
        Get active (unacknowledged) alerts.
        
        Args:
            priority: Optional filter by priority
            
        Returns:
            List of active alerts
        """
        active = [a for a in self.alerts if not a["acknowledged"]]
        
        if priority:
            active = [a for a in active if a["priority"] == priority.value]
        
        return active
    
    def clear_acknowledged_alerts(self):
        """Remove acknowledged alerts from active list."""
        self.alerts = [a for a in self.alerts if not a["acknowledged"]]
    
    def register_callback(self, callback):
        """
        Register a callback function to be called when alerts are generated.
        
        Args:
            callback: Function that takes alert dictionary as parameter
        """
        self.alert_callbacks.append(callback)
