# EvacuAIDi Presentation - Vercel Deployment Guide

This is the interactive presentation for Amir Rafe's PhD dissertation "EvacuAIDi: An AI-Driven, Causal-Informed Framework for Probabilistic and Disability-Inclusive Evacuation Guidance" from Utah State University (2025).

## Why Vercel Instead of GitHub Pages?

Your AI chatbot needs server-side functionality to:
- Keep API keys secure (not exposed to users)
- Handle real-time API requests to Google Gemini
- Process RAG (Retrieval-Augmented Generation) for intelligent responses

GitHub Pages can only serve static files, so the AI features won't work there.

## Quick Deployment Steps

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Save it - you'll need it for both embedding and generation

### 2. Deploy to Vercel (Easy Option)

#### Using Vercel Dashboard:

1. Go to [vercel.com](https://vercel.com) and sign up (free)
2. Click "Add New..." → "Project" 
3. Import your GitHub repository: `https://github.com/pozapas/evacuaidi-presentation`
4. Configure project settings:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave default)
   - **Build Command**: Leave empty
   - **Install Command**: `npm install`

5. **IMPORTANT**: Add Environment Variables before deploying:
   - `GEMINI_EMBEDDING_API_KEY` = Your Gemini API key
   - `GEMINI_GENERATION_API_KEY` = Your Gemini API key (same key)

6. Click "Deploy"

#### Using Vercel CLI (Alternative):

```bash
# Install Vercel CLI
npm install -g vercel

# In your project directory
vercel login
vercel

# Add environment variables
vercel env add GEMINI_EMBEDDING_API_KEY
vercel env add GEMINI_GENERATION_API_KEY

# Redeploy with env vars
vercel --prod
```

### 3. Test Your Deployment

1. Visit your Vercel URL (e.g., `https://evacuaidi-presentation.vercel.app`)
2. Scroll to "Ask AI Researcher" section  
3. Wait for "✅ Ready for Q&A!" message
4. Try asking: "What are the main research contributions?"

## How It Works

### Serverless Architecture
- **Frontend**: Your HTML/CSS/JS serves the presentation
- **Backend**: Vercel serverless functions (`/api/chat.js`, `/api/embeddings.js`) handle API calls
- **Security**: API keys stay server-side, never exposed to users

### File Structure
```
your-project/
├── index.html           # Main presentation
├── api/
│   ├── chat.js         # AI chat endpoint  
│   └── embeddings.js   # Text embeddings
├── vercel.json         # Vercel configuration
├── package.json        # Dependencies
└── Plots/              # Your research images
```

## Troubleshooting

### "❌ Configuration Error: API keys not found"
- Check that environment variables are set in Vercel dashboard
- Ensure you redeployed after adding environment variables
- Verify your Gemini API key is valid

### Chat not working
- Open browser developer tools (F12) → Console tab
- Look for error messages
- Check that `/api/chat` endpoint is accessible

### Need Help?
- Check Vercel function logs in your Vercel dashboard
- Ensure your Gemini API key has sufficient quota
- Contact Amir at amir.rafe@usu.edu for technical issues

## Cost

- **Vercel**: Free tier includes 100GB bandwidth, 6,000 function invocations/month
- **Gemini API**: Pay-per-use, very affordable for typical presentation usage
- **Total**: Likely $0-5/month for normal usage

## Migration from GitHub Pages

If you currently have this on GitHub Pages:
1. Keep GitHub Pages as a backup
2. Deploy to Vercel using steps above  
3. Update any links to point to your new Vercel URL
4. Your AI bot will now work properly!

## Contact

**Amir Rafe**  
PhD Candidate, Civil & Environmental Engineering  
Utah State University  
📧 amir.rafe@usu.edu  
🔗 GitHub: [@pozapas](https://github.com/pozapas)
