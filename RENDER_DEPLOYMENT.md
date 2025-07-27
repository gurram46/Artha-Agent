# 🚀 Render Deployment Guide - Artha-AI SAndeep System

## 🎯 Why Render is Perfect for Your AI System

✅ **No timeout limits** - SAndeep AI agents can run as long as needed  
✅ **Auto-scaling** - Handles traffic spikes automatically  
✅ **Simple Git deployment** - Push to deploy  
✅ **Free tier available** - Great for testing  
✅ **Built-in HTTPS** - Secure by default  
✅ **Environment variables** - Easy configuration  

---

## 🚀 Quick Deploy (5 minutes)

### Prerequisites:
1. **GitHub account** with your code
2. **Google AI API key** from: https://makersuite.google.com/app/apikey
3. **Render account** (free): https://render.com

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Deploy Backend on Render

1. **Go to Render Dashboard** → "New" → "Web Service"
2. **Connect GitHub** and select your repository
3. **Configure Backend:**
   - **Name:** `artha-ai-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `cd backend && uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Starter` (free) or `Standard` (better performance)

4. **Set Environment Variables:**
   ```
   GOOGLE_AI_API_KEY = your_google_ai_api_key_here
   ENVIRONMENT = production
   PYTHONPATH = /opt/render/project/src/backend
   ```

5. **Click "Create Web Service"**

### Step 3: Deploy Frontend on Render

1. **Create New Web Service** for frontend
2. **Configure Frontend:**
   - **Name:** `artha-ai-frontend`
   - **Environment:** `Node`
   - **Build Command:** `cd frontend && npm ci && npm run build`
   - **Start Command:** `cd frontend && npm start`
   - **Plan:** `Starter` (free)

3. **Set Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL = https://your-backend-url.onrender.com
   NODE_ENV = production
   ```

4. **Click "Create Web Service"**

---

## 🔧 Configuration Files Created

### ✅ `render.yaml` - Infrastructure as Code
```yaml
services:
  - type: web
    name: artha-ai-backend
    env: python
    buildCommand: "./build.sh"
    startCommand: "cd backend && uvicorn api_server:app --host 0.0.0.0 --port $PORT"
```

### ✅ `build.sh` - Backend Build Script
- Installs all Python dependencies
- Sets up SAndeep AI components
- Configures Google ADK
- Verifies MCP data files

### ✅ `requirements.txt` - Root Dependencies
- FastAPI and core backend
- Google AI for SAndeep
- All required libraries

### ✅ `next.config.ts` - Frontend Optimization
- Standalone output for better performance
- API route rewrites for backend communication
- Production optimizations

---

## 🎯 What Works After Deployment

### ✅ SAndeep Multi-Agent System:
- **Data Analyst Agent** - Market research
- **Trading Analyst Agent** - Investment strategies  
- **Execution Analyst Agent** - Broker recommendations
- **Risk Analyst Agent** - Risk assessment

### ✅ Fi Money MCP Integration:
- Real financial data processing
- Demo mode with sample data
- 6 JSON file structure support

### ✅ Features Available:
- Investment recommendations
- Portfolio analysis
- Risk assessment
- 6 major Indian broker integration
- Chat interface with AI agents

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. Backend Build Fails:
```bash
# Check logs in Render dashboard
# Usually missing Google AI API key
```

#### 2. Frontend Can't Connect:
```bash
# Verify NEXT_PUBLIC_API_URL is set correctly
# Should be: https://your-backend-url.onrender.com
```

#### 3. SAndeep Agents Not Responding:
```bash
# Check Google AI API key is valid
# Verify API quota not exceeded
# Check backend logs for initialization errors
```

#### 4. Demo Data Not Loading:
```bash
# Ensure mcp-docs folder is in repository
# Check build logs for file copy errors
```

### Health Checks:
- **Backend Health:** `https://your-backend-url.onrender.com/health`
- **SAndeep Status:** `https://your-backend-url.onrender.com/api/sandeep-investment-recommendations/status`
- **Demo Data:** `https://your-backend-url.onrender.com/financial-data?demo=true`

---

## 💰 Costs

### Free Tier (Starter Plan):
- ✅ **750 hours/month** - Enough for development
- ✅ **512MB RAM** - Sufficient for basic usage
- ⚠️ **Sleeps after 15min** - Cold starts for AI

### Paid Tier (Standard Plan - $7/month):
- ✅ **Always on** - No cold starts
- ✅ **1GB RAM** - Better for AI workloads
- ✅ **Faster builds** - Quicker deployments

**Recommendation:** Start with free tier, upgrade if needed.

---

## 🚀 Production Optimizations

### For Heavy Usage:
1. **Upgrade to Standard plan** - No cold starts
2. **Enable auto-scaling** - Handle traffic spikes
3. **Monitor logs** - Check for AI agent performance
4. **Set up alerts** - Get notified of issues

### Performance Tips:
- **Cache AI responses** when possible
- **Monitor memory usage** for SAndeep agents
- **Use CDN** for frontend assets (Render includes this)
- **Optimize API calls** to reduce latency

---

## 🎉 Success!

After deployment, you'll have:

- ✅ **Live frontend:** `https://your-frontend-url.onrender.com`
- ✅ **API backend:** `https://your-backend-url.onrender.com`
- ✅ **SAndeep AI agents** running 24/7
- ✅ **Fi Money integration** with real data
- ✅ **Auto-deploy** on every Git push
- ✅ **HTTPS** and custom domains
- ✅ **Monitoring** and logs included

Your Artha-AI SAndeep investment system is now live! 🎯

---

## 📞 Need Help?

1. **Check Render logs** first (most issues shown here)
2. **Verify environment variables** are set correctly
3. **Test with demo mode** to isolate issues
4. **Check Google AI API status** and quota

**Your integrated SAndeep system is production-ready on Render!** 🚀