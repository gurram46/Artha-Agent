# 🚀 Quick Start Guide - Investment Agent

Get your Investment Agent running in minutes! Choose the setup option that works best for you.

## 📋 Requirements

- Python 3.9 or higher
- Internet connection
- **Choose ONE:**
  - Google AI Studio API Key (Free) - **Recommended for beginners**
  - Google Cloud Project with Vertex AI - **For production use**

## 🎯 Setup Options

### Option 1: One-Click Setup (Windows) ⚡
**Easiest way to get started!**

1. Double-click `start.bat`
2. Follow the prompts to choose your setup (AI Studio or Vertex AI)
3. Enter your API key or project details
4. Start chatting with your investment advisor!

### Option 2: Automated Setup 🤖
**Cross-platform automated setup**

```bash
python setup.py
```

Choose from:
1. **Google AI Studio** (Free, easy setup)
2. **Google Cloud Vertex AI** (Production-ready)
3. **Both options** (Switch between them later)

### Option 3: Manual Setup 🔧
**For advanced users**

#### For Google AI Studio:
```bash
# Install dependencies
pip install -r requirements.txt

# Get API key from https://aistudio.google.com/app/apikey
# Create .env file
echo "GOOGLE_API_KEY=your-api-key-here" > .env

# Run the agent
python run_with_ai_studio.py
```

#### For Google Cloud Vertex AI:
```bash
# Install dependencies
pip install -r requirements.txt

# Set up Google Cloud authentication
gcloud auth application-default login

# Create .env file
echo "GOOGLE_GENAI_USE_VERTEXAI=true" > .env
echo "GOOGLE_CLOUD_PROJECT=your-project-id" >> .env
echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env

# Run the agent
python run_with_vertex_ai.py
```

## 🔑 Getting Your Credentials

### Google AI Studio (Free & Easy)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and use it in setup

### Google Cloud Vertex AI (Production)
1. Create a [Google Cloud Project](https://console.cloud.google.com/)
2. Enable Vertex AI API
3. Set up authentication: `gcloud auth application-default login`
4. Use your project ID in setup

For detailed Vertex AI setup, see [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md)

## 🎮 Running the Agent

After setup, you can run:

- **Google AI Studio**: `python run_with_ai_studio.py`
- **Vertex AI**: `python run_with_vertex_ai.py`
- **Interactive mode**: `python run_interactive.py`
- **Test mode**: `python run_local_test.py`

## 💬 Try These Questions

Once your agent is running, try asking:

```
"I'm 25 and want to start investing ₹10,000 monthly. What should I do?"

"Which ELSS funds are best for tax saving?"

"Should I invest in large-cap or mid-cap funds?"

"How should I diversify my portfolio?"

"What are the best SIP options for 5 years?"
```

## 🎯 What Your Agent Can Do

✅ **Investment Planning** - Personalized strategies for Indian markets  
✅ **SIP Recommendations** - Systematic investment plans  
✅ **Risk Assessment** - Portfolio risk analysis  
✅ **Tax Planning** - ELSS, PPF, and other tax-saving options  
✅ **Market Analysis** - Current trends and insights  
✅ **Fund Selection** - Best mutual funds for your goals  

## 🆘 Troubleshooting

### "API key not found"
- Check your `.env` file has the correct API key
- Make sure there are no extra spaces or quotes

### "Project not found" (Vertex AI)
- Verify your project ID is correct
- Ensure you're authenticated: `gcloud auth list`

### "Permission denied"
- For Vertex AI: Check your IAM roles
- Run `gcloud auth application-default login` again

### "Module not found"
- Run `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.9+)

## 🔄 Switching Between Options

You can switch between Google AI Studio and Vertex AI by editing your `.env` file:

**For AI Studio:**
```
GOOGLE_API_KEY=your-api-key
# GOOGLE_GENAI_USE_VERTEXAI=true
# GOOGLE_CLOUD_PROJECT=your-project
```

**For Vertex AI:**
```
# GOOGLE_API_KEY=your-api-key
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1
```

## 🎉 You're Ready!

Your Investment Agent is now ready to help you navigate the Indian financial markets. Start with simple questions and explore its capabilities!

**Need more help?** Check out:
- [README.md](README.md) - Full documentation
- [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md) - Detailed Vertex AI setup
- Ask your agent: "How can you help me with investments?"