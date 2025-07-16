// Backend proxy server (deploy on Vercel, Netlify, or similar)
const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors({
    origin: ['https://pozapas.github.io', 'http://localhost:3000']
}));
app.use(express.json());

// Environment variables are loaded on the server side
const GEMINI_EMBEDDING_API_KEY = process.env.GEMINI_EMBEDDING_API_KEY;
const GEMINI_GENERATION_API_KEY = process.env.GEMINI_GENERATION_API_KEY;

// Proxy endpoint for chat completions
app.post('/api/chat', async (req, res) => {
    try {
        const { contents } = req.body;
        
        const response = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemma-3-27b-it:generateContent?key=${GEMINI_GENERATION_API_KEY}`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ contents })
            }
        );
        
        const result = await response.json();
        res.json(result);
        
    } catch (error) {
        console.error('Chat API Error:', error);
        res.status(500).json({ error: 'Failed to generate response' });
    }
});

// Proxy endpoint for embeddings
app.post('/api/embeddings', async (req, res) => {
    try {
        const { text } = req.body;
        
        const response = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=${GEMINI_EMBEDDING_API_KEY}`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: "models/gemini-embedding-001",
                    content: { parts: [{ text }] }
                })
            }
        );
        
        const result = await response.json();
        res.json(result);
        
    } catch (error) {
        console.error('Embedding API Error:', error);
        res.status(500).json({ error: 'Failed to generate embedding' });
    }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`Proxy server running on port ${PORT}`);
});

module.exports = app;
