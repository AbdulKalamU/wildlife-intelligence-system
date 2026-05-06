# Railway Deployment Fix - PORT Variable Issue

## The Problem

Railway deployment was showing **502 Bad Gateway** error with this message in Deploy Logs:
```
Error: Invalid value for '--server.port' (env var: 'STREAMLIT_SERVER_PORT'): '$PORT' is not a valid integer.
```

## Root Cause

Railway was receiving the **literal string `"$PORT"`** instead of the actual port number (like `8501`).

### Why This Happened

Railway has a **priority order** for determining how to run your app:

1. **Procfile** (highest priority) ⚠️ This was the culprit!
2. **Dockerfile CMD**
3. **Auto-detection**

Even though we fixed the Dockerfile, Railway was using the `Procfile` which had:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

This command runs directly in Railway's process manager, which **doesn't expand environment variables** like `$PORT`.

## The Solution

### What We Fixed

**Procfile** (before):
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Procfile** (after):
```
web: sh -c "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"
```

### Why This Works

1. **`sh -c`**: Runs the command in a shell that can expand variables
2. **`${PORT:-8501}`**: Bash parameter expansion syntax
   - Uses `$PORT` if it exists
   - Falls back to `8501` if `$PORT` is not set
3. **Quotes**: Ensures the entire command is passed to the shell

## Technical Details

### Environment Variable Expansion

Different contexts handle `$PORT` differently:

| Context | `$PORT` Expansion | Works? |
|---------|------------------|--------|
| Procfile direct | ❌ No | `"$PORT"` literal string |
| Procfile with `sh -c` | ✅ Yes | Actual port number |
| Dockerfile CMD (JSON) | ❌ No | `"$PORT"` literal string |
| Dockerfile CMD with shell | ✅ Yes | Actual port number |

### Railway's Procfile Behavior

Railway's Procfile runs commands through its process manager, which:
- Does NOT expand environment variables in the command string
- Passes the command exactly as written
- Sets environment variables AFTER parsing the command

This is why `$PORT` became a literal string instead of being replaced with `8501`.

## Deployment Timeline

1. **Initial Issue**: libGL.so.1 missing (OpenCV dependency)
   - **Fix**: Added Dockerfile with `apt-get install libgl1`

2. **Second Issue**: PORT variable not expanding in Dockerfile
   - **Fix**: Changed Dockerfile CMD to use `sh -c`

3. **Third Issue** (Current): Procfile overriding Dockerfile
   - **Fix**: Updated Procfile to use `sh -c` with proper expansion

## Verification Steps

After Railway rebuilds (5-10 minutes):

1. **Check Deploy Logs** - Should see:
   ```
   Starting Container
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   
   You can now view your Streamlit app in your browser.
   ```

2. **Visit App** - https://web-production-e9ad8.up.railway.app
   - Should load without 502 error
   - Wildlife Intelligence Command Center should appear

3. **Test Features**:
   - ✅ Demo video upload
   - ✅ Image upload
   - ✅ Analytics dashboard
   - ❌ Webcam (not available in cloud)

## Files Modified

### Commit History
```
8dfbcf4 - Fix Procfile PORT variable expansion for Railway
106b56a - Fix Railway PORT variable expansion in Dockerfile CMD
3a27216 - Fix: Use libgl1 instead of libgl1-mesa-glx for Debian
```

### Changed Files
1. **Procfile** - Added shell expansion for PORT variable
2. **Dockerfile** - Added shell expansion for PORT variable (backup)

## Lessons Learned

### Railway Deployment Priority

Always check **all** deployment configuration files:
- `Procfile` (highest priority)
- `railway.toml`
- `Dockerfile`
- `nixpacks.toml`

### Environment Variable Best Practices

When using environment variables in commands:

✅ **DO**:
```bash
sh -c "command --port=${PORT:-8501}"
```

❌ **DON'T**:
```bash
command --port=$PORT
```

### Testing Locally

To test the exact command Railway will use:
```bash
# Simulate Railway's environment
export PORT=8501
sh -c "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"
```

## Alternative Solutions

If this fix doesn't work, other options:

### Option 1: Remove Procfile
Let Railway use Dockerfile CMD:
```bash
git rm Procfile
git commit -m "Remove Procfile, use Dockerfile CMD"
git push
```

### Option 2: Use railway.toml
Override with explicit command:
```toml
[deploy]
startCommand = "sh -c 'streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0'"
```

### Option 3: Use Streamlit Cloud
Streamlit Cloud is optimized for Streamlit apps and handles this automatically.

## Current Status

✅ **Fix Applied**: Procfile updated with shell expansion
⏳ **Waiting**: Railway to rebuild and deploy (5-10 minutes)
🎯 **Expected**: App should load successfully at https://web-production-e9ad8.up.railway.app

## Next Steps

1. Wait for Railway deployment to complete
2. Check Deploy Logs for successful startup
3. Visit the app URL to verify it loads
4. Test demo video upload feature
5. Celebrate! 🎉

---

**Last Updated**: May 6, 2026, 8:46 PM GMT+5:30
**Status**: Fix deployed, waiting for Railway rebuild
