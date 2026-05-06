#!/usr/bin/env python
"""
Example: Analytics-Based Alert System

Demonstrates the alert system built on top of sightings analytics.

Features:
- Population risk alerts (decreasing trends)
- Low population alerts (below threshold)
- Anomaly alerts (sudden spikes)
- Configurable severity levels
- Rule-based triggering
"""

from datetime import datetime, timedelta
from wildlife_monitoring.database import WildlifeDatabase
from wildlife_monitoring.analytics import SightingsAnalytics
from wildlife_monitoring.alerts import (
    AnalyticsAlertSystem,
    AlertConfig,
    check_alerts,
    generate_alerts_for_all_species
)


def setup_test_data(db: WildlifeDatabase):
    """
    Create test data with various alert scenarios.
    
    Scenarios:
    - Tiger: Decreasing + low count (HIGH severity)
    - Deer: Only decreasing (MEDIUM severity)
    - Bear: Stable (LOW severity)
    - Fox: Sudden spike (ANOMALY)
    - Wolf: Low count only (MEDIUM severity)
    """
    print("\n📝 Setting up test data with alert scenarios...")
    
    now = datetime.now()
    
    # SCENARIO 1: Tiger - Decreasing + Low Count (HIGH)
    print("   Creating Tiger scenario (HIGH: decreasing + low count)...")
    # Previous: 10 sightings
    for i in range(10):
        db.insert_sighting(
            species="tiger",
            confidence=0.85,
            track_id=100 + i,
            frame_number=i,
            timestamp=now - timedelta(minutes=120 - i * 5)
        )
    # Current: 3 sightings (below threshold of 5)
    for i in range(3):
        db.insert_sighting(
            species="tiger",
            confidence=0.87,
            track_id=200 + i,
            frame_number=100 + i,
            timestamp=now - timedelta(minutes=60 - i * 15)
        )
    
    # SCENARIO 2: Deer - Only Decreasing (MEDIUM)
    print("   Creating Deer scenario (MEDIUM: only decreasing)...")
    # Previous: 15 sightings
    for i in range(15):
        db.insert_sighting(
            species="deer",
            confidence=0.80,
            track_id=300 + i,
            frame_number=i,
            timestamp=now - timedelta(minutes=115 - i * 5)
        )
    # Current: 8 sightings (above threshold but decreasing)
    for i in range(8):
        db.insert_sighting(
            species="deer",
            confidence=0.82,
            track_id=400 + i,
            frame_number=100 + i,
            timestamp=now - timedelta(minutes=55 - i * 5)
        )
    
    # SCENARIO 3: Bear - Stable (LOW)
    print("   Creating Bear scenario (LOW: stable)...")
    # Previous: 10 sightings
    for i in range(10):
        db.insert_sighting(
            species="bear",
            confidence=0.88,
            track_id=500 + i,
            frame_number=i,
            timestamp=now - timedelta(minutes=110 - i * 8)
        )
    # Current: 10 sightings (stable)
    for i in range(10):
        db.insert_sighting(
            species="bear",
            confidence=0.89,
            track_id=600 + i,
            frame_number=100 + i,
            timestamp=now - timedelta(minutes=50 - i * 4)
        )
    
    # SCENARIO 4: Fox - Sudden Spike (ANOMALY)
    print("   Creating Fox scenario (ANOMALY: sudden spike)...")
    # Previous: 2 sightings
    for i in range(2):
        db.insert_sighting(
            species="fox",
            confidence=0.75,
            track_id=700 + i,
            frame_number=i,
            timestamp=now - timedelta(minutes=100 - i * 20)
        )
    # Current: 10 sightings (500% increase!)
    for i in range(10):
        db.insert_sighting(
            species="fox",
            confidence=0.78,
            track_id=800 + i,
            frame_number=100 + i,
            timestamp=now - timedelta(minutes=45 - i * 4)
        )
    
    # SCENARIO 5: Wolf - Low Count Only (MEDIUM)
    print("   Creating Wolf scenario (MEDIUM: low count only)...")
    # Previous: 3 sightings
    for i in range(3):
        db.insert_sighting(
            species="wolf",
            confidence=0.82,
            track_id=900 + i,
            frame_number=i,
            timestamp=now - timedelta(minutes=105 - i * 15)
        )
    # Current: 4 sightings (low but stable)
    for i in range(4):
        db.insert_sighting(
            species="wolf",
            confidence=0.84,
            track_id=1000 + i,
            frame_number=100 + i,
            timestamp=now - timedelta(minutes=50 - i * 10)
        )
    
    print("   ✅ Test data created with 5 alert scenarios")


def example_1_check_single_species():
    """
    Example 1: Check alerts for a single species.
    """
    print("\n" + "=" * 70)
    print("Example 1: Check Alerts for Single Species")
    print("=" * 70)
    
    # Initialize
    db = WildlifeDatabase("alert_test.db")
    db.clear_all_sightings()
    setup_test_data(db)
    
    analytics = SightingsAnalytics("alert_test.db")
    alert_system = AnalyticsAlertSystem(analytics)
    
    # Check tiger (HIGH severity)
    print("\n🐅 Checking Tiger Alerts:")
    tiger_alert = alert_system.check_alerts("tiger", time_window_minutes=60)
    
    print(f"   Species: {tiger_alert.species}")
    print(f"   Alert: {tiger_alert.alert}")
    print(f"   Severity: {tiger_alert.severity}")
    print(f"   Count: {tiger_alert.count}")
    print(f"   Trend: {tiger_alert.trend} ({tiger_alert.trend_percentage:+.1f}%)")
    print(f"   Message: {tiger_alert.message}")
    
    # Output in requested format
    print("\n📊 OUTPUT (as requested):")
    print(tiger_alert.to_simple_dict())
    
    analytics.close()
    db.close()
    print()


def example_2_all_species_alerts():
    """
    Example 2: Generate alerts for all species.
    """
    print("=" * 70)
    print("Example 2: Generate Alerts for All Species")
    print("=" * 70)
    
    analytics = SightingsAnalytics("alert_test.db")
    alert_system = AnalyticsAlertSystem(analytics)
    
    # Generate all alerts
    print("\n🚨 Generating alerts for all species...")
    all_alerts = alert_system.generate_alerts_for_all_species(time_window_minutes=60)
    
    print(f"\n   Found {len(all_alerts)} alert(s):\n")
    
    for alert in all_alerts:
        severity_symbol = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢",
            "info": "ℹ️"
        }.get(alert.severity, "")
        
        print(f"   {severity_symbol} {alert.species.upper()}")
        print(f"      Alert: {alert.alert}")
        print(f"      Severity: {alert.severity}")
        print(f"      Count: {alert.count} (previous: {alert.previous_count})")
        print(f"      Trend: {alert.trend} ({alert.trend_percentage:+.1f}%)")
        print(f"      Message: {alert.message}")
        print()
    
    analytics.close()
    print()


def example_3_simple_format_output():
    """
    Example 3: Simple format output (as requested).
    """
    print("=" * 70)
    print("Example 3: Simple Format Output")
    print("=" * 70)
    
    analytics = SightingsAnalytics("alert_test.db")
    
    # Use convenience function
    print("\n📋 Using convenience function check_alerts():")
    tiger_alert = check_alerts(analytics, "tiger", time_window_minutes=60)
    
    print("\n   Simple format:")
    print(f"   {tiger_alert.to_simple_dict()}")
    
    # Generate all alerts
    print("\n📋 Using convenience function generate_alerts_for_all_species():")
    all_alerts = generate_alerts_for_all_species(analytics, time_window_minutes=60)
    
    print("\n   All alerts in simple format:")
    for alert in all_alerts:
        print(f"   {alert.to_simple_dict()}")
    
    analytics.close()
    print()


def example_4_severity_filtering():
    """
    Example 4: Filter alerts by severity.
    """
    print("=" * 70)
    print("Example 4: Filter Alerts by Severity")
    print("=" * 70)
    
    analytics = SightingsAnalytics("alert_test.db")
    alert_system = AnalyticsAlertSystem(analytics)
    
    # Get only critical alerts (high severity)
    print("\n🔴 Critical Alerts (HIGH severity only):")
    critical_alerts = alert_system.get_critical_alerts(
        time_window_minutes=60,
        severity_threshold="high"
    )
    
    if critical_alerts:
        for alert in critical_alerts:
            print(f"   {alert.species}: {alert.alert} - {alert.message}")
    else:
        print("   No critical alerts")
    
    # Get high and medium alerts
    print("\n🟡 Important Alerts (HIGH + MEDIUM severity):")
    important_alerts = alert_system.get_critical_alerts(
        time_window_minutes=60,
        severity_threshold="medium"
    )
    
    for alert in important_alerts:
        print(f"   {alert.species}: {alert.severity} - {alert.alert}")
    
    analytics.close()
    print()


def example_5_alert_types():
    """
    Example 5: Filter alerts by type.
    """
    print("=" * 70)
    print("Example 5: Filter Alerts by Type")
    print("=" * 70)
    
    analytics = SightingsAnalytics("alert_test.db")
    alert_system = AnalyticsAlertSystem(analytics)
    
    # Population risk alerts
    print("\n📉 Population Risk Alerts:")
    risk_alerts = alert_system.get_alerts_by_type(
        "population_risk",
        time_window_minutes=60
    )
    for alert in risk_alerts:
        print(f"   {alert.species}: {alert.severity} - {alert.trend_percentage:+.1f}%")
    
    # Low population alerts
    print("\n⚠️  Low Population Alerts:")
    low_pop_alerts = alert_system.get_alerts_by_type(
        "low_population",
        time_window_minutes=60
    )
    for alert in low_pop_alerts:
        print(f"   {alert.species}: {alert.count} sighting(s)")
    
    # Anomaly alerts
    print("\n🚀 Anomaly Alerts (Sudden Spikes):")
    anomaly_alerts = alert_system.get_alerts_by_type(
        "anomaly",
        time_window_minutes=60
    )
    for alert in anomaly_alerts:
        print(f"   {alert.species}: {alert.trend_percentage:+.1f}% increase")
    
    analytics.close()
    print()


def example_6_custom_configuration():
    """
    Example 6: Custom alert configuration.
    """
    print("=" * 70)
    print("Example 6: Custom Alert Configuration")
    print("=" * 70)
    
    analytics = SightingsAnalytics("alert_test.db")
    
    # Custom configuration
    custom_config = AlertConfig(
        low_count_threshold=8,  # Stricter threshold
        anomaly_spike_threshold=150.0,  # 150% increase for anomaly
        anomaly_min_count=5,  # Higher minimum
        decreasing_threshold=-15.0  # -15% or more
    )
    
    print("\n⚙️  Custom Configuration:")
    print(f"   Low count threshold: {custom_config.low_count_threshold}")
    print(f"   Anomaly spike threshold: {custom_config.anomaly_spike_threshold}%")
    print(f"   Anomaly min count: {custom_config.anomaly_min_count}")
    print(f"   Decreasing threshold: {custom_config.decreasing_threshold}%")
    
    # Create alert system with custom config
    alert_system = AnalyticsAlertSystem(analytics, custom_config)
    
    print("\n🚨 Alerts with custom configuration:")
    all_alerts = alert_system.generate_alerts_for_all_species(time_window_minutes=60)
    
    for alert in all_alerts:
        print(f"   {alert.species}: {alert.severity} - {alert.alert}")
    
    analytics.close()
    print()


def example_7_alert_summary():
    """
    Example 7: Alert summary statistics.
    """
    print("=" * 70)
    print("Example 7: Alert Summary Statistics")
    print("=" * 70)
    
    analytics = SightingsAnalytics("alert_test.db")
    alert_system = AnalyticsAlertSystem(analytics)
    
    # Get summary
    print("\n📊 Alert Summary:")
    summary = alert_system.get_alert_summary(time_window_minutes=60)
    
    print(f"\n   Time Window: {summary['time_window_minutes']} minutes")
    print(f"   Total Alerts: {summary['total_alerts']}")
    
    print("\n   Severity Breakdown:")
    for severity, count in summary['severity_counts'].items():
        print(f"      {severity}: {count}")
    
    print("\n   Alert Type Breakdown:")
    for alert_type, count in summary['type_counts'].items():
        print(f"      {alert_type}: {count}")
    
    print(f"\n   Critical Species: {', '.join(summary['critical_species'])}")
    
    analytics.close()
    print()


def example_8_json_output():
    """
    Example 8: JSON-ready output.
    """
    print("=" * 70)
    print("Example 8: JSON Output Format")
    print("=" * 70)
    
    import json
    
    analytics = SightingsAnalytics("alert_test.db")
    all_alerts = generate_alerts_for_all_species(analytics, time_window_minutes=60)
    
    # Simple format
    print("\n📄 Simple Format (as requested):")
    simple_output = [alert.to_simple_dict() for alert in all_alerts]
    print(json.dumps(simple_output, indent=2))
    
    # Full format
    print("\n📄 Full Format (with details):")
    full_output = [alert.to_dict() for alert in all_alerts]
    print(json.dumps(full_output[:2], indent=2))  # Show first 2 for brevity
    
    analytics.close()
    print()


def main():
    """Run all examples."""
    print("\n🚨 Wildlife Alert System Examples\n")
    
    # Run examples
    example_1_check_single_species()
    example_2_all_species_alerts()
    example_3_simple_format_output()
    example_4_severity_filtering()
    example_5_alert_types()
    example_6_custom_configuration()
    example_7_alert_summary()
    example_8_json_output()
    
    print("=" * 70)
    print("Examples complete!")
    print("=" * 70)
    print("\n✅ Alert System Features:")
    print("   ✓ Population risk alerts (decreasing trends)")
    print("   ✓ Low population alerts (below threshold)")
    print("   ✓ Anomaly alerts (sudden spikes)")
    print("   ✓ Configurable severity levels")
    print("   ✓ Rule-based triggering")
    print("   ✓ Simple and full output formats")
    print("   ✓ Filtering by severity and type")
    print()


if __name__ == "__main__":
    main()
