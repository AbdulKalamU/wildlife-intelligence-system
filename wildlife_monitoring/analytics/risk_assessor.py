"""
Risk Assessor Module

Assesses risks based on wildlife detection patterns.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum


class RiskLevel(Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAssessor:
    """
    Assesses risks based on wildlife monitoring data.
    
    Attributes:
        risk_rules: Dictionary of risk assessment rules
        endangered_species: List of endangered species
    """
    
    def __init__(self, endangered_species: List[str] = None):
        """
        Initialize risk assessor.
        
        Args:
            endangered_species: List of endangered species names
        """
        self.endangered_species = endangered_species or []
        self.risk_history = []
        self.risk_rules = self._initialize_risk_rules()
    
    def _initialize_risk_rules(self) -> Dict[str, Any]:
        """
        Initialize risk assessment rules.
        
        Returns:
            Dictionary of risk rules
        """
        return {
            "endangered_species_detected": {
                "risk_level": RiskLevel.HIGH,
                "description": "Endangered species detected in area"
            },
            "unusual_activity_pattern": {
                "risk_level": RiskLevel.MEDIUM,
                "description": "Unusual wildlife activity pattern detected"
            },
            "high_population_density": {
                "risk_level": RiskLevel.MEDIUM,
                "description": "High population density detected"
            },
            "predator_near_vulnerable": {
                "risk_level": RiskLevel.HIGH,
                "description": "Predator detected near vulnerable species"
            },
            "habitat_intrusion": {
                "risk_level": RiskLevel.CRITICAL,
                "description": "Human activity detected in protected habitat"
            }
        }
    
    def assess_species_risk(
        self,
        species: str,
        count: int,
        location: tuple = None
    ) -> Dict[str, Any]:
        """
        Assess risk for a detected species.
        
        Args:
            species: Species name
            count: Number of individuals
            location: Optional (x, y) location
            
        Returns:
            Risk assessment dictionary
        """
        risks = []
        overall_risk = RiskLevel.LOW
        
        # Check if endangered
        if species in self.endangered_species:
            risks.append({
                "rule": "endangered_species_detected",
                "level": RiskLevel.HIGH,
                "description": f"Endangered species '{species}' detected"
            })
            overall_risk = RiskLevel.HIGH
        
        # Check population density
        if count > 10:
            risks.append({
                "rule": "high_population_density",
                "level": RiskLevel.MEDIUM,
                "description": f"High density: {count} individuals detected"
            })
            if overall_risk == RiskLevel.LOW:
                overall_risk = RiskLevel.MEDIUM
        
        assessment = {
            "species": species,
            "overall_risk": overall_risk.value,
            "risk_factors": risks,
            "timestamp": datetime.now(),
            "location": location
        }
        
        self.risk_history.append(assessment)
        
        return assessment
    
    def assess_interaction_risk(
        self,
        species_list: List[str],
        proximity: float
    ) -> Dict[str, Any]:
        """
        Assess risk from species interactions.
        
        Args:
            species_list: List of species in proximity
            proximity: Distance between species
            
        Returns:
            Interaction risk assessment
        """
        predators = ["Wolf", "Bear", "Fox"]
        vulnerable = ["Rabbit", "Deer"]
        
        risks = []
        overall_risk = RiskLevel.LOW
        
        # Check for predator-prey proximity
        has_predator = any(s in predators for s in species_list)
        has_vulnerable = any(s in vulnerable for s in species_list)
        
        if has_predator and has_vulnerable and proximity < 50:
            risks.append({
                "rule": "predator_near_vulnerable",
                "level": RiskLevel.HIGH,
                "description": "Predator detected near vulnerable species"
            })
            overall_risk = RiskLevel.HIGH
        
        return {
            "species_involved": species_list,
            "overall_risk": overall_risk.value,
            "risk_factors": risks,
            "proximity": proximity,
            "timestamp": datetime.now()
        }
    
    def get_risk_summary(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get summary of risks in time window.
        
        Args:
            time_window_hours: Time window for summary
            
        Returns:
            Risk summary dictionary
        """
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        recent_risks = [
            r for r in self.risk_history
            if r["timestamp"] >= cutoff_time
        ]
        
        if not recent_risks:
            return {
                "total_assessments": 0,
                "risk_distribution": {},
                "highest_risk": RiskLevel.LOW.value
            }
        
        # Count by risk level
        risk_counts = {
            RiskLevel.LOW.value: 0,
            RiskLevel.MEDIUM.value: 0,
            RiskLevel.HIGH.value: 0,
            RiskLevel.CRITICAL.value: 0
        }
        
        for risk in recent_risks:
            level = risk["overall_risk"]
            risk_counts[level] += 1
        
        # Determine highest risk
        if risk_counts[RiskLevel.CRITICAL.value] > 0:
            highest = RiskLevel.CRITICAL.value
        elif risk_counts[RiskLevel.HIGH.value] > 0:
            highest = RiskLevel.HIGH.value
        elif risk_counts[RiskLevel.MEDIUM.value] > 0:
            highest = RiskLevel.MEDIUM.value
        else:
            highest = RiskLevel.LOW.value
        
        return {
            "total_assessments": len(recent_risks),
            "risk_distribution": risk_counts,
            "highest_risk": highest,
            "time_window_hours": time_window_hours
        }
