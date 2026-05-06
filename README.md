# Wildlife Intelligence Command Center

Real-time wildlife monitoring system with AI-powered detection, tracking, and analytics.

**Status**: ✅ Deployed on Railway with Docker support (v2.0)

## Features

- **Real-time Detection**: YOLOv8-based animal detection
- **Species Classification**: ResNet50 wildlife classification
- **Multi-Zone Tracking**: DeepSORT tracking across 4 zones
- **Smart Alerts**: Intelligent alert system for critical events
- **Advanced Analytics**: Real-time charts and statistics
- **Data Export**: CSV and JSON export functionality

## Quick Start

### Local Installation

```bash
# Clone repository
git clone <repository-url>
cd wildlife-monitoring

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Railway Deployment

#### Prerequisites
- GitHub account
- Railway account (https://railway.app)

#### Deployment Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo>
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect the Procfile and deploy

3. **Configure Environment**
   - Railway will use `runtime.txt` for Python version
   - Railway will use `Procfile` for startup command
   - Railway will use `.streamlit/config.toml` for Streamlit settings

4. **Access Application**
   - Railway will provide a public URL
   - Application will be accessible at: `https://your-app.railway.app`

#### Important Notes for Cloud Deployment

⚠️ **Webcam Limitations**: Railway servers do not have physical webcams. The application will automatically detect this and prompt users to upload video files instead.

✅ **Recommended Usage**: Use the "Upload" option to process video files in cloud deployment.

## Usage

1. Select video source (Webcam or Upload)
2. Click **Start** to begin monitoring
3. View live feed with zone overlays
4. Monitor species detection and alerts
5. Analyze data with real-time charts
6. Export sightings data

## System Requirements

### Local Development
- Python 3.11+
- Webcam (optional)
- 4GB RAM minimum
- GPU recommended for optimal performance

### Cloud Deployment (Railway)
- Python 3.11 (specified in runtime.txt)
- 512MB RAM minimum
- Video upload required (no webcam support)

## Technology Stack

- **Detection**: YOLOv8
- **Tracking**: DeepSORT
- **Classification**: ResNet50
- **Frontend**: Streamlit
- **Analytics**: Plotly
- **Database**: SQLite

## Project Structure

```
├── app.py                      # Main application
├── requirements.txt            # Dependencies
├── Procfile                    # Railway deployment config
├── runtime.txt                 # Python version
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── README.md                   # This file
├── wildlife_monitoring/        # Core modules
│   ├── detection/             # YOLO detection
│   ├── classification/        # Species classification
│   ├── tracking/              # Object tracking
│   ├── database/              # Data persistence
│   ├── analytics/             # Analytics engine
│   └── alerts/                # Alert system
├── config/                     # Configuration
├── data/                       # Data directory
└── tests/                      # Test suite
```

## Troubleshooting

### Local Issues

**Issue**: Camera not found
**Solution**: Check camera index (0, 1, 2...) or use Upload option

**Issue**: Slow performance
**Solution**: Reduce video resolution or use GPU

**Issue**: Module not found
**Solution**: Ensure all dependencies installed: `pip install -r requirements.txt`

### Railway Deployment Issues

**Issue**: Webcam not working
**Solution**: This is expected. Use Upload option for video files.

**Issue**: Application timeout
**Solution**: Railway free tier has limitations. Upgrade plan if needed.

**Issue**: Model loading slow
**Solution**: Models are cached after first load. Subsequent loads are faster.

**Issue**: Out of memory
**Solution**: Process smaller videos or upgrade Railway plan.

## Environment Variables

No environment variables required for basic operation.

## License

MIT License

## Contact

For questions or support, please open an issue on GitHub.

## Deployment Checklist

- [x] Procfile created
- [x] runtime.txt created
- [x] .streamlit/config.toml created
- [x] requirements.txt updated (opencv-python-headless)
- [x] Cloud camera safety added
- [x] Model caching implemented
- [x] Debug logs removed
- [x] Deployment documentation added

## Launch Commands

**Local**: `streamlit run app.py`

**Railway**: Automatic via Procfile (`streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`)
