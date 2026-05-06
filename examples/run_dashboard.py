"""
Example script to run the Streamlit dashboard.

This script launches the wildlife monitoring dashboard with real-time
pipeline integration.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from wildlife_monitoring.dashboard import run_dashboard


if __name__ == "__main__":
    print("=" * 70)
    print("Wildlife Monitoring Dashboard")
    print("=" * 70)
    print("\nStarting Streamlit dashboard...")
    print("The dashboard will open in your browser automatically.")
    print("\nFeatures:")
    print("  • Real-time video processing")
    print("  • Wildlife detection with YOLOv8")
    print("  • Species classification with ResNet50")
    print("  • Object tracking across frames")
    print("  • Live statistics and track summaries")
    print("\nPress Ctrl+C to stop the dashboard.")
    print("=" * 70)
    print()
    
    run_dashboard()
