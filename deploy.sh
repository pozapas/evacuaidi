#!/bin/bash

# EvacuAIDi Backend Deployment Script
# This script helps deploy the backend proxy to Vercel

echo "🚀 EvacuAIDi Backend Deployment Helper"
echo "======================================"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "📦 Setting up Vercel project..."

# Initialize Vercel project
vercel

echo ""
echo "🔧 Next steps:"
echo "1. Go to your Vercel dashboard: https://vercel.com/dashboard"
echo "2. Find your project and go to Settings → Environment Variables"
echo "3. Add these environment variables:"
echo "   - GEMINI_EMBEDDING_API_KEY: [Your embedding API key]"
echo "   - GEMINI_GENERATION_API_KEY: [Your generation API key]"
echo "4. Redeploy your project: vercel --prod"
echo "5. Update env-config.js with your Vercel URL"
echo ""
echo "📋 Your Vercel project URL will be displayed above."
echo "Copy this URL and update the getBackendUrl() function in env-config.js"
echo ""
echo "✅ Deployment complete! Your AI chat should now work securely."
