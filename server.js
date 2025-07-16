// server.js - Backend server for EvacuAIDi application
const express = require('express');
const cors = require('cors');
const path = require('path');
const fetch = require('node-fetch');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// API keys from environment variables with fallbacks for development
const GEMINI_EMBEDDING_API_KEY = process.env.GEMINI_EMBEDDING_API_KEY || process.env.EMBEDDING_API_KEY || '';
const GEMINI_GENERATION_API_KEY = process.env.GEMINI_GENERATION_API_KEY || process.env.GENERATION_API_KEY || '';

// Check if API keys are available - just log warning instead of exiting
if (!GEMINI_EMBEDDING_API_KEY || !GEMINI_GENERATION_API_KEY) {
  console.warn('Warning: Missing API keys in environment variables - some functionality may be limited');
  console.warn('Note: Add these to your environment variables or .env file if needed');
}

// Middleware
app.use(cors({
  origin: '*', // Allow all origins for development - restrict this in production
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Proxy route for Gemini Embedding API
app.post('/api/embedding', async (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }
    
    if (!GEMINI_EMBEDDING_API_KEY) {
      return res.status(401).json({ 
        error: 'API key missing',
        message: 'Embedding API key is not configured',
        embeddings: null,
        // Return a mock embedding for development purposes
        values: new Array(768).fill(0).map(() => Math.random() - 0.5)
      });
    }

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=${GEMINI_EMBEDDING_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: "models/gemini-embedding-001",
          content: {
            parts: [{ text: text.substring(0, 2000) }]
          }
        })
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API Error: ${response.status}`, errorText);
      return res.status(response.status).json({ 
        error: `Google API error: ${response.status}`,
        details: errorText
      });
    }

    const result = await response.json();
    res.json(result);
  } catch (error) {
    console.error('Server error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Proxy route for Gemini Generation API
app.post('/api/generate', async (req, res) => {
  try {
    const { prompt } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }
    
    if (!GEMINI_GENERATION_API_KEY) {
      return res.status(401).json({
        error: 'API key missing',
        message: 'Generation API key is not configured',
        candidates: [{
          content: {
            parts: [{
              text: "I'm sorry, but the AI service is currently unavailable. The API key for text generation is missing. Please contact the administrator to set up the API keys properly. In the meantime, you can explore the dissertation content on this website manually."
            }]
          },
          finishReason: "STOP"
        }]
      });
    }

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemma-3-27b-it:generateContent?key=${GEMINI_GENERATION_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [
            {
              role: "user",
              parts: [{ text: prompt }]
            }
          ]
        })
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API Error: ${response.status}`, errorText);
      return res.status(response.status).json({ 
        error: `Google API error: ${response.status}`,
        details: errorText
      });
    }

    const result = await response.json();
    res.json(result);
  } catch (error) {
    console.error('Server error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'EvacuAIDi API server is running',
    environment: process.env.NODE_ENV || 'development',
    embeddings_api: GEMINI_EMBEDDING_API_KEY ? 'configured' : 'missing',
    generation_api: GEMINI_GENERATION_API_KEY ? 'configured' : 'missing',
    server_time: new Date().toISOString()
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`API keys loaded: ${GEMINI_EMBEDDING_API_KEY ? 'Embedding ✓' : 'Embedding ✗'} | ${GEMINI_GENERATION_API_KEY ? 'Generation ✓' : 'Generation ✗'}`);
});
