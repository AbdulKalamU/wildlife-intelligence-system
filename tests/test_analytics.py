"""
Tests for Analytics Module
"""

import pytest
from datetime import datetime
from wildlife_monitoring.analytics import TrendAnalyzer, RiskAssessor, StatisticsCalculator


class TestTrendAnalyzer:
    """Tests for TrendAnalyzer class."""
    
    def test_trend_analyzer_initialization(self):
        """Test trend analyzer initialization."""
        analyzer = TrendAnalyzer()
        assert len(analyzer.detection_history) == 0
        assert len(analyzer.species_counts) == 0
    
    def test_add_detection_data(self):
        """Test adding detection data."""
        analyzer = TrendAnalyzer()
        analyzer.add_detection_data(datetime.now(), "deer", 3)
        
        assert len(analyzer.detection_history) == 1
        assert "deer" in analyzer.species_counts


class TestRiskAssessor:
    """Tests for RiskAssessor class."""
    
    def test_risk_assessor_initialization(self):
        """Test risk assessor initialization."""
        assessor = RiskAssessor(endangered_species=["wolf", "bear"])
        assert "wolf" in assessor.endangered_species
        assert "bear" in assessor.endangered_species
    
    def test_assess_species_risk(self):
        """Test species risk assessment."""
        assessor = RiskAssessor(endangered_species=["wolf"])
        result = assessor.assess_species_risk("wolf", 2)
        
        assert "overall_risk" in result
        assert result["overall_risk"] == "high"


class TestStatisticsCalculator:
    """Tests for StatisticsCalculator class."""
    
    def test_calculate_basic_stats(self):
        """Test basic statistics calculation."""
        data = [1, 2, 3, 4, 5]
        stats = StatisticsCalculator.calculate_basic_stats(data)
        
        assert stats["mean"] == 3.0
        assert stats["median"] == 3.0
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["count"] == 5
    
    def test_calculate_percentiles(self):
        """Test percentile calculation."""
        data = list(range(1, 101))
        percentiles = StatisticsCalculator.calculate_percentiles(data, [25, 50, 75])
        
        assert 25 in percentiles
        assert 50 in percentiles
        assert 75 in percentiles
