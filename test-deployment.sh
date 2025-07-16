#!/bin/bash

# EvacuAIDi API Configuration Test Script
# This script helps verify that your Vercel deployment is working correctly

echo "🚀 EvacuAIDi API Configuration Test"
echo "=================================="
echo

# Check if environment variables are set locally (optional)
if [ -f ".env" ]; then
    echo "📁 Local .env file detected"
    if grep -q "GEMINI_" .env; then
        echo "✅ GEMINI API keys found in .env"
    else
        echo "⚠️  No GEMINI API keys in .env (this is OK for Vercel deployment)"
    fi
else
    echo "📁 No local .env file (this is OK for Vercel deployment)"
fi

echo

# Test if we can reach the API endpoints
BASE_URL="https://evacuaidi-presentation.vercel.app"

echo "🔍 Testing API endpoints..."
echo "Base URL: $BASE_URL"
echo

# Test the test endpoint
echo "Testing /api/test endpoint..."
curl -s -w "HTTP Status: %{http_code}\n" "$BASE_URL/api/test" | head -10
echo

# Instructions
echo "📋 Next Steps:"
echo "1. If you see 'hasEmbeddingKey: true' and 'hasGenerationKey: true', your API is configured correctly"
echo "2. If you see false values, add GEMINI_EMBEDDING_API_KEY and GEMINI_GENERATION_API_KEY to your Vercel dashboard"
echo "3. Get your API key from: https://aistudio.google.com/app/apikey"
echo "4. Add both environment variables with the SAME API key value"
echo "5. Redeploy your Vercel project"
echo

echo "🌐 Visit your site: $BASE_URL"
echo "💬 Test the chat: Go to the 'Ask AI Researcher' section"
