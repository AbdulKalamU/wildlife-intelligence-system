"""
Tests for Alerts Module
"""

import pytest
from wildlife_monitoring.alerts import AlertGenerator, AlertRule, AlertRuleEngine, AlertPriority


class TestAlertGenerator:
    """Tests for AlertGenerator class."""
    
    def test_alert_generator_initialization(self):
        """Test alert generator initialization."""
        generator = AlertGenerator()
        assert len(generator.alerts) == 0
        assert len(generator.alert_history) == 0
    
    def test_generate_alert(self):
        """Test alert generation."""
        generator = AlertGenerator()
        alert = generator.generate_alert(
            "test_alert",
            AlertPriority.HIGH,
            "Test alert message"
        )
        
        assert alert["type"] == "test_alert"
        assert alert["priority"] == "high"
        assert alert["message"] == "Test alert message"
        assert len(generator.alerts) == 1
    
    def test_acknowledge_alert(self):
        """Test alert acknowledgment."""
        generator = AlertGenerator()
        alert = generator.generate_alert(
            "test_alert",
            AlertPriority.LOW,
            "Test message"
        )
        
        result = generator.acknowledge_alert(alert["id"])
        assert result is True
        assert alert["acknowledged"] is True
    
    def test_get_active_alerts(self):
        """Test getting active alerts."""
        generator = AlertGenerator()
        generator.generate_alert("alert1", AlertPriority.HIGH, "Message 1")
        generator.generate_alert("alert2", AlertPriority.LOW, "Message 2")
        
        active = generator.get_active_alerts()
        assert len(active) == 2


class TestAlertRuleEngine:
    """Tests for AlertRuleEngine class."""
    
    def test_rule_engine_initialization(self):
        """Test rule engine initialization."""
        engine = AlertRuleEngine()
        assert len(engine.rules) > 0
    
    def test_add_rule(self):
        """Test adding a rule."""
        engine = AlertRuleEngine()
        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            condition=lambda data: data.get("test", False),
            priority="medium"
        )
        
        engine.add_rule(rule)
        assert "test_rule" in engine.rules
    
    def test_evaluate_rules(self):
        """Test rule evaluation."""
        engine = AlertRuleEngine()
        data = {"is_endangered": True}
        
        triggered = engine.evaluate(data)
        assert len(triggered) > 0
