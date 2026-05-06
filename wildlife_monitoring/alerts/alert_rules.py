"""
Alert Rules Module

Defines and manages alert rules for wildlife monitoring.
"""

from typing import Dict, List, Any, Callable
from dataclasses import dataclass


@dataclass
class AlertRule:
    """
    Represents an alert rule.
    
    Attributes:
        name: Rule name
        description: Rule description
        condition: Function that evaluates the rule
        priority: Alert priority if triggered
        enabled: Whether rule is active
    """
    name: str
    description: str
    condition: Callable[[Dict[str, Any]], bool]
    priority: str
    enabled: bool = True


class AlertRuleEngine:
    """
    Manages and evaluates alert rules.
    
    Attributes:
        rules: Dictionary of alert rules
    """
    
    def __init__(self):
        """Initialize alert rule engine."""
        self.rules: Dict[str, AlertRule] = {}
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        
        # Endangered species rule
        self.add_rule(AlertRule(
            name="endangered_species",
            description="Alert when endangered species is detected",
            condition=lambda data: data.get("is_endangered", False),
            priority="high"
        ))
        
        # High population density rule
        self.add_rule(AlertRule(
            name="high_density",
            description="Alert when population density exceeds threshold",
            condition=lambda data: data.get("count", 0) > 10,
            priority="medium"
        ))
        
        # Rapid population decline rule
        self.add_rule(AlertRule(
            name="rapid_decline",
            description="Alert when population is declining rapidly",
            condition=lambda data: (
                data.get("trend", "") == "decreasing" and
                data.get("change_rate", 0) < -0.5
            ),
            priority="high"
        ))
        
        # Unusual activity time rule
        self.add_rule(AlertRule(
            name="unusual_activity_time",
            description="Alert when activity detected at unusual hours",
            condition=lambda data: data.get("hour", 12) in [0, 1, 2, 3, 4],
            priority="low"
        ))
        
        # Predator proximity rule
        self.add_rule(AlertRule(
            name="predator_proximity",
            description="Alert when predator is near vulnerable species",
            condition=lambda data: (
                data.get("has_predator", False) and
                data.get("has_vulnerable", False) and
                data.get("proximity", 100) < 50
            ),
            priority="high"
        ))
    
    def add_rule(self, rule: AlertRule):
        """
        Add a new alert rule.
        
        Args:
            rule: AlertRule instance
        """
        self.rules[rule.name] = rule
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove an alert rule.
        
        Args:
            rule_name: Name of rule to remove
            
        Returns:
            True if removed, False if not found
        """
        if rule_name in self.rules:
            del self.rules[rule_name]
            return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """
        Enable a rule.
        
        Args:
            rule_name: Name of rule to enable
            
        Returns:
            True if enabled, False if not found
        """
        if rule_name in self.rules:
            self.rules[rule_name].enabled = True
            return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """
        Disable a rule.
        
        Args:
            rule_name: Name of rule to disable
            
        Returns:
            True if disabled, False if not found
        """
        if rule_name in self.rules:
            self.rules[rule_name].enabled = False
            return True
        return False
    
    def evaluate(self, data: Dict[str, Any]) -> List[AlertRule]:
        """
        Evaluate all enabled rules against data.
        
        Args:
            data: Data dictionary to evaluate
            
        Returns:
            List of triggered rules
        """
        triggered_rules = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            try:
                if rule.condition(data):
                    triggered_rules.append(rule)
            except Exception as e:
                # Log error but continue evaluating other rules
                print(f"Error evaluating rule '{rule.name}': {e}")
        
        return triggered_rules
    
    def get_rule(self, rule_name: str) -> AlertRule:
        """
        Get a specific rule.
        
        Args:
            rule_name: Name of rule
            
        Returns:
            AlertRule instance or None
        """
        return self.rules.get(rule_name)
    
    def get_all_rules(self) -> List[AlertRule]:
        """
        Get all rules.
        
        Returns:
            List of all AlertRule instances
        """
        return list(self.rules.values())
    
    def get_enabled_rules(self) -> List[AlertRule]:
        """
        Get all enabled rules.
        
        Returns:
            List of enabled AlertRule instances
        """
        return [rule for rule in self.rules.values() if rule.enabled]
