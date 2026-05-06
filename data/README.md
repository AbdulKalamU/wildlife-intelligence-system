# Data Directory

This directory contains data files for the wildlife monitoring system.

## Directory Structure

```
data/
├── models/          # Model weights and configurations
├── videos/          # Input video files
└── outputs/         # Processed results and outputs
```

## Models Directory

Place your YOLOv8 model weights and classification models here:
- `yolov8n.pt` - YOLOv8 nano model (default)
- `yolov8s.pt` - YOLOv8 small model
- `yolov8m.pt` - YOLOv8 medium model
- Custom trained models

## Videos Directory

Place your input video files here for processing:
- Supported formats: MP4, AVI, MOV
- Recommended resolution: 720p or 1080p
- Frame rate: 24-30 FPS

## Outputs Directory

Processed results will be saved here:
- Annotated videos with detections
- Detection logs (JSON/CSV)
- Track histories
- Analytics reports
- Alert logs

## Getting Started

1. Download a YOLOv8 model:
   ```bash
   # The model will be downloaded automatically on first run
   # Or manually download from: https://github.com/ultralytics/ultralytics
   ```

2. Add your video files to the `videos/` directory

3. Run the system and check `outputs/` for results

## Notes

- Large model files (*.pt, *.pth) are excluded from version control
- Video files are excluded from version control
- Output files are excluded from version control
- Keep this directory structure intact for proper system operation
