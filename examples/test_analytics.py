#!/usr/bin/env python
"""
Example: Sightings Analytics

Demonstrates analytics module for analyzing stored wildlife sightings.

Features:
- Species count analysis
- Trend detection (increasing/decreasing/stable)
- Time-based grouping
- Comparative statistics
- Hourly breakdowns
"""

import time
from datetime import datetime, timedelta
from wildlife_monitoring.database import WildlifeDatabase
from wildlife_monitoring.analytics import SightingsAnalytics


def setup_test_data(db: WildlifeDatabase):
    """
    Create test data with realistic patterns.
    
    Simulates:
    - Tiger sightings decreasing over time
    - Deer sightings increasing over time
    - Bear sightings stable
    """
    print("\n📝 Setting up test data...")
    
    now = datetime.now()
    
    # Period 1: 120-60 minutes ago (previous period)
    print("   Creating previous period data (120-60 min ago)...")
    
    # Tigers: 8 sightings (will decrease)
    for i in range(8):
        timestamp = now - timedelta(minutes=120 - i * 5)
        db.insert_sighting(
            species="tiger",
            confidence=0.85 + i * 0.01,
            track_id=100 + i,
            frame_number=i,
            timestamp=timestamp
        )
    
    # Deer: 3 sightings (will increase)
    for i in range(3):
        timestamp = now - timedelta(minutes=115 - i * 10)
        db.insert_sighting(
            species="deer",
            confidence=0.80 + i * 0.02,
            track_id=200 + i,
            frame_number=i,
            timestamp=timestamp
        )
    
    # Bear: 5 sightings (will stay stable)
    for i in range(5):
        timestamp = now - timedelta(minutes=110 - i * 8)
        db.insert_sighting(
            species="bear",
            confidence=0.88 + i * 0.01,
            track_id=300 + i,
            frame_number=i,
            timestamp=timestamp
        )
    
    # Period 2: 60-0 minutes ago (current period)
    print("   Creating current period data (60-0 min ago)...")
    
    # Tigers: 3 sightings (DECREASING from 8)
    for i in range(3):
        timestamp = now - timedelta(minutes=60 - i * 15)
        db.insert_sighting(
            species="tiger",
            confidence=0.87 + i * 0.01,
            track_id=400 + i,
            frame_number=100 + i,
            timestamp=timestamp
        )
    
    # Deer: 9 sightings (INCREASING from 3)
    for i in range(9):
        timestamp = now - timedelta(minutes=55 - i * 5)
        db.insert_sighting(
            species="deer",
            confidence=0.82 + i * 0.01,
            track_id=500 + i,
            frame_number=100 + i,
            timestamp=timestamp
        )
    
    # Bear: 5 sightings (STABLE at 5)
    for i in range(5):
        timestamp = now - timedelta(minutes=50 - i * 8)
        db.insert_sighting(
            species="bear",
            confidence=0.89 + i * 0.01,
            track_id=600 + i,
            frame_number=100 + i,
            timestamp=timestamp
        )
    
    # Fox: 2 sightings (NEW species in current period)
    for i in range(2):
        timestamp = now - timedelta(minutes=30 - i * 10)
        db.insert_sighting(
            species="fox",
            confidence=0.75 + i * 0.05,
            track_id=700 + i,
            frame_number=100 + i,
            timestamp=timestamp
        )
    
    print("   ✅ Test data created")
    print(f"      Previous period (120-60 min): 16 sightings")
    print(f"      Current period (60-0 min): 19 sightings")


def example_1_basic_species_analysis():
    """
    Example 1: Analyze individual species.
    """
    print("\n" + "=" * 70)
    print("Example 1: Basic Species Analysis")
    print("=" * 70)
    
    # Initialize database and analytics
    db = WildlifeDatabase("analytics_test.db")
    db.clear_all_sightings()  # Start fresh
    
    # Setup test data
    setup_test_data(db)
    
    # Initialize analytics
    analytics = SightingsAnalytics("analytics_test.db")
    
    # Analyze tiger (decreasing trend)
    print("\n🐅 Analyzing Tiger:")
    tiger_analytics = analytics.analyze_species(
        species="tiger",
        time_window_minutes=60
    )
    
    print(f"   Species: {tiger_analytics.species}")
    print(f"   Count (last 60 min): {tiger_analytics.count}")
    print(f"   Previous count: {tiger_analytics.previous_count}")
    print(f"   Trend: {tiger_analytics.trend}")
    print(f"   Trend %: {tiger_analytics.trend_percentage:+.1f}%")
    print(f"   Avg confidence: {tiger_analytics.avg_confidence:.2f}")
    print(f"   Unique tracks: {tiger_analytics.unique_tracks}")
    
    # Analyze deer (increasing trend)
    print("\n🦌 Analyzing Deer:")
    deer_analytics = analytics.analyze_species(
        species="deer",
        time_window_minutes=60
    )
    
    print(f"   Species: {deer_analytics.species}")
    print(f"   Count (last 60 min): {deer_analytics.count}")
    print(f"   Previous count: {deer_analytics.previous_count}")
    print(f"   Trend: {deer_analytics.trend}")
    print(f"   Trend %: {deer_analytics.trend_percentage:+.1f}%")
    print(f"   Avg confidence: {deer_analytics.avg_confidence:.2f}")
    
    # Analyze bear (stable trend)
    print("\n🐻 Analyzing Bear:")
    bear_analytics = analytics.analyze_species(
        species="bear",
        time_window_minutes=60
    )
    
    print(f"   Species: {bear_analytics.species}")
    print(f"   Count (last 60 min): {bear_analytics.count}")
    print(f"   Previous count: {bear_analytics.previous_count}")
    print(f"   Trend: {bear_analytics.trend}")
    print(f"   Trend %: {bear_analytics.trend_percentage:+.1f}%")
    
    # Output in requested format
    print("\n📊 Output Format (as requested):")
    print(f'   {{"species": "tiger", "count": {tiger_analytics.count}, "trend": "{tiger_analytics.trend}"}}')
    print(f'   {{"species": "deer", "count": {deer_analytics.count}, "trend": "{deer_analytics.trend}"}}')
    print(f'   {{"species": "bear", "count": {bear_analytics.count}, "trend": "{bear_analytics.trend}"}}')
    
    analytics.close()
    db.close()
    print()


def example_2_all_species_analysis():
    """
    Example 2: Analyze all species at once.
    """
    print("=" * 70)
    print("Example 2: All Species Analysis")
    print("=" * 70)
    
    analytics = SightingsAnalytics("analytics_test.db")
    
    # Analyze all species
    print("\n📊 Analyzing all species (last 60 minutes)...")
    all_analytics = analytics.analyze_all_species(
        time_window_minutes=60,
        min_count=1
    )
    
    print(f"\n   Found {len(all_analytics)} species:\n")
    
    for species_data in all_analytics:
        trend_symbol = {
            "increasing": "📈",
            "decreasing": "📉",
            "stable": "➡️",
            "insufficient_data": "❓"
        }.get(species_data.trend, "")
        
        print(f"   {trend_symbol} {species_data.species.upper()}")
        print(f"      Count: {species_data.count}")
        print(f"      Trend: {species_data.trend} ({species_data.trend_percentage:+.1f}%)")
        print(f"      Confidence: {species_data.avg_confidence:.2f}")
        print(f"      Tracks: {species_data.unique_tracks}")
        print()
    
    analytics.close()
    print()


def example_3_time_based_grouping():
    """
    Example 3: Time-based grouping and counts.
    """
    print("=" * 70)
    print("Example 3: Time-Based Grouping")
    print("=" * 70)
    
    analytics = SightingsAnalytics("analytics_test.db")
    
    # Test different time windows
    time_windows = [30, 60, 120]
    
    print("\n⏰ Species counts across different time windows:\n")
    
    for window in time_windows:
        print(f"   Last {window} minutes:")
        counts = analytics.get_all_species_counts(time_window_minutes=window)
        
        for species, count in counts.items():
            print(f"      {species}: {count}")
        print()
    
    analytics.close()
    print()


def example_4_activity_summary():
    """
    Example 4: Overall activity summary.
    """
    print("=" * 70)
    print("Example 4: Activity Summary")
    print("=" * 70)
    
    analytics = SightingsAnalytics("analytics_test.db")
    
    # Get activity summary
    print("\n📈 Activity Summary (last 60 minutes):")
    summary = analytics.get_activity_summary(time_window_minutes=60)
    
    print(f"\n   Time Window: {summary['time_window_minutes']} minutes")
    print(f"   Period: {summary['start_time']} to {summary['end_time']}")
    print(f"   Total Sightings: {summary['total_sightings']}")
    print(f"   Unique Species: {summary['unique_species']}")
    print(f"   Unique Tracks: {summary['unique_tracks']}")
    print(f"   Avg Confidence: {summary['avg_confidence']:.2f}")
    print(f"   Most Common: {summary['most_common_species']} ({summary['most_common_count']} sightings)")
    
    analytics.close()
    print()


def example_5_period_comparison():
    """
    Example 5: Compare time periods.
    """
    print("=" * 70)
    print("Example 5: Period Comparison")
    print("=" * 70)
    
    analytics = SightingsAnalytics("analytics_test.db")
    
    # Compare periods for each species
    species_list = ["tiger", "deer", "bear", "fox"]
    
    print("\n🔄 Comparing current vs previous 60-minute periods:\n")
    
    for species in species_list:
        comparison = analytics.compare_time_periods(
            species=species,
            period_minutes=60
        )
        
        trend_symbol = {
            "increasing": "📈",
            "decreasing": "📉",
            "stable": "➡️",
            "insufficient_data": "❓"
        }.get(comparison["trend"], "")
        
        print(f"   {trend_symbol} {species.upper()}")
        print(f"      Current: {comparison['current_period_count']}")
        print(f"      Previous: {comparison['previous_period_count']}")
        print(f"      Change: {comparison['trend_percentage']:+.1f}%")
        print(f"      Trend: {comparison['trend']}")
        print()
    
    # Compare all species combined
    print("   📊 ALL SPECIES COMBINED")
    all_comparison = analytics.compare_time_periods(
        species=None,
        period_minutes=60
    )
    print(f"      Current: {all_comparison['current_period_count']}")
    print(f"      Previous: {all_comparison['previous_period_count']}")
    print(f"      Change: {all_comparison['trend_percentage']:+.1f}%")
    print(f"      Trend: {all_comparison['trend']}")
    
    analytics.close()
    print()


def example_6_json_output():
    """
    Example 6: JSON-ready output format.
    """
    print("=" * 70)
    print("Example 6: JSON Output Format")
    print("=" * 70)
    
    analytics = SightingsAnalytics("analytics_test.db")
    
    # Get all species analytics
    all_analytics = analytics.analyze_all_species(time_window_minutes=60)
    
    print("\n📄 JSON-ready output:\n")
    
    import json
    
    # Convert to list of dictionaries
    results = [species.to_dict() for species in all_analytics]
    
    # Pretty print JSON
    print(json.dumps(results, indent=2))
    
    analytics.close()
    print()


def example_7_custom_time_windows():
    """
    Example 7: Custom time windows for trend analysis.
    """
    print("=" * 70)
    print("Example 7: Custom Time Windows")
    print("=" * 70)
    
    analytics = SightingsAnalytics("analytics_test.db")
    
    print("\n⏱️  Analyzing tiger with different time windows:\n")
    
    # Current window: 30 min, compare with previous 30 min
    print("   30-minute windows:")
    tiger_30 = analytics.analyze_species(
        species="tiger",
        time_window_minutes=30,
        trend_comparison_minutes=30
    )
    print(f"      Current: {tiger_30.count}, Previous: {tiger_30.previous_count}")
    print(f"      Trend: {tiger_30.trend} ({tiger_30.trend_percentage:+.1f}%)")
    
    # Current window: 60 min, compare with previous 60 min
    print("\n   60-minute windows:")
    tiger_60 = analytics.analyze_species(
        species="tiger",
        time_window_minutes=60,
        trend_comparison_minutes=60
    )
    print(f"      Current: {tiger_60.count}, Previous: {tiger_60.previous_count}")
    print(f"      Trend: {tiger_60.trend} ({tiger_60.trend_percentage:+.1f}%)")
    
    # Current window: 60 min, compare with previous 120 min
    print("\n   60-minute current vs 120-minute previous:")
    tiger_mixed = analytics.analyze_species(
        species="tiger",
        time_window_minutes=60,
        trend_comparison_minutes=120
    )
    print(f"      Current (60 min): {tiger_mixed.count}")
    print(f"      Previous (120 min): {tiger_mixed.previous_count}")
    print(f"      Trend: {tiger_mixed.trend} ({tiger_mixed.trend_percentage:+.1f}%)")
    
    analytics.close()
    print()


def main():
    """Run all examples."""
    print("\n🦌 Wildlife Sightings Analytics Examples\n")
    
    # Run examples
    example_1_basic_species_analysis()
    example_2_all_species_analysis()
    example_3_time_based_grouping()
    example_4_activity_summary()
    example_5_period_comparison()
    example_6_json_output()
    example_7_custom_time_windows()
    
    print("=" * 70)
    print("Examples complete!")
    print("=" * 70)
    print("\n✅ Analytics Features:")
    print("   ✓ Species count analysis")
    print("   ✓ Trend detection (increasing/decreasing/stable)")
    print("   ✓ Time-based grouping (customizable windows)")
    print("   ✓ Period comparison")
    print("   ✓ Activity summaries")
    print("   ✓ JSON-ready output")
    print("   ✓ SQLite queries + Python logic")
    print()


if __name__ == "__main__":
    main()
