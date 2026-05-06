# Sightings Analytics Module

Complete guide to the wildlife sightings analytics module.

## Overview

The `SightingsAnalytics` module provides powerful analytics capabilities for analyzing stored wildlife sightings data. It uses SQLite queries combined with Python logic to deliver insights about species counts, trends, and activity patterns.

## Features

- **Species Count Analysis**: Count sightings per species in time windows
- **Trend Detection**: Identify increasing/decreasing/stable trends
- **Time-Based Grouping**: Analyze data across custom time windows
- **Period Comparison**: Compare current vs previous periods
- **Activity Summaries**: Overall statistics and insights
- **JSON Output**: API-ready data format

## Installation

The analytics module is part of the wildlife monitoring system:

```python
from wildlife_monitoring.analytics import SightingsAnalytics, SpeciesAnalytics, Trend
```

## Quick Start

### Basic Usage

```python
from wildlife_monitoring.analytics import SightingsAnalytics

# Initialize analytics engine
analytics = SightingsAnalytics("wildlife_sightings.db")

# Analyze a species
tiger_data = analytics.analyze_species("tiger", time_window_minutes=60)

print(f"Species: {tiger_data.species}")
print(f"Count: {tiger_data.count}")
print(f"Trend: {tiger_data.trend}")
print(f"Change: {tiger_data.trend_percentage:+.1f}%")

# Close connection
analytics.close()
```

### Output Format (As Requested)

```python
# Simple format
{"species": "tiger", "count": 5, "trend": "decreasing"}

# Full format
{
  "species": "tiger",
  "count": 5,
  "trend": "decreasing",
  "avg_confidence": 0.87,
  "unique_tracks": 3,
  "previous_count": 8,
  "trend_percentage": -37.5
}
```

## Core Classes

### SightingsAnalytics

Main analytics engine for querying and analyzing sightings data.

**Constructor:**
```python
analytics = SightingsAnalytics(db_path="wildlife_sightings.db")
```

**Parameters:**
- `db_path` (str): Path to SQLite database file

### SpeciesAnalytics

Data class containing analysis results for a species.

**Attributes:**
- `species` (str): Species name
- `count` (int): Total sightings in time window
- `trend` (str): Trend direction ("increasing", "decreasing", "stable", "insufficient_data")
- `avg_confidence` (float): Average classification confidence
- `unique_tracks` (int): Number of unique tracks
- `first_seen` (str): First sighting timestamp
- `last_seen` (str): Last sighting timestamp
- `previous_count` (int): Count in previous period
- `trend_percentage` (float): Percentage change from previous period

**Methods:**
- `to_dict()`: Convert to dictionary format

### Trend Enum

Enumeration of trend directions:
- `Trend.INCREASING`: Count is increasing
- `Trend.DECREASING`: Count is decreasing
- `Trend.STABLE`: Count is stable (within threshold)
- `Trend.INSUFFICIENT_DATA`: Not enough data to determine trend

## Methods

### analyze_species()

Analyze a specific species within a time window.

```python
analytics.analyze_species(
    species="tiger",
    time_window_minutes=60,
    trend_comparison_minutes=60  # Optional, defaults to time_window_minutes
)
```

**Parameters:**
- `species` (str): Species name to analyze
- `time_window_minutes` (int): Current time window in minutes (default: 60)
- `trend_comparison_minutes` (int): Previous period for trend comparison (default: same as time_window_minutes)

**Returns:**
- `SpeciesAnalytics`: Analysis results

**Example:**
```python
tiger = analytics.analyze_species("tiger", time_window_minutes=60)
print(f"{tiger.species}: {tiger.count} sightings, trend: {tiger.trend}")
```

### analyze_all_species()

Analyze all species within a time window.

```python
analytics.analyze_all_species(
    time_window_minutes=60,
    trend_comparison_minutes=None,
    min_count=1
)
```

**Parameters:**
- `time_window_minutes` (int): Time window in minutes (default: 60)
- `trend_comparison_minutes` (int): Previous period for trend comparison (optional)
- `min_count` (int): Minimum count to include in results (default: 1)

**Returns:**
- `List[SpeciesAnalytics]`: List of analysis results, sorted by count (descending)

**Example:**
```python
all_species = analytics.analyze_all_species(time_window_minutes=60)
for species in all_species:
    print(f"{species.species}: {species.count} ({species.trend})")
```

### get_species_count()

Get count of sightings for a species in time window.

```python
count = analytics.get_species_count("tiger", time_window_minutes=60)
```

**Parameters:**
- `species` (str): Species name
- `time_window_minutes` (int): Time window in minutes (default: 60)

**Returns:**
- `int`: Count of sightings

### get_all_species_counts()

Get counts for all species in time window.

```python
counts = analytics.get_all_species_counts(time_window_minutes=60)
# Returns: {"tiger": 5, "deer": 12, "bear": 3}
```

**Parameters:**
- `time_window_minutes` (int): Time window in minutes (default: 60)

**Returns:**
- `Dict[str, int]`: Dictionary mapping species name to count

### get_activity_summary()

Get overall activity summary for time window.

```python
summary = analytics.get_activity_summary(time_window_minutes=60)
```

**Parameters:**
- `time_window_minutes` (int): Time window in minutes (default: 60)

**Returns:**
- `Dict[str, Any]`: Summary statistics including:
  - `time_window_minutes`: Time window size
  - `start_time`: Period start timestamp
  - `end_time`: Period end timestamp
  - `total_sightings`: Total number of sightings
  - `unique_species`: Number of unique species
  - `unique_tracks`: Number of unique tracks
  - `avg_confidence`: Average classification confidence
  - `most_common_species`: Most frequently seen species
  - `most_common_count`: Count of most common species

**Example:**
```python
summary = analytics.get_activity_summary(60)
print(f"Total sightings: {summary['total_sightings']}")
print(f"Most common: {summary['most_common_species']}")
```

### compare_time_periods()

Compare current period with previous period.

```python
comparison = analytics.compare_time_periods(
    species="tiger",  # None = all species
    period_minutes=60
)
```

**Parameters:**
- `species` (str, optional): Species name (None = all species)
- `period_minutes` (int): Period length in minutes (default: 60)

**Returns:**
- `Dict[str, Any]`: Comparison results including:
  - `species`: Species name or "all"
  - `current_period_count`: Count in current period
  - `previous_period_count`: Count in previous period
  - `trend`: Trend direction
  - `trend_percentage`: Percentage change
  - `period_minutes`: Period length

**Example:**
```python
comparison = analytics.compare_time_periods("tiger", period_minutes=60)
print(f"Current: {comparison['current_period_count']}")
print(f"Previous: {comparison['previous_period_count']}")
print(f"Trend: {comparison['trend']} ({comparison['trend_percentage']:+.1f}%)")
```

### get_hourly_breakdown()

Get hourly breakdown of sightings.

```python
breakdown = analytics.get_hourly_breakdown(
    species="tiger",  # None = all species
    hours=24
)
```

**Parameters:**
- `species` (str, optional): Species name (None = all species)
- `hours` (int): Number of hours to analyze (default: 24)

**Returns:**
- `List[Dict[str, Any]]`: List of hourly data with `hour` and `count`

**Example:**
```python
breakdown = analytics.get_hourly_breakdown("tiger", hours=24)
for entry in breakdown:
    print(f"{entry['hour']}: {entry['count']} sightings")
```

## Trend Detection

### How Trends Are Calculated

1. **Compare Periods**: Current period count vs previous period count
2. **Calculate Change**: `percentage_change = ((current - previous) / previous) * 100`
3. **Determine Trend**:
   - If `|percentage_change| < 10%`: **STABLE**
   - If `percentage_change > 10%`: **INCREASING**
   - If `percentage_change < -10%`: **DECREASING**
   - If both periods have 0 counts: **INSUFFICIENT_DATA**

### Custom Threshold

The stable threshold (default 10%) can be adjusted by modifying the `_calculate_trend()` method's `stable_threshold` parameter.

## Time Windows

### Standard Time Windows

```python
# Last 30 minutes
analytics.analyze_species("tiger", time_window_minutes=30)

# Last hour
analytics.analyze_species("tiger", time_window_minutes=60)

# Last 2 hours
analytics.analyze_species("tiger", time_window_minutes=120)

# Last 24 hours
analytics.analyze_species("tiger", time_window_minutes=1440)
```

### Custom Comparison Windows

```python
# Current: last 60 min, Previous: 60 min before that
analytics.analyze_species(
    "tiger",
    time_window_minutes=60,
    trend_comparison_minutes=60
)

# Current: last 30 min, Previous: last 120 min
analytics.analyze_species(
    "tiger",
    time_window_minutes=30,
    trend_comparison_minutes=120
)
```

## Usage Examples

### Example 1: Simple Species Analysis

```python
from wildlife_monitoring.analytics import SightingsAnalytics

analytics = SightingsAnalytics("wildlife_sightings.db")

# Analyze tiger
tiger = analytics.analyze_species("tiger", time_window_minutes=60)

# Output in requested format
output = {
    "species": tiger.species,
    "count": tiger.count,
    "trend": tiger.trend
}
print(output)
# {"species": "tiger", "count": 5, "trend": "decreasing"}

analytics.close()
```

### Example 2: All Species Dashboard

```python
analytics = SightingsAnalytics("wildlife_sightings.db")

# Get all species
all_species = analytics.analyze_all_species(time_window_minutes=60)

# Display dashboard
print("Wildlife Activity Dashboard")
print("=" * 50)

for species in all_species:
    trend_symbol = {
        "increasing": "📈",
        "decreasing": "📉",
        "stable": "➡️"
    }.get(species.trend, "")
    
    print(f"{trend_symbol} {species.species.upper()}")
    print(f"   Count: {species.count}")
    print(f"   Trend: {species.trend} ({species.trend_percentage:+.1f}%)")
    print(f"   Confidence: {species.avg_confidence:.2f}")
    print()

analytics.close()
```

### Example 3: Activity Summary

```python
analytics = SightingsAnalytics("wildlife_sightings.db")

summary = analytics.get_activity_summary(time_window_minutes=60)

print(f"Activity Summary (Last {summary['time_window_minutes']} minutes)")
print(f"Total Sightings: {summary['total_sightings']}")
print(f"Unique Species: {summary['unique_species']}")
print(f"Most Common: {summary['most_common_species']} ({summary['most_common_count']})")

analytics.close()
```

### Example 4: JSON API Response

```python
import json
from wildlife_monitoring.analytics import SightingsAnalytics

analytics = SightingsAnalytics("wildlife_sightings.db")

# Get all species analytics
all_species = analytics.analyze_all_species(time_window_minutes=60)

# Convert to JSON
results = [species.to_dict() for species in all_species]
json_output = json.dumps(results, indent=2)

print(json_output)

analytics.close()
```

### Example 5: Context Manager

```python
from wildlife_monitoring.analytics import SightingsAnalytics

# Automatic cleanup with context manager
with SightingsAnalytics("wildlife_sightings.db") as analytics:
    tiger = analytics.analyze_species("tiger", time_window_minutes=60)
    print(f"{tiger.species}: {tiger.count} ({tiger.trend})")
# Connection automatically closed
```

## Integration with Pipeline

### Real-Time Analytics

```python
from wildlife_monitoring.database import WildlifeDatabase
from wildlife_monitoring.analytics import SightingsAnalytics
from wildlife_monitoring.pipeline.modular_pipeline import process_frame_modular

# Initialize
db = WildlifeDatabase("wildlife.db")
analytics = SightingsAnalytics("wildlife.db")

# Process frame and save to database
state = process_frame_modular(frame, frame_number, detector, classifier, tracker)

# Save sightings
from wildlife_monitoring.database.pipeline_integration import save_pipeline_results_to_db
save_pipeline_results_to_db(db, state)

# Get real-time analytics
summary = analytics.get_activity_summary(time_window_minutes=5)
print(f"Last 5 minutes: {summary['total_sightings']} sightings")

# Check trends
all_species = analytics.analyze_all_species(time_window_minutes=10)
for species in all_species:
    if species.trend == "increasing":
        print(f"⚠️ {species.species} activity increasing!")
```

## Performance Considerations

### Database Indexes

The analytics module benefits from these indexes (automatically created):
- `idx_track_frame`: On (track_id, frame_number) for duplicate checking
- `idx_species`: On species for species queries
- `idx_timestamp`: On timestamp for time-based queries

### Query Optimization

- Time-based queries use ISO timestamp comparison
- Aggregations use SQLite's built-in functions (COUNT, AVG, etc.)
- Results are cached in Python for multiple operations

### Best Practices

1. **Reuse connections**: Create one `SightingsAnalytics` instance and reuse it
2. **Use context managers**: Ensures proper cleanup
3. **Batch operations**: Analyze multiple species at once with `analyze_all_species()`
4. **Appropriate time windows**: Larger windows = more data but slower queries

## Troubleshooting

### No Data Returned

```python
# Check if database has data
summary = analytics.get_activity_summary(time_window_minutes=1440)  # 24 hours
print(f"Total sightings: {summary['total_sightings']}")
```

### Insufficient Data Trend

If trend is "insufficient_data", both current and previous periods have 0 counts. Try:
- Increasing time window
- Checking if data exists in database
- Verifying timestamps are recent

### Incorrect Trends

Ensure:
- Database timestamps are in ISO format
- System time is correct
- Time windows are appropriate for your data frequency

## API Reference Summary

| Method | Purpose | Returns |
|--------|---------|---------|
| `analyze_species()` | Analyze single species | `SpeciesAnalytics` |
| `analyze_all_species()` | Analyze all species | `List[SpeciesAnalytics]` |
| `get_species_count()` | Get count for species | `int` |
| `get_all_species_counts()` | Get counts for all | `Dict[str, int]` |
| `get_activity_summary()` | Overall statistics | `Dict[str, Any]` |
| `compare_time_periods()` | Compare periods | `Dict[str, Any]` |
| `get_hourly_breakdown()` | Hourly data | `List[Dict]` |

## See Also

- [Database Module](DATABASE.md) - Sightings storage
- [Pipeline Module](MODULAR_PIPELINE.md) - Data collection
- [Dashboard Integration](../README.md) - Visualization
