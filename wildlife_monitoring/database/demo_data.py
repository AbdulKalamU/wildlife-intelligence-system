"""
Demo data generator for Wildlife Intelligence Command Center.
Generates realistic sample data for demonstration purposes.
"""

from datetime import datetime, timedelta
import random
import json
from typing import List, Dict
import sqlite3


class DemoDataGenerator:
    """Generate realistic demo data for wildlife monitoring."""
    
    # Realistic wildlife species
    SPECIES = [
        "Labrador Retriever", "Leopard Cat", "Eagle", "Wild Horse",
        "Bison", "African Elephant", "Grizzly Bear", "Plains Zebra",
        "Masai Giraffe", "Bighorn Sheep"
    ]
    
    ZONES = ['A', 'B', 'C', 'D']
    
    def __init__(self, db_path: str = "wildlife_monitoring.db"):
        """Initialize demo data generator."""
        self.db_path = db_path
    
    def generate_demo_sightings(self, count: int = 100) -> List[Dict]:
        """
        Generate demo sightings data.
        
        Args:
            count: Number of sightings to generate
            
        Returns:
            List of sighting dictionaries
        """
        sightings = []
        base_time = datetime.now() - timedelta(hours=2)  # Start 2 hours ago
        
        # Create realistic patterns
        for i in range(count):
            # Time progression (spread over 2 hours)
            timestamp = base_time + timedelta(minutes=i * 1.2)
            
            # Species distribution (some more common than others)
            species_weights = [15, 12, 8, 10, 7, 5, 6, 9, 4, 8]  # Weighted distribution
            species = random.choices(self.SPECIES, weights=species_weights)[0]
            
            # Confidence (higher for common species)
            if species in ["Labrador Retriever", "Leopard Cat", "Wild Horse"]:
                confidence = random.uniform(0.75, 0.95)
            else:
                confidence = random.uniform(0.60, 0.85)
            
            # Zone distribution (Zone A and B more active)
            zone_weights = [30, 25, 25, 20]
            zone = random.choices(self.ZONES, weights=zone_weights)[0]
            
            # Track ID (simulate multiple tracks)
            track_id = random.randint(1, 30)
            
            # Frame number
            frame_number = i * 30  # Simulate 30 FPS
            
            sighting = {
                'timestamp': timestamp.isoformat(),
                'species': species,
                'confidence': confidence,
                'zone': zone,
                'track_id': track_id,
                'frame_number': frame_number,
                'bbox_x1': random.randint(50, 400),
                'bbox_y1': random.randint(50, 300),
                'bbox_x2': random.randint(450, 800),
                'bbox_y2': random.randint(350, 600)
            }
            
            sightings.append(sighting)
        
        return sightings
    
    def load_demo_data_to_db(self, count: int = 100):
        """
        Load demo data directly into the database.
        
        Args:
            count: Number of sightings to generate
        """
        sightings = self.generate_demo_sightings(count)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table if not exists (matching actual schema)
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
        
        # Insert demo data (store zone in location field)
        for sighting in sightings:
            try:
                # Store zone in location field as "Zone X"
                location = f"Zone {sighting['zone']}"
                
                # Create bbox JSON string
                bbox_json = json.dumps([
                    sighting['bbox_x1'],
                    sighting['bbox_y1'],
                    sighting['bbox_x2'],
                    sighting['bbox_y2']
                ])
                
                cursor.execute("""
                    INSERT INTO sightings 
                    (timestamp, species, confidence, track_id, frame_number, bbox, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sighting['timestamp'],
                    sighting['species'],
                    sighting['confidence'],
                    sighting['track_id'],
                    sighting['frame_number'],
                    bbox_json,
                    location
                ))
            except sqlite3.IntegrityError:
                # Skip duplicates
                continue
        
        conn.commit()
        conn.close()
        
        return len(sightings)
    
    def generate_demo_events(self, count: int = 50) -> List[Dict]:
        """
        Generate demo event log entries.
        
        Args:
            count: Number of events to generate
            
        Returns:
            List of event dictionaries
        """
        events = []
        base_time = datetime.now() - timedelta(hours=1)
        
        # Define event types with proper templates
        event_templates = [
            ('new_track', '{species} entered Zone {zone}', 0.4),
            ('zone_change', '{species} moved from Zone {from_zone} to Zone {zone}', 0.3),
            ('alert', '🚨 {species} entered Restricted Zone D', 0.15),
            ('alert', '⭐ Rare species detected: {species}', 0.15),
        ]
        
        # Rare species for special alerts
        rare_species = ["African Elephant", "Grizzly Bear", "Masai Giraffe"]
        
        for i in range(count):
            timestamp = base_time + timedelta(minutes=i * 1.2)
            species = random.choice(self.SPECIES)
            zone = random.choice(self.ZONES)
            track_id = random.randint(1, 30)
            
            # Weighted random choice of event type
            event_type, message_template, _ = random.choices(
                event_templates,
                weights=[t[2] for t in event_templates]
            )[0]
            
            # Generate message based on template
            if 'from_zone' in message_template:
                from_zone = random.choice(self.ZONES)
                to_zone = random.choice([z for z in self.ZONES if z != from_zone])
                message = message_template.format(
                    species=species,
                    from_zone=from_zone,
                    zone=to_zone
                )
                zone = to_zone
            elif 'Restricted Zone D' in message_template:
                # Only create this alert if actually in Zone D
                if zone == 'D':
                    message = message_template.format(species=species, zone=zone)
                else:
                    continue  # Skip this event
            elif 'Rare species' in message_template:
                # Only create this alert for rare species
                if species in rare_species:
                    message = message_template.format(species=species, zone=zone)
                else:
                    continue  # Skip this event
            else:
                message = message_template.format(species=species, zone=zone)
            
            event = {
                'timestamp': timestamp,
                'species': species,
                'zone': zone,
                'track_id': track_id,
                'type': event_type,
                'message': message
            }
            
            events.append(event)
        
        return events
    
    def get_demo_summary_stats(self) -> Dict:
        """
        Get summary statistics for demo data.
        
        Returns:
            Dictionary with summary stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total animals
        cursor.execute("SELECT COUNT(*) FROM sightings")
        total_animals = cursor.fetchone()[0]
        
        # Unique species
        cursor.execute("SELECT COUNT(DISTINCT species) FROM sightings")
        total_species = cursor.fetchone()[0]
        
        # Species breakdown
        cursor.execute("""
            SELECT species, COUNT(*) as count 
            FROM sightings 
            GROUP BY species 
            ORDER BY count DESC
        """)
        species_counts = cursor.fetchall()
        
        # Zone distribution
        cursor.execute("""
            SELECT zone, COUNT(*) as count 
            FROM sightings 
            GROUP BY zone
        """)
        zone_counts = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_animals': total_animals,
            'total_species': total_species,
            'species_counts': species_counts,
            'zone_counts': zone_counts
        }


def load_demo_data(db_path: str = "wildlife_monitoring.db", count: int = 100) -> Dict:
    """
    Convenience function to load demo data.
    
    Args:
        db_path: Path to database
        count: Number of sightings to generate
        
    Returns:
        Summary statistics
    """
    generator = DemoDataGenerator(db_path)
    sightings_count = generator.load_demo_data_to_db(count)
    stats = generator.get_demo_summary_stats()
    
    return {
        'sightings_loaded': sightings_count,
        'stats': stats
    }


if __name__ == "__main__":
    # Test demo data generation
    result = load_demo_data(count=100)
    print(f"Loaded {result['sightings_loaded']} demo sightings")
    print(f"Total animals: {result['stats']['total_animals']}")
    print(f"Total species: {result['stats']['total_species']}")
    print("\nSpecies breakdown:")
    for species, count in result['stats']['species_counts']:
        print(f"  {species}: {count}")
