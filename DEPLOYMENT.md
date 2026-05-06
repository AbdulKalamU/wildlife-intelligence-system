# Railway Deployment Guide

Complete guide for deploying Wildlife Intelligence Command Center to Railway.

## Prerequisites

- GitHub account
- Railway account (https://railway.app)
- Git installed locally

## Deployment Files

The following files are configured for Railway deployment:

### 1. Procfile
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```
- Tells Railway how to start the application
- Binds to Railway's dynamic port
- Listens on all network interfaces

### 2. runtime.txt
```
python-3.11.9
```
- Specifies Python version
- Railway will use this exact version

### 3. .streamlit/config.toml
```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = true
port = 8501

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"

[theme]
base = "dark"
primaryColor = "#667eea"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
```
- Configures Streamlit for production
- Sets dark theme
- Disables usage stats
- Enables headless mode

### 4. requirements.txt
- Uses `opencv-python-headless` for cloud compatibility
- Pins numpy to 1.x for PyTorch compatibility
- Includes all necessary dependencies

## Step-by-Step Deployment

### Step 1: Prepare Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Railway deployment"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/wildlife-monitoring.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Authorize Railway to access your repositories
6. Select your wildlife-monitoring repository
7. Railway will automatically:
   - Detect the Procfile
   - Install dependencies from requirements.txt
   - Use Python version from runtime.txt
   - Start the application

### Step 3: Configure Settings (Optional)

1. In Railway dashboard, click on your project
2. Go to "Settings"
3. Under "Environment", you can add variables if needed
4. Under "Networking", Railway will provide a public URL

### Step 4: Access Application

1. Railway will provide a URL like: `https://wildlife-monitoring-production.up.railway.app`
2. Click the URL to access your deployed application
3. Application will be live and accessible worldwide

## Important Notes

### Webcam Limitations

⚠️ **Railway servers do NOT have physical webcams**

The application includes safety checks:
- Detects when webcam is unavailable
- Shows user-friendly message
- Prompts to use Upload option instead

### Model Loading

- First load will download YOLO models (~6MB)
- Models are cached using `@st.cache_resource`
- Subsequent loads are instant

### Memory Considerations

- Railway free tier: 512MB RAM
- Hobby tier: 8GB RAM
- For production use, consider Hobby tier or higher

### Performance

- First request may be slow (cold start)
- Subsequent requests are fast
- Models stay in memory between requests

## Troubleshooting

### Issue: Build Fails

**Cause**: Missing dependencies or incompatible versions

**Solution**:
1. Check requirements.txt has all dependencies
2. Ensure opencv-python-headless (not opencv-python)
3. Check Railway build logs for specific errors

### Issue: Application Crashes on Start

**Cause**: Port binding or configuration issues

**Solution**:
1. Verify Procfile uses `$PORT` variable
2. Check .streamlit/config.toml is present
3. Review Railway logs for error messages

### Issue: Webcam Not Working

**Cause**: This is expected behavior

**Solution**:
- Use Upload option for video files
- Application will show helpful message

### Issue: Slow Performance

**Cause**: Free tier limitations or large video files

**Solution**:
1. Upgrade to Hobby tier
2. Process smaller video files
3. Reduce video resolution

### Issue: Out of Memory

**Cause**: Processing large videos on free tier

**Solution**:
1. Upgrade Railway plan
2. Process shorter videos
3. Reduce batch size

## Monitoring

### Railway Dashboard

- View logs in real-time
- Monitor memory usage
- Check request metrics
- View deployment history

### Application Health

- Railway provides health checks
- Application auto-restarts on crashes
- Logs are retained for debugging

## Updating Deployment

### Push Updates

```bash
# Make changes to code
git add .
git commit -m "Update feature"
git push origin main
```

Railway will automatically:
1. Detect the push
2. Rebuild the application
3. Deploy the new version
4. Zero-downtime deployment

## Cost Considerations

### Free Tier
- $5 credit per month
- 512MB RAM
- Shared CPU
- Good for demos and testing

### Hobby Tier ($5/month)
- 8GB RAM
- Dedicated resources
- Better performance
- Recommended for production

## Security

### Best Practices

1. **No Secrets in Code**: Use Railway environment variables
2. **HTTPS**: Railway provides automatic HTTPS
3. **CORS**: Disabled in config for security
4. **XSRF Protection**: Enabled in config

### Environment Variables

If you need to add secrets:
1. Go to Railway dashboard
2. Click on your project
3. Go to "Variables"
4. Add key-value pairs
5. Access in code via `os.environ.get('KEY')`

## Backup and Data

### Database

- SQLite database is ephemeral on Railway
- Data is lost on redeployment
- For persistent data, use Railway's PostgreSQL addon

### Persistent Storage

To add persistent storage:
1. In Railway dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Update app.py to use PostgreSQL instead of SQLite

## Support

### Railway Support
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Email: team@railway.app

### Application Issues
- Open issue on GitHub
- Check logs in Railway dashboard
- Review troubleshooting section above

## Deployment Checklist

Before deploying, ensure:

- [x] Procfile exists and is correct
- [x] runtime.txt specifies Python 3.11
- [x] .streamlit/config.toml is configured
- [x] requirements.txt uses opencv-python-headless
- [x] Cloud camera safety implemented
- [x] Model caching added
- [x] Debug logs removed
- [x] Code pushed to GitHub
- [x] Railway project created
- [x] Deployment successful
- [x] Application accessible via URL

## Success Criteria

Your deployment is successful when:

✅ Application loads without errors
✅ Upload functionality works
✅ Video processing works
✅ Analytics charts render
✅ Database operations work
✅ Export functionality works
✅ No console errors
✅ Responsive on mobile

## Next Steps

After successful deployment:

1. Test all features with uploaded videos
2. Monitor performance and memory usage
3. Consider upgrading to Hobby tier for production
4. Set up custom domain (optional)
5. Configure analytics (optional)
6. Add monitoring alerts (optional)

## Conclusion

Your Wildlife Intelligence Command Center is now deployed and accessible worldwide via Railway!

**Deployment URL**: Check Railway dashboard for your unique URL

**Launch Command**: Automatic via Procfile

**Status**: Production Ready ✅
