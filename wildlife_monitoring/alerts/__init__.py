"""
Alerts Module

Alert generation and management for wildlife monitoring events.
"""

from .alert_generator import AlertGenerator
from .alert_rules import AlertRule, AlertRuleEngine
from .analytics_alerts import (
    AnalyticsAlertSystem,
    Alert,
    AlertConfig,
    AlertType,
    Severity,
    check_alerts,
    generate_alerts_for_all_species
)

__all__ = [
    "AlertGenerator",
    "AlertRule",
    "AlertRuleEngine",
    "AnalyticsAlertSystem",
    "Alert",
    "AlertConfig",
    "AlertType",
    "Severity",
    "check_alerts",
    "generate_alerts_for_all_species"
]
