# Secure Deployment Guide for EvacuAIDi GitHub Pages

This guide shows how to deploy EvacuAIDi to GitHub Pages with a secure backend that protects your API keys.

## 🔐 Architecture Overview

```
GitHub Pages (Frontend) → Vercel API (Backend) → Google Gemini API
     ↑                           ↑                      ↑
User Interface              API Keys Hidden         AI Processing
```

**Benefits:**
- ✅ API keys never exposed to users
- ✅ Free hosting on GitHub Pages + Vercel
- ✅ CORS properly configured
- ✅ Rate limiting and validation

## 🚀 Step-by-Step Deployment

### Step 1: Deploy Backend to Vercel

1. **Create Vercel Account:**
   - Go to [vercel.com](https://vercel.com)
   - Sign up/login with GitHub

2. **Deploy Backend:**
   - Click "New Project" in Vercel
   - Import your GitHub repository
   - Vercel will auto-detect the `vercel.json` config

3. **Set Environment Variables in Vercel:**
   - Go to your project settings in Vercel
   - Navigate to "Environment Variables"
   - Add these variables:
     ```
     GEMINI_EMBEDDING_API_KEY = your_actual_embedding_key
     GEMINI_GENERATION_API_KEY = your_actual_generation_key
     ```

4. **Get Your Vercel URL:**
   - After deployment, note your Vercel URL (e.g., `https://evacuaidi-presentation.vercel.app`)

### Step 2: Update Frontend Configuration

1. **Edit `api-config-secure.js`:**
   ```javascript
   // Update this line with your Vercel URL
   API_BASE_URL: 'https://evacuaidi-presentation.vercel.app',
   ```

2. **Update `index.html`:**
   ```html
   <!-- Change this line -->
   <script src="api-config.js"></script>
   <!-- To this -->
   <script src="api-config-secure.js"></script>
   ```

### Step 3: Deploy to GitHub Pages

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add secure backend configuration"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to your repository settings
   - Navigate to "Pages"
   - Select "Deploy from branch"
   - Choose "main" branch
   - Save

3. **Update CORS in Backend:**
   - Once you have your GitHub Pages URL (`https://pozapas.github.io/evacuaidi-presentation/`)
   - Update the CORS origin in `api/chat.js` and `api/embed.js`:
     ```javascript
     res.setHeader('Access-Control-Allow-Origin', 'https://pozapas.github.io');
     ```
   - Redeploy to Vercel

## 🔧 Configuration Files

### Required Files:
- `api/chat.js` - Chat API endpoint
- `api/embed.js` - Embedding API endpoint  
- `vercel.json` - Vercel configuration
- `api-config-secure.js` - Secure frontend config

### Modified Files:
- `index.html` - Updated to use secure config
- Update any references from `api-config.js` to `api-config-secure.js`

## 🧪 Testing

1. **Test Backend:**
   ```bash
   curl -X POST https://evacuaidi-presentation.vercel.app/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is EvacuAIDi?"}'
   ```

2. **Test Frontend:**
   - Open your GitHub Pages URL
   - Try the AI chat feature
   - Check browser console for errors

## 🔒 Security Features

- **API Keys Protected:** Never exposed in client-side code
- **CORS Configured:** Only your domain can access the API
- **Input Validation:** Prevents malicious inputs
- **Rate Limiting:** Built-in request limits
- **Error Handling:** Graceful fallbacks for failures

## 🛠️ Troubleshooting

### Common Issues:

1. **CORS Error:**
   - Ensure the CORS origin matches your GitHub Pages URL exactly
   - Check for trailing slashes

2. **API Key Error:**
   - Verify environment variables are set in Vercel
   - Check variable names match exactly

3. **404 on API calls:**
   - Ensure `vercel.json` is in the root directory
   - Check that API functions are in `/api/` folder

4. **Chat not working:**
   - Open browser console (F12) for error messages
   - Verify the API_BASE_URL in `api-config-secure.js`

### Debug Commands:

```bash
# Check Vercel deployment
vercel --debug

# Test API endpoints
curl -X OPTIONS https://evacuaidi-presentation.vercel.app/api/chat
```

## 📝 Environment Variables Reference

Set these in your Vercel project settings:

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_EMBEDDING_API_KEY` | For RAG embeddings | `AIzaSy...` |
| `GEMINI_GENERATION_API_KEY` | For chat responses | `AIzaSy...` |

## 🎯 Final Checklist

- [ ] Backend deployed to Vercel
- [ ] Environment variables set in Vercel
- [ ] Frontend updated with Vercel URL
- [ ] CORS configured with GitHub Pages URL
- [ ] GitHub Pages enabled
- [ ] AI chat feature tested and working
- [ ] No API keys exposed in client code

Your EvacuAIDi presentation is now securely deployed with protected API keys! 🎉
