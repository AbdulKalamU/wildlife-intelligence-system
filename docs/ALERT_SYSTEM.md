# Analytics-Based Alert System

Complete guide to the wildlife monitoring alert system built on top of sightings analytics.

## Overview

The `AnalyticsAlertSystem` provides intelligent alerting based on wildlife sightings analytics. It automatically evaluates trends, counts, and patterns to generate alerts with appropriate severity levels.

## Features

- **Population Risk Alerts**: Detect decreasing population trends
- **Low Population Alerts**: Identify species with critically low counts
- **Anomaly Alerts**: Detect sudden spikes in activity
- **Configurable Rules**: Customize thresholds and parameters
- **Severity Levels**: Automatic severity assignment (high/medium/low)
- **Multiple Output Formats**: Simple and detailed formats

## Installation

The alert system is part of the wildlife monitoring system:

```python
from wildlife_monitoring.alerts import (
    AnalyticsAlertSystem,
    Alert,
    AlertConfig,
    check_alerts,
    generate_alerts_for_all_species
)
```

## Quick Start

### Basic Usage

```python
from wildlife_monitoring.analytics import SightingsAnalytics
from wildlife_monitoring.alerts import AnalyticsAlertSystem

# Initialize analytics and alert system
analytics = SightingsAnalytics("wildlife_sightings.db")
alert_system = AnalyticsAlertSystem(analytics)

# Check alerts for a species
tiger_alert = alert_system.check_alerts("tiger", time_window_minutes=60)

print(f"Species: {tiger_alert.species}")
print(f"Alert: {tiger_alert.alert}")
print(f"Severity: {tiger_alert.severity}")

# Close connections
analytics.close()
```

### Output Format (As Requested)

```python
# Simple format
{"species": "tiger", "alert": "population_risk", "severity": "high"}

# Full format
{
  "species": "tiger",
  "alert": "population_risk",
  "severity": "high",
  "count": 3,
  "trend": "decreasing",
  "trend_percentage": -70.0,
  "previous_count": 10,
  "message": "Critical: Population decreasing (-70.0%) and low count (3)"
}
```

## Alert Types

### 1. Population Risk (`population_risk`)

**Trigger**: Decreasing population trend detected

**Conditions**:
- Trend is "decreasing"
- Percentage change ≤ -10% (configurable)

**Severity**:
- **HIGH**: Decreasing + low count (below threshold)
- **MEDIUM**: Only decreasing (count above threshold)

**Example**:
```python
# Tiger: 10 → 3 sightings (decreasing + low count)
{"species": "tiger", "alert": "population_risk", "severity": "high"}
```

### 2. Low Population (`low_population`)

**Trigger**: Count below threshold

**Conditions**:
- Current count < low_count_threshold (default: 5)
- Trend is NOT decreasing (otherwise it's population_risk)

**Severity**:
- **MEDIUM**: Low count detected

**Example**:
```python
# Wolf: 4 sightings (below threshold of 5)
{"species": "wolf", "alert": "low_population", "severity": "medium"}
```

### 3. Anomaly (`anomaly`)

**Trigger**: Sudden spike in activity

**Conditions**:
- Percentage increase ≥ anomaly_spike_threshold (default: 100%)
- Count ≥ anomaly_min_count (default: 3)

**Severity**:
- **MEDIUM**: Sudden spike detected

**Example**:
```python
# Fox: 2 → 10 sightings (+400% increase)
{"species": "fox", "alert": "anomaly", "severity": "medium"}
```

### 4. Stable (`stable`)

**Trigger**: No issues detected

**Conditions**:
- Trend is "stable" or "increasing"
- Count above threshold

**Severity**:
- **LOW**: Normal activity

**Example**:
```python
# Bear: 10 sightings (stable)
{"species": "bear", "alert": "stable", "severity": "low"}
```

### 5. No Data (`no_data`)

**Trigger**: No sightings in current or previous period

**Severity**:
- **INFO**: Informational only

## Severity Logic

The system uses the following severity logic (as requested):

| Condition | Severity | Alert Type |
|-----------|----------|------------|
| Decreasing + Low Count | **HIGH** | population_risk |
| Only Decreasing | **MEDIUM** | population_risk |
| Only Low Count | **MEDIUM** | low_population |
| Sudden Spike | **MEDIUM** | anomaly |
| Stable/Increasing | **LOW** | stable |

## Core Classes

### AnalyticsAlertSystem

Main alert system class that evaluates analytics data and generates alerts.

**Constructor:**
```python
alert_system = AnalyticsAlertSystem(
    analytics,  # SightingsAnalytics instance
    config=AlertConfig()  # Optional configuration
)
```

### Alert

Data class containing alert information.

**Attributes:**
- `species` (str): Species name
- `alert` (str): Alert type
- `severity` (str): Severity level
- `count` (int): Current count
- `trend` (str): Trend direction
- `trend_percentage` (float): Percentage change
- `previous_count` (int): Previous period count
- `message` (str): Human-readable message
- `timestamp` (str): When alert was generated

**Methods:**
- `to_dict()`: Convert to full dictionary format
- `to_simple_dict()`: Convert to simple format (species, alert, severity)

### AlertConfig

Configuration for alert rules.

**Attributes:**
- `low_count_threshold` (int): Count below this triggers low population alert (default: 5)
- `anomaly_spike_threshold` (float): Percentage increase for anomaly (default: 100.0)
- `anomaly_min_count` (int): Minimum count to trigger anomaly (default: 3)
- `decreasing_threshold` (float): Percentage decrease to consider significant (default: -10.0)

## Methods

### check_alerts()

Check alerts for a specific species.

```python
alert = alert_system.check_alerts(
    species="tiger",
    time_window_minutes=60
)
```

**Parameters:**
- `species` (str): Species name
- `time_window_minutes` (int): Time window for analysis (default: 60)

**Returns:**
- `Alert`: Alert object with type and severity

**Example:**
```python
tiger_alert = alert_system.check_alerts("tiger", time_window_minutes=60)
print(tiger_alert.to_simple_dict())
# {"species": "tiger", "alert": "population_risk", "severity": "high"}
```

### generate_alerts_for_all_species()

Generate alerts for all species.

```python
all_alerts = alert_system.generate_alerts_for_all_species(
    time_window_minutes=60,
    min_count=1
)
```

**Parameters:**
- `time_window_minutes` (int): Time window for analysis (default: 60)
- `min_count` (int): Minimum count to include species (default: 1)

**Returns:**
- `List[Alert]`: List of alerts, sorted by severity (high to low)

**Example:**
```python
all_alerts = alert_system.generate_alerts_for_all_species(60)
for alert in all_alerts:
    print(f"{alert.species}: {alert.severity} - {alert.alert}")
```

### get_critical_alerts()

Get only critical alerts (high or medium severity).

```python
critical_alerts = alert_system.get_critical_alerts(
    time_window_minutes=60,
    severity_threshold="medium"  # "high" or "medium"
)
```

**Parameters:**
- `time_window_minutes` (int): Time window for analysis
- `severity_threshold` (str): Minimum severity ("high" or "medium")

**Returns:**
- `List[Alert]`: List of critical alerts

**Example:**
```python
# Get only HIGH severity alerts
high_alerts = alert_system.get_critical_alerts(60, severity_threshold="high")

# Get HIGH + MEDIUM severity alerts
important_alerts = alert_system.get_critical_alerts(60, severity_threshold="medium")
```

### get_alerts_by_type()

Get alerts of a specific type.

```python
risk_alerts = alert_system.get_alerts_by_type(
    alert_type="population_risk",
    time_window_minutes=60
)
```

**Parameters:**
- `alert_type` (str): Alert type ("population_risk", "low_population", "anomaly", "stable")
- `time_window_minutes` (int): Time window for analysis

**Returns:**
- `List[Alert]`: List of alerts matching the type

**Example:**
```python
# Get all population risk alerts
risk_alerts = alert_system.get_alerts_by_type("population_risk", 60)

# Get all anomaly alerts
anomaly_alerts = alert_system.get_alerts_by_type("anomaly", 60)
```

### get_alert_summary()

Get summary statistics for all alerts.

```python
summary = alert_system.get_alert_summary(time_window_minutes=60)
```

**Parameters:**
- `time_window_minutes` (int): Time window for analysis

**Returns:**
- `Dict[str, Any]`: Summary with counts by severity and type

**Example:**
```python
summary = alert_system.get_alert_summary(60)
print(f"Total alerts: {summary['total_alerts']}")
print(f"High severity: {summary['severity_counts']['high']}")
print(f"Critical species: {summary['critical_species']}")
```

## Configuration

### Default Configuration

```python
config = AlertConfig(
    low_count_threshold=5,
    anomaly_spike_threshold=100.0,  # 100% increase
    anomaly_min_count=3,
    decreasing_threshold=-10.0  # -10% or more
)
```

### Custom Configuration

```python
# Stricter thresholds
strict_config = AlertConfig(
    low_count_threshold=10,  # Higher threshold
    anomaly_spike_threshold=150.0,  # 150% increase
    anomaly_min_count=5,
    decreasing_threshold=-15.0  # -15% or more
)

alert_system = AnalyticsAlertSystem(analytics, strict_config)
```

### Update Configuration

```python
# Update configuration after initialization
new_config = AlertConfig(low_count_threshold=8)
alert_system.update_config(new_config)
```

## Usage Examples

### Example 1: Simple Alert Check

```python
from wildlife_monitoring.analytics import SightingsAnalytics
from wildlife_monitoring.alerts import check_alerts

analytics = SightingsAnalytics("wildlife_sightings.db")

# Check tiger alerts
tiger_alert = check_alerts(analytics, "tiger", time_window_minutes=60)

# Output in requested format
print(tiger_alert.to_simple_dict())
# {"species": "tiger", "alert": "population_risk", "severity": "high"}

analytics.close()
```

### Example 2: All Species Dashboard

```python
from wildlife_monitoring.alerts import generate_alerts_for_all_species

analytics = SightingsAnalytics("wildlife_sightings.db")

# Generate all alerts
all_alerts = generate_alerts_for_all_species(analytics, time_window_minutes=60)

# Display dashboard
for alert in all_alerts:
    severity_symbol = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    symbol = severity_symbol.get(alert.severity, "")
    
    print(f"{symbol} {alert.species}: {alert.alert} ({alert.severity})")
    print(f"   {alert.message}")

analytics.close()
```

### Example 3: Critical Alerts Only

```python
analytics = SightingsAnalytics("wildlife_sightings.db")
alert_system = AnalyticsAlertSystem(analytics)

# Get only critical alerts
critical = alert_system.get_critical_alerts(60, severity_threshold="high")

if critical:
    print("🚨 CRITICAL ALERTS:")
    for alert in critical:
        print(f"   {alert.species}: {alert.message}")
else:
    print("✅ No critical alerts")

analytics.close()
```

### Example 4: Alert Monitoring Loop

```python
import time
from wildlife_monitoring.database import WildlifeDatabase
from wildlife_monitoring.analytics import SightingsAnalytics
from wildlife_monitoring.alerts import AnalyticsAlertSystem

db = WildlifeDatabase("wildlife.db")
analytics = SightingsAnalytics("wildlife.db")
alert_system = AnalyticsAlertSystem(analytics)

# Monitor every 5 minutes
while True:
    # Get critical alerts
    critical = alert_system.get_critical_alerts(60, severity_threshold="medium")
    
    if critical:
        print(f"\n🚨 {len(critical)} alert(s) detected:")
        for alert in critical:
            print(f"   {alert.species}: {alert.severity} - {alert.alert}")
    
    time.sleep(300)  # Wait 5 minutes
```

### Example 5: JSON API Response

```python
import json
from wildlife_monitoring.alerts import generate_alerts_for_all_species

analytics = SightingsAnalytics("wildlife_sightings.db")

# Generate alerts
all_alerts = generate_alerts_for_all_species(analytics, 60)

# Convert to JSON (simple format)
simple_output = [alert.to_simple_dict() for alert in all_alerts]
print(json.dumps(simple_output, indent=2))

# Convert to JSON (full format)
full_output = [alert.to_dict() for alert in all_alerts]
print(json.dumps(full_output, indent=2))

analytics.close()
```

## Integration with Pipeline

### Real-Time Alerting

```python
from wildlife_monitoring.database import WildlifeDatabase
from wildlife_monitoring.analytics import SightingsAnalytics
from wildlife_monitoring.alerts import AnalyticsAlertSystem
from wildlife_monitoring.database.pipeline_integration import save_pipeline_results_to_db

# Initialize
db = WildlifeDatabase("wildlife.db")
analytics = SightingsAnalytics("wildlife.db")
alert_system = AnalyticsAlertSystem(analytics)

# Process frame and save
state = process_frame_modular(frame, frame_number, detector, classifier, tracker)
save_pipeline_results_to_db(db, state)

# Check for alerts (last 5 minutes)
critical = alert_system.get_critical_alerts(5, severity_threshold="high")

if critical:
    for alert in critical:
        print(f"🚨 ALERT: {alert.species} - {alert.message}")
        # Send notification, log, etc.
```

## Convenience Functions

### check_alerts()

Quick function to check alerts for a species without creating an alert system instance.

```python
from wildlife_monitoring.alerts import check_alerts

alert = check_alerts(analytics, "tiger", time_window_minutes=60)
```

### generate_alerts_for_all_species()

Quick function to generate alerts for all species.

```python
from wildlife_monitoring.alerts import generate_alerts_for_all_species

all_alerts = generate_alerts_for_all_species(analytics, time_window_minutes=60)
```

## Alert Rules Summary

| Rule | Condition | Alert Type | Severity |
|------|-----------|------------|----------|
| Decreasing + Low Count | trend="decreasing" AND count < threshold | population_risk | HIGH |
| Only Decreasing | trend="decreasing" AND count ≥ threshold | population_risk | MEDIUM |
| Only Low Count | count < threshold AND trend ≠ "decreasing" | low_population | MEDIUM |
| Sudden Spike | increase ≥ 100% AND count ≥ 3 | anomaly | MEDIUM |
| Stable | No issues | stable | LOW |

## Best Practices

1. **Choose appropriate time windows**: Shorter windows (5-15 min) for real-time monitoring, longer windows (60+ min) for trend analysis

2. **Configure thresholds**: Adjust `AlertConfig` based on your species and environment

3. **Filter by severity**: Focus on high/medium alerts for critical monitoring

4. **Monitor trends**: Track alert patterns over time to identify persistent issues

5. **Combine with analytics**: Use alert system alongside analytics for comprehensive insights

## Troubleshooting

### No Alerts Generated

- Check if database has recent data
- Verify time window is appropriate
- Check if species exists in database
- Ensure analytics is working correctly

### Too Many False Positives

- Increase `low_count_threshold`
- Adjust `anomaly_spike_threshold`
- Increase `anomaly_min_count`
- Make `decreasing_threshold` more strict (e.g., -20%)

### Missing Critical Alerts

- Decrease `low_count_threshold`
- Lower `anomaly_spike_threshold`
- Make `decreasing_threshold` less strict (e.g., -5%)

## See Also

- [Analytics Module](SIGHTINGS_ANALYTICS.md) - Underlying analytics system
- [Database Module](DATABASE.md) - Sightings storage
- [Pipeline Module](MODULAR_PIPELINE.md) - Data collection
