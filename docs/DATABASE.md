# Wildlife Database Layer

## Overview

SQLite database layer for storing and querying wildlife sightings with automatic duplicate prevention and thread-safe operations.

---

## Features

✅ **Automatic table creation** - Database initialized on first use  
✅ **Duplicate prevention** - UNIQUE constraint on (track_id, frame_number)  
✅ **Thread-safe operations** - Safe for concurrent access  
✅ **Query utilities** - Built-in methods for common queries  
✅ **Context manager support** - Automatic cleanup with `with` statement  
✅ **Pipeline integration** - Helper functions for easy integration  

---

## Quick Start

### Basic Usage

```python
from wildlife_monitoring.database import WildlifeDatabase
from datetime import datetime

# Initialize database
db = WildlifeDatabase("wildlife_sightings.db")

# Insert a sighting
sighting_id = db.insert_sighting(
    species="Red Fox",
    confidence=0.85,
    track_id=1,
    frame_number=100,
    timestamp=datetime.now(),
    bbox=[100, 100, 300, 300]
)

print(f"Inserted sighting: {sighting_id}")

# Query sightings
sightings = db.get_sightings_by_track(track_id=1)
for s in sightings:
    print(f"Frame {s['frame_number']}: {s['species']} ({s['confidence']:.2f})")

# Close database
db.close()
```

### With Context Manager

```python
with WildlifeDatabase("wildlife_sightings.db") as db:
    db.insert_sighting(
        species="Deer",
        confidence=0.92,
        track_id=2,
        frame_number=100
    )
    
    stats = db.get_statistics()
    print(f"Total sightings: {stats['total_sightings']}")
# Database automatically closed
```

---

## Database Schema

### Sightings Table

```sql
CREATE TABLE sightings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species TEXT NOT NULL,
    confidence REAL NOT NULL,
    timestamp TEXT NOT NULL,
    track_id INTEGER NOT NULL,
    frame_number INTEGER DEFAULT 0,
    bbox TEXT,
    location TEXT,
    UNIQUE(track_id, frame_number)
)
```

**Columns**:
- `id`: Auto-incrementing primary key
- `species`: Species name (e.g., "Red Fox", "Deer")
- `confidence`: Classification confidence (0.0 to 1.0)
- `timestamp`: ISO format timestamp
- `track_id`: Tracking ID from centroid tracker
- `frame_number`: Frame number in video
- `bbox`: Bounding box as JSON string `[x1, y1, x2, y2]`
- `location`: Optional location information

**Indexes**:
- `idx_track_frame`: On (track_id, frame_number) for fast duplicate checking
- `idx_species`: On species for fast species queries
- `idx_timestamp`: On timestamp for temporal queries

---

## API Reference

### WildlifeDatabase Class

#### `__init__(db_path="wildlife_sightings.db")`

Initialize database connection and create tables.

```python
db = WildlifeDatabase("my_database.db")
```

#### `insert_sighting(...)`

Insert a new sighting record.

```python
sighting_id = db.insert_sighting(
    species="Red Fox",           # Required
    confidence=0.85,             # Required
    track_id=1,                  # Required
    frame_number=100,            # Required
    timestamp=datetime.now(),    # Optional (defaults to now)
    bbox=[100, 100, 300, 300],  # Optional
    location="Forest Area A"     # Optional
)
```

**Returns**: Inserted row ID, or `None` if duplicate

**Duplicate Prevention**: Automatically prevents duplicate inserts for the same `track_id` and `frame_number` using UNIQUE constraint.

#### `insert_sighting_batch(sightings)`

Insert multiple sightings in a single transaction.

```python
sightings = [
    ("Red Fox", 0.85, 1, 100, datetime.now(), None, None),
    ("Deer", 0.92, 2, 100, datetime.now(), None, None),
]

inserted_count = db.insert_sighting_batch(sightings)
print(f"Inserted {inserted_count} sightings")
```

**Returns**: Number of successfully inserted records

#### `get_sighting_by_id(sighting_id)`

Get a sighting by its ID.

```python
sighting = db.get_sighting_by_id(1)
print(sighting["species"])  # "Red Fox"
```

**Returns**: Dictionary with sighting data, or `None` if not found

#### `get_sightings_by_track(track_id)`

Get all sightings for a specific track.

```python
sightings = db.get_sightings_by_track(track_id=1)
for s in sightings:
    print(f"Frame {s['frame_number']}: {s['species']}")
```

**Returns**: List of sighting dictionaries, ordered by frame_number

#### `get_sightings_by_species(species, limit=None)`

Get all sightings of a specific species.

```python
deer_sightings = db.get_sightings_by_species("Deer", limit=10)
```

**Returns**: List of sighting dictionaries, ordered by timestamp (newest first)

#### `get_recent_sightings(limit=100)`

Get most recent sightings.

```python
recent = db.get_recent_sightings(limit=50)
```

**Returns**: List of sighting dictionaries, ordered by timestamp (newest first)

#### `get_species_count()`

Get count of sightings per species.

```python
counts = db.get_species_count()
# Returns: {"Red Fox": 10, "Deer": 25, ...}
```

**Returns**: Dictionary mapping species name to count

#### `get_statistics()`

Get database statistics.

```python
stats = db.get_statistics()
print(f"Total sightings: {stats['total_sightings']}")
print(f"Unique tracks: {stats['unique_tracks']}")
print(f"Unique species: {stats['unique_species']}")
```

**Returns**: Dictionary with:
- `total_sightings`: Total number of records
- `unique_tracks`: Number of unique track IDs
- `unique_species`: Number of unique species
- `species_counts`: Count per species
- `first_sighting`: Earliest timestamp
- `last_sighting`: Latest timestamp

#### `check_duplicate(track_id, frame_number)`

Check if a sighting already exists.

```python
exists = db.check_duplicate(track_id=1, frame_number=100)
if exists:
    print("Sighting already recorded")
```

**Returns**: `True` if duplicate exists, `False` otherwise

#### `delete_sighting(sighting_id)`

Delete a sighting by ID.

```python
deleted = db.delete_sighting(sighting_id=1)
```

**Returns**: `True` if deleted, `False` if not found

#### `clear_all_sightings()`

Delete all sightings from database.

```python
db.clear_all_sightings()  # WARNING: Cannot be undone!
```

---

## Pipeline Integration

### Helper Function: `save_pipeline_results_to_db()`

Automatically save pipeline results to database.

```python
from wildlife_monitoring.database import (
    WildlifeDatabase,
    save_pipeline_results_to_db
)
from wildlife_monitoring.pipeline.modular_pipeline import (
    process_frame_modular,
    create_modular_pipeline
)

# Initialize
db = WildlifeDatabase("wildlife.db")
detector, classifier, tracker = create_modular_pipeline()

# Process frame
state = process_frame_modular(
    frame, frame_num, detector, classifier, tracker,
    ALLOWED_ANIMALS, True, False
)

# Save to database (automatic duplicate prevention)
inserted_count = save_pipeline_results_to_db(db, state)
print(f"Saved {inserted_count} sightings")
```

### Helper Function: `get_track_history()`

Get complete history for a track.

```python
from wildlife_monitoring.database import get_track_history

history = get_track_history(db, track_id=1)
print(f"Track {history['track_id']}:")
print(f"  Species: {history['species']}")
print(f"  Total frames: {history['total_frames']}")
print(f"  Avg confidence: {history['avg_confidence']:.2f}")
print(f"  First seen: {history['first_seen']}")
print(f"  Last seen: {history['last_seen']}")
```

---

## Complete Example

### Video Processing with Database

```python
import cv2
from datetime import datetime
from wildlife_monitoring.database import (
    WildlifeDatabase,
    save_pipeline_results_to_db
)
from wildlife_monitoring.pipeline.modular_pipeline import (
    process_frame_modular,
    create_modular_pipeline
)

# Setup
ALLOWED_ANIMALS = {"dog", "cat", "horse", "cow", "elephant", "bear", "zebra", "giraffe"}

db = WildlifeDatabase("wildlife_video.db")
detector, classifier, tracker = create_modular_pipeline(
    allowed_animal_classes=ALLOWED_ANIMALS
)

# Process video
cap = cv2.VideoCapture("wildlife.mp4")
frame_num = 0
total_saved = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_num += 1
    
    # Process frame
    state = process_frame_modular(
        frame, frame_num, detector, classifier, tracker,
        ALLOWED_ANIMALS, True, False
    )
    
    # Save to database
    inserted = save_pipeline_results_to_db(db, state, datetime.now())
    total_saved += inserted
    
    if frame_num % 30 == 0:
        print(f"Frame {frame_num}: {inserted} sightings saved")

cap.release()

# Show results
print(f"\nTotal sightings saved: {total_saved}")

stats = db.get_statistics()
print(f"Unique tracks: {stats['unique_tracks']}")
print(f"Unique species: {stats['unique_species']}")

print("\nSpecies counts:")
for species, count in stats['species_counts'].items():
    print(f"  {species}: {count}")

db.close()
```

---

## Duplicate Prevention

The database automatically prevents duplicate sightings using a UNIQUE constraint on `(track_id, frame_number)`.

### How It Works

```python
# First insert - succeeds
id1 = db.insert_sighting(
    species="Red Fox",
    confidence=0.85,
    track_id=1,
    frame_number=100
)
print(f"Inserted: {id1}")  # Inserted: 1

# Duplicate insert - returns None
id2 = db.insert_sighting(
    species="Red Fox",
    confidence=0.85,
    track_id=1,
    frame_number=100  # Same track_id and frame_number
)
print(f"Inserted: {id2}")  # Inserted: None

# Different frame - succeeds
id3 = db.insert_sighting(
    species="Red Fox",
    confidence=0.82,
    track_id=1,
    frame_number=101  # Different frame_number
)
print(f"Inserted: {id3}")  # Inserted: 2
```

### Why This Matters

- **Prevents data duplication** when reprocessing frames
- **Ensures data integrity** in the database
- **No manual checking required** - handled automatically
- **Fast duplicate detection** using database index

---

## Thread Safety

The database uses a threading lock to ensure thread-safe operations:

```python
# Safe to use from multiple threads
import threading

def process_and_save(frame, frame_num):
    state = process_frame_modular(...)
    save_pipeline_results_to_db(db, state)

threads = [
    threading.Thread(target=process_and_save, args=(frame1, 1)),
    threading.Thread(target=process_and_save, args=(frame2, 2))
]

for t in threads:
    t.start()

for t in threads:
    t.join()
```

---

## Performance Tips

1. **Use batch inserts** for multiple sightings:
   ```python
   db.insert_sighting_batch(sightings)  # Faster than individual inserts
   ```

2. **Use context manager** for automatic cleanup:
   ```python
   with WildlifeDatabase("db.db") as db:
       # Operations
   # Automatically closed
   ```

3. **Check duplicates before insert** (optional):
   ```python
   if not db.check_duplicate(track_id, frame_num):
       db.insert_sighting(...)
   ```

4. **Use indexes** - Already created automatically:
   - `(track_id, frame_number)` for duplicate checking
   - `species` for species queries
   - `timestamp` for temporal queries

---

## Summary

✅ **Easy to use** - Simple API for common operations  
✅ **Automatic setup** - Tables created on initialization  
✅ **Duplicate prevention** - UNIQUE constraint handles it  
✅ **Thread-safe** - Safe for concurrent access  
✅ **Pipeline integration** - Helper functions included  
✅ **Query utilities** - Built-in methods for common queries  

**Result**: Robust database layer for wildlife monitoring! 🚀
