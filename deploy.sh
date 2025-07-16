#!/bin/bash

# EvacuAIDi Vercel Deployment Script
# This script helps deploy your presentation to Vercel with proper configuration

echo "🚀 EvacuAIDi Vercel Deployment Helper"
echo "======================================"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
else
    echo "✅ Vercel CLI found"
fi

# Check if logged in to Vercel
echo ""
echo "🔐 Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    echo "❌ Not logged in to Vercel. Please login:"
    vercel login
else
    echo "✅ Logged in to Vercel"
fi

echo ""
echo "📋 Pre-deployment checklist:"
echo "1. ✅ Vercel CLI installed"
echo "2. ✅ Logged in to Vercel"
echo "3. ⚠️  Do you have your Gemini API key ready?"
echo ""

read -p "Do you have your Gemini API key from Google AI Studio? (y/n): " has_api_key

if [ "$has_api_key" != "y" ]; then
    echo ""
    echo "🔑 Please get your API key first:"
    echo "1. Go to: https://makersuite.google.com/app/apikey"
    echo "2. Create a new API key"
    echo "3. Copy it and come back"
    echo ""
    exit 1
fi

echo ""
echo "🚀 Starting deployment..."

# Deploy to Vercel
vercel --prod

echo ""
echo "🔧 Setting up environment variables..."
echo "Please enter your Gemini API key when prompted:"

# Add environment variables
vercel env add GEMINI_EMBEDDING_API_KEY production
vercel env add GEMINI_GENERATION_API_KEY production

echo ""
echo "♻️  Redeploying with environment variables..."

# Redeploy with environment variables
vercel --prod

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Visit your Vercel deployment URL"
echo "2. Navigate to the 'Ask AI Researcher' section"
echo "3. Look for '✅ Ready for Q&A!' message"
echo "4. Test the chatbot functionality"
echo ""
echo "🔍 If something doesn't work:"
echo "- Check Vercel function logs in your dashboard"
echo "- Verify your API key is valid and has quota"
echo "- Open browser console (F12) for error messages"
echo ""
echo "📧 Need help? Contact amir.rafe@usu.edu"
