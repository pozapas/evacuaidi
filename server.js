// server.js - Backend server for EvacuAIDi application
const express = require('express');
const cors = require('cors');
const path = require('path');
const fetch = require('node-fetch');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// API keys from environment variables
const GEMINI_EMBEDDING_API_KEY = process.env.GEMINI_EMBEDDING_API_KEY;
const GEMINI_GENERATION_API_KEY = process.env.GEMINI_GENERATION_API_KEY;

// Check if API keys are available
if (!GEMINI_EMBEDDING_API_KEY || !GEMINI_GENERATION_API_KEY) {
  console.error('Error: Missing API keys in environment variables');
  process.exit(1);
}

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Proxy route for Gemini Embedding API
app.post('/api/embedding', async (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
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
  res.json({ status: 'ok', message: 'EvacuAIDi API server is running' });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`API keys loaded: ${GEMINI_EMBEDDING_API_KEY ? 'Embedding ✓' : 'Embedding ✗'} | ${GEMINI_GENERATION_API_KEY ? 'Generation ✓' : 'Generation ✗'}`);
});
