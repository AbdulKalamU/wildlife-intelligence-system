"""
Wildlife Database Module

SQLite database layer for storing wildlife sightings.

Features:
- Automatic table creation
- Duplicate prevention (same track_id in same frame)
- Transaction support
- Query utilities
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import threading


@dataclass
class SightingRecord:
    """
    Record of a wildlife sighting.
    
    Attributes:
        id: Primary key (auto-generated)
        species: Species name
        confidence: Classification confidence (0-1)
        timestamp: When the sighting occurred
        track_id: Tracking ID from centroid tracker
        frame_number: Frame number in video
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        location: Optional location information
    """
    species: str
    confidence: float
    timestamp: datetime
    track_id: int
    frame_number: int = 0
    bbox: Optional[str] = None  # Stored as JSON string
    location: Optional[str] = None
    id: Optional[int] = None  # Auto-generated


class WildlifeDatabase:
    """
    SQLite database for wildlife monitoring system.
    
    Manages sightings table with automatic initialization and
    duplicate prevention.
    """
    
    def __init__(self, db_path: str = "wildlife_sightings.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._lock = threading.Lock()  # Thread-safe operations
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """
        Initialize database and create tables if they don't exist.
        
        Creates the 'sightings' table with the following schema:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - species: TEXT NOT NULL
        - confidence: REAL NOT NULL
        - timestamp: TEXT NOT NULL (ISO format)
        - track_id: INTEGER NOT NULL
        - frame_number: INTEGER DEFAULT 0
        - bbox: TEXT (JSON string)
        - location: TEXT
        
        Also creates an index on (track_id, frame_number) for fast
        duplicate checking.
        """
        with self._lock:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            cursor = self.connection.cursor()
            
            # Create sightings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sightings (
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
            """)
            
            # Create index for fast lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_track_frame 
                ON sightings(track_id, frame_number)
            """)
            
            # Create index for species queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_species 
                ON sightings(species)
            """)
            
            # Create index for timestamp queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON sightings(timestamp)
            """)
            
            self.connection.commit()
    
    def insert_sighting(
        self,
        species: str,
        confidence: float,
        track_id: int,
        frame_number: int = 0,
        timestamp: Optional[datetime] = None,
        bbox: Optional[List[float]] = None,
        location: Optional[str] = None
    ) -> Optional[int]:
        """
        Insert a new sighting record.
        
        Automatically prevents duplicate inserts for the same track_id
        in the same frame using UNIQUE constraint.
        
        Args:
            species: Species name (e.g., "Red Fox")
            confidence: Classification confidence (0.0 to 1.0)
            track_id: Tracking ID from centroid tracker
            frame_number: Frame number in video
            timestamp: When sighting occurred (defaults to now)
            bbox: Bounding box [x1, y1, x2, y2] (optional)
            location: Location information (optional)
            
        Returns:
            Inserted row ID, or None if duplicate
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Convert bbox to JSON string if provided
        bbox_str = None
        if bbox is not None:
            import json
            bbox_str = json.dumps(bbox)
        
        with self._lock:
            cursor = self.connection.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO sightings 
                    (species, confidence, timestamp, track_id, frame_number, bbox, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    species,
                    confidence,
                    timestamp.isoformat(),
                    track_id,
                    frame_number,
                    bbox_str,
                    location
                ))
                
                self.connection.commit()
                return cursor.lastrowid
            
            except sqlite3.IntegrityError:
                # Duplicate entry (same track_id and frame_number)
                return None
    
    def insert_sighting_batch(
        self,
        sightings: List[Tuple[str, float, int, int, datetime, Optional[str], Optional[str]]]
    ) -> int:
        """
        Insert multiple sightings in a single transaction.
        
        More efficient than multiple individual inserts.
        
        Args:
            sightings: List of tuples (species, confidence, track_id, 
                      frame_number, timestamp, bbox_json, location)
            
        Returns:
            Number of successfully inserted records
        """
        with self._lock:
            cursor = self.connection.cursor()
            inserted_count = 0
            
            for sighting in sightings:
                try:
                    cursor.execute("""
                        INSERT INTO sightings 
                        (species, confidence, timestamp, track_id, frame_number, bbox, location)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, sighting)
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    # Skip duplicates
                    continue
            
            self.connection.commit()
            return inserted_count
    
    def get_sighting_by_id(self, sighting_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a sighting by its ID.
        
        Args:
            sighting_id: Sighting ID
            
        Returns:
            Dictionary with sighting data, or None if not found
        """
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, species, confidence, timestamp, track_id, 
                       frame_number, bbox, location
                FROM sightings
                WHERE id = ?
            """, (sighting_id,))
            
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_dict(row)
    
    def get_sightings_by_track(self, track_id: int) -> List[Dict[str, Any]]:
        """
        Get all sightings for a specific track.
        
        Args:
            track_id: Track ID
            
        Returns:
            List of sighting dictionaries
        """
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, species, confidence, timestamp, track_id, 
                       frame_number, bbox, location
                FROM sightings
                WHERE track_id = ?
                ORDER BY frame_number ASC
            """, (track_id,))
            
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def get_sightings_by_species(
        self,
        species: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all sightings of a specific species.
        
        Args:
            species: Species name
            limit: Maximum number of results (None = all)
            
        Returns:
            List of sighting dictionaries
        """
        with self._lock:
            cursor = self.connection.cursor()
            
            query = """
                SELECT id, species, confidence, timestamp, track_id, 
                       frame_number, bbox, location
                FROM sightings
                WHERE species = ?
                ORDER BY timestamp DESC
            """
            
            if limit is not None:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (species,))
            
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def get_recent_sightings(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get most recent sightings.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of sighting dictionaries
        """
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, species, confidence, timestamp, track_id, 
                       frame_number, bbox, location
                FROM sightings
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def get_species_count(self) -> Dict[str, int]:
        """
        Get count of sightings per species.
        
        Returns:
            Dictionary mapping species name to count
        """
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT species, COUNT(*) as count
                FROM sightings
                GROUP BY species
                ORDER BY count DESC
            """)
            
            rows = cursor.fetchall()
            return {row[0]: row[1] for row in rows}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics:
                - total_sightings: Total number of records
                - unique_tracks: Number of unique track IDs
                - unique_species: Number of unique species
                - species_counts: Count per species
                - first_sighting: Earliest timestamp
                - last_sighting: Latest timestamp
        """
        with self._lock:
            cursor = self.connection.cursor()
            
            # Total sightings
            cursor.execute("SELECT COUNT(*) FROM sightings")
            total_sightings = cursor.fetchone()[0]
            
            # Unique tracks
            cursor.execute("SELECT COUNT(DISTINCT track_id) FROM sightings")
            unique_tracks = cursor.fetchone()[0]
            
            # Unique species
            cursor.execute("SELECT COUNT(DISTINCT species) FROM sightings")
            unique_species = cursor.fetchone()[0]
            
            # Species counts
            species_counts = self.get_species_count()
            
            # First and last sighting
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM sightings")
            first_sighting, last_sighting = cursor.fetchone()
            
            return {
                "total_sightings": total_sightings,
                "unique_tracks": unique_tracks,
                "unique_species": unique_species,
                "species_counts": species_counts,
                "first_sighting": first_sighting,
                "last_sighting": last_sighting
            }
    
    def check_duplicate(self, track_id: int, frame_number: int) -> bool:
        """
        Check if a sighting already exists for this track in this frame.
        
        Args:
            track_id: Track ID
            frame_number: Frame number
            
        Returns:
            True if duplicate exists, False otherwise
        """
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM sightings
                WHERE track_id = ? AND frame_number = ?
            """, (track_id, frame_number))
            
            count = cursor.fetchone()[0]
            return count > 0
    
    def delete_sighting(self, sighting_id: int) -> bool:
        """
        Delete a sighting by ID.
        
        Args:
            sighting_id: Sighting ID
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM sightings WHERE id = ?", (sighting_id,))
            self.connection.commit()
            return cursor.rowcount > 0
    
    def clear_all_sightings(self):
        """
        Delete all sightings from database.
        
        WARNING: This cannot be undone!
        """
        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM sightings")
            self.connection.commit()
    
    def _row_to_dict(self, row: Tuple) -> Dict[str, Any]:
        """
        Convert database row to dictionary.
        
        Args:
            row: Database row tuple
            
        Returns:
            Dictionary with column names as keys
        """
        import json
        
        # Parse bbox JSON if present
        bbox = None
        if row[6] is not None:
            try:
                bbox = json.loads(row[6])
            except:
                bbox = None
        
        return {
            "id": row[0],
            "species": row[1],
            "confidence": row[2],
            "timestamp": row[3],
            "track_id": row[4],
            "frame_number": row[5],
            "bbox": bbox,
            "location": row[7]
        }
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor - ensure connection is closed."""
        self.close()
