# Railway Deployment Troubleshooting Guide

## Current Issue: 502 Bad Gateway

**What it means**: The deployment succeeded, but the application is crashing when it tries to start.

## Common Causes & Solutions

### 1. Model Download Timeout
**Problem**: YOLOv8 model (yolov8n.pt) downloads on first run, which can timeout on Railway.

**Solution**: Pre-include the model in the repository
```bash
# Download model locally
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Add to git (if not already there)
git add yolov8n.pt
git commit -m "Include YOLOv8 model for Railway deployment"
git push
```

### 2. Memory Issues
**Problem**: Railway free tier has limited memory. Loading YOLOv8 + ResNet50 + Streamlit can exceed limits.

**Solution**: Optimize model loading
- Use smaller models
- Implement lazy loading
- Add memory limits to Dockerfile

### 3. Port Binding Issues
**Problem**: App not listening on the correct port.

**Current Status**: ✅ FIXED - Using `${PORT:-8501}` in Dockerfile

### 4. Missing System Dependencies
**Problem**: OpenCV requires system libraries.

**Current Status**: ✅ FIXED - Dockerfile installs libgl1, libglib2.0-0, etc.

### 5. Database Initialization
**Problem**: SQLite database file permissions or initialization issues.

**Solution**: Ensure database directory is writable
```dockerfile
# Add to Dockerfile
RUN mkdir -p /app/data && chmod 777 /app/data
```

### 6. Streamlit Configuration
**Problem**: Streamlit server settings not compatible with Railway.

**Current Status**: ✅ FIXED - Using `.streamlit/config.toml`

## Debugging Steps

### Step 1: Check Deploy Logs
Go to Railway Dashboard → Deploy Logs tab

Look for:
- Import errors
- Model download messages
- Memory errors
- Port binding errors
- Timeout messages

### Step 2: Check Build Logs
Verify Docker image built successfully with all dependencies.

### Step 3: Test Locally with Docker
```bash
# Build the same Docker image locally
docker build -t wildlife-app .

# Run with same environment
docker run -p 8501:8501 -e PORT=8501 wildlife-app
```

### Step 4: Add Health Check Endpoint
Add a simple health check to verify app startup:
```python
# In app.py
@st.cache_resource
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

## Railway-Specific Issues

### Free Tier Limitations
- **Memory**: 512 MB RAM (can be exceeded by ML models)
- **CPU**: Shared CPU (slower model loading)
- **Timeout**: 5 minutes for first request
- **Sleep**: Apps sleep after 5 minutes of inactivity

### Recommended Railway Plan
For ML applications like this, consider:
- **Hobby Plan**: $5/month, 1GB RAM, no sleep
- **Pro Plan**: $20/month, 8GB RAM, better performance

## Alternative Deployment Options

If Railway continues to have issues:

### 1. Streamlit Cloud (Recommended for Streamlit apps)
- Free tier available
- Optimized for Streamlit
- Easy GitHub integration
- **Limitation**: No webcam support (same as Railway)

### 2. Hugging Face Spaces
- Free GPU available
- Good for ML models
- Streamlit support

### 3. Google Cloud Run
- Pay-per-use
- Better for ML workloads
- More memory available

### 4. AWS EC2 / Lightsail
- Full control
- Can support webcam (with proper setup)
- More expensive

## Next Steps

1. **Show me the Deploy Logs** - This will tell us the exact error
2. **Check if yolov8n.pt is in the repo** - If not, we need to add it
3. **Consider memory optimization** - May need to reduce model size
4. **Try Streamlit Cloud** - Might be better suited for this app

## Quick Fixes to Try

### Fix 1: Add Model to Repo
```bash
# If yolov8n.pt exists locally
git add yolov8n.pt
git commit -m "Add YOLOv8 model for deployment"
git push
```

### Fix 2: Increase Timeout
Add to `railway.toml`:
```toml
[deploy]
startCommand = "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### Fix 3: Add Startup Logging
Modify app.py to log startup progress:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting Wildlife Intelligence Command Center...")
logger.info("Loading models...")
# ... rest of code
```

## Contact Information

If issues persist:
1. Share Deploy Logs
2. Share Build Logs  
3. Check Railway status page: https://status.railway.app/
4. Railway Discord: https://discord.gg/railway
