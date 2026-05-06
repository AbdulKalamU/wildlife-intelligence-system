# Production Wildlife Monitoring Dashboard

Professional, product-level interface for wildlife monitoring with real-time analytics and alerts.

## Overview

The production dashboard provides a clean, minimal interface for monitoring wildlife with:
- **Live camera feed** with bounding boxes and species labels
- **Species activity panel** with counts and trends
- **Real-time alerts** with severity-based highlighting
- **Database integration** for persistent storage
- **Analytics engine** for trend detection
- **Alert system** for critical notifications

## Features

### Layout

**Two-Column Design**:
- **Left Column (2/3 width)**: Live camera feed with annotated detections
- **Right Column (1/3 width)**: Dashboard panel with species and alerts

### Dashboard Panel

**Species Activity Section**:
- Species name (e.g., "Tiger", "Deer")
- Current count (last 5 minutes)
- Trend indicator (📈 increasing, 📉 decreasing, ➡️ stable)
- Percentage change from previous period

**Alerts Section**:
- **HIGH alerts** (red background, 🔴 icon)
- **MEDIUM alerts** (orange background, 🟡 icon)
- **LOW alerts** (green background, 🟢 icon)
- Human-readable alert messages

### Special States

**No Wildlife Detected**:
- Shows "🦌 No wildlife detected" message
- Clean, centered display
- Appears when no animals in last 5 minutes

**No Alerts**:
- Shows "No alerts at this time" message
- Informational display

## Installation

The production dashboard is part of the wildlife monitoring system:

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Run the production dashboard
python3 run_production_dashboard.py
```

## Quick Start

### Launch Dashboard

```bash
# Method 1: Using launcher script (recommended)
python3 run_production_dashboard.py

# Method 2: Direct Streamlit command
streamlit run wildlife_monitoring/dashboard/production_app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

### Basic Usage

1. **Initialize System**: Dashboard auto-initializes on startup
2. **Select Video Source**: Choose "Webcam" or "Upload Video"
3. **Click Start**: Begin processing
4. **Monitor**: Watch live feed and dashboard updates
5. **Click Stop**: Pause processing
6. **Click Refresh**: Update dashboard manually

## User Interface

### Header

```
🦌 Wildlife Monitoring
Real-time detection, tracking, and analytics
```

Clean, minimal header with system title and subtitle.

### Settings Panel (Collapsible)

**Video Source**:
- Webcam (with camera index selector)
- Upload Video (file uploader)

**Database**:
- Clear Database button (resets all data)

### Control Buttons

- **▶️ Start**: Begin processing video
- **⏸️ Stop**: Pause processing
- **📊 Refresh**: Update dashboard manually

### Live Feed Panel

**Features**:
- Real-time video display
- Bounding boxes around detected animals
- Species labels (if classification enabled)
- Track IDs for each animal
- Smooth 30 FPS playback

**When Not Processing**:
- Shows "👆 Click 'Start' to begin monitoring"

### Dashboard Panel

#### Species Activity

**Card Layout**:
```
┌─────────────────────┐
│ Tiger               │
│ 5                   │
│ 📈 Increasing (+50%)│
└─────────────────────┘
```

**Information Displayed**:
- Species name (capitalized)
- Count (large, bold number)
- Trend with icon and percentage

**Trend Indicators**:
- 📈 Green: Increasing population
- 📉 Red: Decreasing population
- ➡️ Gray: Stable population

#### Alerts

**HIGH Severity (Red)**:
```
┌─────────────────────────────────────┐
│ 🔴 Tiger - Population Risk          │
│ Critical: Population decreasing     │
│ (-70%) and low count (3)            │
└─────────────────────────────────────┘
```

**MEDIUM Severity (Orange)**:
```
┌─────────────────────────────────────┐
│ 🟡 Fox - Unusual Activity           │
│ Sudden spike detected: +400%        │
│ increase                            │
└─────────────────────────────────────┘
```

**LOW Severity (Green)**:
```
┌─────────────────────────────────────┐
│ 🟢 Bear - Stable                    │
│ Population stable: 10 sighting(s)   │
└─────────────────────────────────────┘
```

## Technical Details

### System Components

**Pipeline**:
- YOLOv8 for detection
- ResNet50 for classification
- Centroid tracker for tracking

**Database**:
- SQLite for persistent storage
- Automatic sighting recording
- Duplicate prevention

**Analytics**:
- Time-based analysis (5-minute windows)
- Trend detection (increasing/decreasing/stable)
- Species count aggregation

**Alerts**:
- Population risk detection
- Low population warnings
- Anomaly detection (sudden spikes)
- Severity-based prioritization

### Data Flow

```
Camera/Video → Detection → Classification → Tracking
                                              ↓
                                          Database
                                              ↓
                                          Analytics
                                              ↓
                                           Alerts
                                              ↓
                                         Dashboard
```

### Update Frequency

- **Video Feed**: 30 FPS (real-time)
- **Dashboard**: Every 30 frames (~1 second)
- **Analytics Window**: Last 5 minutes
- **Alert Evaluation**: Every dashboard update

### Performance

**Optimizations**:
- Frame-by-frame processing (no buffering)
- Periodic dashboard updates (not every frame)
- Efficient database queries with indexes
- Minimal UI re-rendering

**Expected Performance**:
- Webcam: 20-30 FPS (depending on hardware)
- Video File: 30+ FPS (no camera latency)
- Dashboard Update: <100ms
- Analytics Query: <50ms

## Configuration

### Time Windows

Default: 5 minutes for analytics and alerts

To change, modify in `production_app.py`:
```python
# Line ~350 and ~360
all_species = st.session_state.analytics.analyze_all_species(
    time_window_minutes=5,  # Change this
    min_count=1
)
```

### Alert Thresholds

Default configuration:
```python
AlertConfig(
    low_count_threshold=5,          # Low population threshold
    anomaly_spike_threshold=100.0,  # 100% increase for anomaly
    anomaly_min_count=3,            # Min count for anomaly
    decreasing_threshold=-10.0      # -10% for decreasing trend
)
```

To change, modify in `production_app.py` (line ~100):
```python
alert_config = AlertConfig(
    low_count_threshold=10,  # Stricter threshold
    # ... other settings
)
```

### Allowed Animal Classes

Default classes:
```python
{
    "dog", "cat", "horse", "cow", "elephant",
    "bear", "zebra", "giraffe", "bird", "sheep"
}
```

To change, modify in `production_app.py` (lines ~90 and ~250).

## Customization

### Colors

**Alert Colors** (in CSS section):
- HIGH: `#fee` background, `#dc3545` border (red)
- MEDIUM: `#fff3cd` background, `#ffc107` border (orange)
- LOW: `#d4edda` background, `#28a745` border (green)

**Trend Colors**:
- Increasing: `#28a745` (green)
- Decreasing: `#dc3545` (red)
- Stable: `#6c757d` (gray)

### Layout

**Column Widths**:
```python
col_video, col_dashboard = st.columns([2, 1])
```
- Video: 2/3 width
- Dashboard: 1/3 width

To change ratio, modify the list values (e.g., `[3, 1]` for wider video).

### Styling

All styles are in the `<style>` section at the top of `production_app.py`.

**Key Classes**:
- `.main-header`: Page title
- `.alert-high/medium/low`: Alert cards
- `.species-card`: Species activity cards
- `.no-wildlife`: No wildlife message

## Troubleshooting

### Dashboard Won't Start

**Issue**: Import errors or module not found

**Solution**:
```bash
# Ensure you're in the project root
cd /path/to/wildlife-monitoring

# Run with PYTHONPATH
PYTHONPATH=. python3 run_production_dashboard.py
```

### No Video Display

**Issue**: Camera not accessible

**Solution**:
- Check camera permissions
- Try different camera index (0, 1, 2)
- Ensure no other app is using camera

### Slow Performance

**Issue**: Low FPS or laggy UI

**Solutions**:
- Use smaller YOLOv8 model (yolov8n)
- Disable classification
- Reduce video resolution
- Close other applications

### No Species Showing

**Issue**: Dashboard shows "No wildlife detected"

**Solutions**:
- Check if animals are in camera view
- Verify detection confidence threshold
- Ensure database is recording sightings
- Check time window (may need longer than 5 min)

### Alerts Not Appearing

**Issue**: No alerts despite detections

**Solutions**:
- Wait for sufficient data (need previous period for trends)
- Check alert thresholds (may be too strict)
- Verify analytics is working (check species counts)
- Ensure database has data from previous period

## Best Practices

### For Demonstrations

1. **Pre-populate database**: Run system for 10-15 minutes before demo
2. **Use test video**: More reliable than live camera
3. **Clear database**: Start fresh for each demo
4. **Check lighting**: Ensure good visibility for detection

### For Production Use

1. **Regular database cleanup**: Clear old data periodically
2. **Monitor performance**: Check FPS and response times
3. **Adjust thresholds**: Tune for your specific environment
4. **Backup database**: Save important sighting data
5. **Log alerts**: Record critical alerts for review

### For Development

1. **Use test data**: Create sample database for testing
2. **Mock components**: Test UI without full pipeline
3. **Profile performance**: Identify bottlenecks
4. **Test edge cases**: No animals, many animals, etc.

## Comparison with Original Dashboard

| Feature | Original | Production |
|---------|----------|------------|
| Layout | Single column | Two-column (video + dashboard) |
| Species Info | Track summaries | Real-time counts + trends |
| Alerts | None | Full alert system with severity |
| Analytics | Basic stats | Time-based trends |
| Database | None | Full SQLite integration |
| UI Style | Developer-focused | Product-level, minimal |
| Updates | Manual | Automatic (every 30 frames) |
| No Wildlife | Generic message | Styled "No wildlife detected" |

## Files

- **Implementation**: `wildlife_monitoring/dashboard/production_app.py`
- **Launcher**: `run_production_dashboard.py`
- **Documentation**: `docs/PRODUCTION_DASHBOARD.md` (this file)
- **Original**: `wildlife_monitoring/dashboard/app.py` (preserved)

## See Also

- [Analytics Module](SIGHTINGS_ANALYTICS.md) - Underlying analytics
- [Alert System](ALERT_SYSTEM.md) - Alert generation
- [Database Module](DATABASE.md) - Data storage
- [Pipeline Module](MODULAR_PIPELINE.md) - Detection and tracking
