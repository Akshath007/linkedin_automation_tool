# 🚀 Deployment Guide - LinkedIn Sales Automation Tool

This guide will help you deploy the LinkedIn Sales Automation Tool locally and on cloud platforms.

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- A Google Cloud account with Gemini API access (API key provided)

## 🏠 Local Deployment

### Option 1: Quick Start (Recommended)

1. **Clone or download the project files**
2. **Run the automated setup:**
   ```bash
   python run.py
   ```
   This will automatically install dependencies and start the app.

### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the setup:**
   ```bash
   python test_app.py
   ```

3. **Start the application:**
   ```bash
   streamlit run app.py
   ```

The app will be available at `http://localhost:8501`

## ☁️ Cloud Deployment

### Streamlit Community Cloud

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: LinkedIn Sales Automation Tool"
   git branch -M main
   git remote add origin https://github.com/yourusername/linkedin-sales-automation.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Click "Deploy"

### Heroku Deployment

1. **Deploy to Heroku:**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## 🧪 Testing Your Deployment

1. **Run the test suite:**
   ```bash
   python test_app.py
   ```

2. **Check these features:**
   - [ ] Campaign creation works
   - [ ] Prospect analysis generates messages
   - [ ] Database saves data correctly
   - [ ] All pages load without errors

## 🔧 Troubleshooting

### Common Issues:

**1. Import Errors:**
```bash
pip install --upgrade -r requirements.txt
```

**2. Database Issues:**
- Delete `linkedin_automation.db` and restart the app
- Check file permissions

**3. API Errors:**
- Verify Gemini API key is correct
- Check internet connection
- Ensure API quotas aren't exceeded

**4. Streamlit Issues:**
```bash
streamlit cache clear
```

---

**Happy Deploying! 🚀**
