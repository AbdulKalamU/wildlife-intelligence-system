#!/usr/bin/env python
"""
Quick Alert System Demo

Demonstrates the exact output format requested:
{"species": "tiger", "alert": "population_risk", "severity": "high"}
"""

from datetime import datetime, timedelta
from wildlife_monitoring.database import WildlifeDatabase
from wildlife_monitoring.analytics import SightingsAnalytics
from wildlife_monitoring.alerts import check_alerts, generate_alerts_for_all_species


def main():
    print("\n" + "=" * 70)
    print("WILDLIFE ALERT SYSTEM - QUICK DEMO")
    print("=" * 70)
    
    # Initialize database
    db = WildlifeDatabase("quick_alert_demo.db")
    db.clear_all_sightings()
    
    # Create sample data
    print("\n📝 Creating sample data...")
    now = datetime.now()
    
    # Tiger: Decreasing + low count (HIGH)
    for i in range(10):
        db.insert_sighting(
            species="tiger",
            confidence=0.85,
            track_id=100 + i,
            frame_number=i,
            timestamp=now - timedelta(minutes=120 - i * 5)
        )
    for i in range(3):
        db.insert_sighting(
            species="tiger",
            confidence=0.87,
            track_id=200 + i,
            frame_number=100 + i,
            timestamp=now - timedelta(minutes=60 - i * 15)
        )
    
    # Deer: Stable (LOW)
    for i in range(10):
        db.insert_sighting(
            species="deer",
            confidence=0.80,
            track_id=300 + i,
            frame_number=i,
            timestamp=now - timedelta(minutes=115 - i * 8)
        )
    for i in range(10):
        db.insert_sighting(
            species="deer",
            confidence=0.82,
            track_id=400 + i,
            frame_number=100 + i,
            timestamp=now - timedelta(minutes=55 - i * 5)
        )
    
    print("   ✅ Created sample data")
    print("      Tiger: 10 → 3 sightings (decreasing + low count)")
    print("      Deer: 10 → 10 sightings (stable)")
    
    # Initialize analytics
    analytics = SightingsAnalytics("quick_alert_demo.db")
    
    # Check single species
    print("\n🐅 Checking Tiger Alert:")
    tiger_alert = check_alerts(analytics, "tiger", time_window_minutes=60)
    
    print("\n📊 OUTPUT (as requested):")
    print("-" * 70)
    print(tiger_alert.to_simple_dict())
    print("-" * 70)
    
    # Check all species
    print("\n📋 Checking All Species:")
    all_alerts = generate_alerts_for_all_species(analytics, time_window_minutes=60)
    
    print("\n📊 ALL ALERTS (as requested):")
    print("-" * 70)
    for alert in all_alerts:
        print(alert.to_simple_dict())
    print("-" * 70)
    
    # Show details
    print("\n📈 Alert Details:")
    for alert in all_alerts:
        severity_symbol = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        symbol = severity_symbol.get(alert.severity, "")
        
        print(f"\n   {symbol} {alert.species.upper()}")
        print(f"      Alert: {alert.alert}")
        print(f"      Severity: {alert.severity}")
        print(f"      Count: {alert.count} (previous: {alert.previous_count})")
        print(f"      Trend: {alert.trend} ({alert.trend_percentage:+.1f}%)")
        print(f"      Message: {alert.message}")
    
    # Clean up
    analytics.close()
    db.close()
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
