# Deploying EvacuAIDi Presentation to Vercel

This guide will help you deploy your interactive dissertation presentation to Vercel with proper Gemini API configuration.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Select "Create API key in new project" or choose an existing project
4. Copy the generated API key (starts with `AIza...`)
5. **Important**: Keep this key secure and never commit it to your repository

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Connect Repository**:
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"
   - Import your Git repository
   - Select the root directory of your project

2. **Configure Environment Variables**:
   - In the deployment settings, find "Environment Variables"
   - Add a new variable:
     - **Name**: `GEMINI_API_KEY`
     - **Value**: Your Gemini API key (paste the key you copied)
     - **Environment**: All (Production, Preview, Development)
   - Click "Add"

3. **Deploy**:
   - Click "Deploy"
   - Vercel will automatically detect your project settings from `vercel.json`
   - Wait for deployment to complete (usually 1-2 minutes)

### Option B: Deploy via CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Set Environment Variable**:
   ```bash
   vercel env add GEMINI_API_KEY production
   ```
   - When prompted, paste your Gemini API key
   - Repeat for preview and development environments if needed

4. **Deploy**:
   ```bash
   vercel --prod
   ```

## Step 3: Configure Custom Domain (Optional)

1. In your Vercel dashboard, go to your project
2. Navigate to "Settings" → "Domains"
3. Add your custom domain (e.g., `evacuaidi.yourdomain.com`)
4. Follow Vercel's instructions to configure DNS

## Step 4: Verify Deployment

1. **Test the Website**:
   - Visit your Vercel URL (e.g., `https://your-project.vercel.app`)
   - Navigate to the "Ask AI Researcher" section
   - Wait for the "✅ AI system ready!" message

2. **Test AI Chat**:
   - Try asking: "What are the main research contributions of EvacuAIDi?"
   - You should receive a detailed response about the research

## Troubleshooting

### Common Issues:

1. **"Environment configuration not loaded" Error**:
   - Check that `GEMINI_API_KEY` is properly set in Vercel environment variables
   - Redeploy the project after adding the environment variable

2. **"API key not configured" Error**:
   - Ensure your Gemini API key is valid and active
   - Check Google AI Studio for API usage limits

3. **Chat Not Working**:
   - Open browser developer tools (F12)
   - Check the Console tab for error messages
   - Verify network requests to `/api/chat` are successful

4. **Plots Not Loading**:
   - Ensure all plot images are properly uploaded to your repository
   - Check that GitHub URLs in the HTML are accessible

### Environment Variable Management:

```bash
# View current environment variables
vercel env ls

# Add new environment variable
vercel env add VARIABLE_NAME

# Remove environment variable
vercel env rm VARIABLE_NAME
```

## Security Best Practices

1. **Never commit API keys**: The `.gitignore` file is configured to exclude environment files
2. **Use environment variables**: API keys are securely stored in Vercel's environment system
3. **Rotate keys regularly**: Generate new API keys periodically for security
4. **Monitor usage**: Check Google AI Studio for unusual API usage patterns

## File Structure

Your project should have this structure:
```
/
├── index.html              # Main presentation page
├── js/
│   └── config.js          # API configuration and client code
├── api/
│   └── chat.js            # Serverless function for Gemini API
├── Plots/                 # Research plots and images
├── vercel.json            # Vercel configuration
├── package.json           # Project dependencies
├── .gitignore            # Files to exclude from Git
└── DEPLOYMENT_GUIDE.md   # This file
```

## Cost Considerations

- **Vercel**: Free tier includes 100GB bandwidth and 6,000 serverless function invocations
- **Gemini API**: Check [Google AI pricing](https://ai.google.dev/pricing) for current rates
- **Typical usage**: Academic presentation sites usually stay within free tiers

## Support

If you encounter issues:
1. Check Vercel's [documentation](https://vercel.com/docs)
2. Review Google AI [Gemini API docs](https://ai.google.dev/docs)
3. Contact Vercel support through their dashboard

## Updates and Maintenance

To update your deployment:
1. Push changes to your Git repository
2. Vercel will automatically redeploy (if auto-deployment is enabled)
3. Or manually trigger deployment from Vercel dashboard

Your EvacuAIDi presentation should now be live and fully functional with AI chat capabilities!
