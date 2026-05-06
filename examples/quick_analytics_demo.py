#!/usr/bin/env python
"""
Quick Analytics Demo

Demonstrates the exact output format requested:
{"species": "tiger", "count": 5, "trend": "decreasing"}
"""

from datetime import datetime, timedelta
from wildlife_monitoring.database import WildlifeDatabase
from wildlife_monitoring.analytics import SightingsAnalytics


def main():
    print("\n" + "=" * 70)
    print("WILDLIFE SIGHTINGS ANALYTICS - QUICK DEMO")
    print("=" * 70)
    
    # Initialize database
    db = WildlifeDatabase("quick_demo.db")
    db.clear_all_sightings()
    
    # Create sample data
    print("\n📝 Creating sample data...")
    now = datetime.now()
    
    # Previous period (120-60 min ago): 8 tigers
    for i in range(8):
        db.insert_sighting(
            species="tiger",
            confidence=0.85,
            track_id=100 + i,
            frame_number=i,
            timestamp=now - timedelta(minutes=120 - i * 5)
        )
    
    # Current period (60-0 min ago): 5 tigers (DECREASING)
    for i in range(5):
        db.insert_sighting(
            species="tiger",
            confidence=0.87,
            track_id=200 + i,
            frame_number=100 + i,
            timestamp=now - timedelta(minutes=60 - i * 10)
        )
    
    print("   ✅ Created 13 tiger sightings")
    print("      Previous period: 8 sightings")
    print("      Current period: 5 sightings")
    
    # Initialize analytics
    analytics = SightingsAnalytics("quick_demo.db")
    
    # Analyze tiger
    print("\n🐅 Analyzing tiger (last 60 minutes)...")
    tiger = analytics.analyze_species("tiger", time_window_minutes=60)
    
    # Output in requested format
    print("\n📊 OUTPUT (as requested):")
    print("-" * 70)
    
    output = {
        "species": tiger.species,
        "count": tiger.count,
        "trend": tiger.trend
    }
    
    print(output)
    
    print("-" * 70)
    
    # Additional details
    print("\n📈 Additional Details:")
    print(f"   Previous count: {tiger.previous_count}")
    print(f"   Change: {tiger.trend_percentage:+.1f}%")
    print(f"   Avg confidence: {tiger.avg_confidence:.2f}")
    print(f"   Unique tracks: {tiger.unique_tracks}")
    
    # Clean up
    analytics.close()
    db.close()
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
