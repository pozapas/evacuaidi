// Vercel Serverless Function for Gemini Embeddings
// This API endpoint securely handles embedding generation for RAG

export default async function handler(req, res) {
    // Enable CORS for GitHub Pages
    res.setHeader('Access-Control-Allow-Origin', 'https://pozapas.github.io');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    // Handle preflight requests
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    
    // Only allow POST requests
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    
    try {
        const { text } = req.body;
        
        // Validate input
        if (!text || typeof text !== 'string' || text.trim().length === 0) {
            return res.status(400).json({ error: 'Text is required' });
        }
        
        if (text.length > 2000) {
            return res.status(400).json({ error: 'Text too long (max 2000 characters)' });
        }
        
        // Get API key from environment variables
        const apiKey = process.env.GEMINI_EMBEDDING_API_KEY;
        if (!apiKey) {
            console.error('GEMINI_EMBEDDING_API_KEY not found in environment variables');
            return res.status(500).json({ error: 'Server configuration error' });
        }
        
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: "models/gemini-embedding-001",
                content: {
                    parts: [{ text: text }]
                }
            })
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            console.error('Gemini Embedding API Error:', result);
            return res.status(500).json({ 
                error: 'Embedding service unavailable',
                details: result.error?.message || 'Unknown error'
            });
        }
        
        if (result.embedding && result.embedding.values) {
            return res.status(200).json({ 
                embedding: result.embedding.values 
            });
        } else {
            return res.status(500).json({ 
                error: 'Invalid response from embedding service'
            });
        }

    } catch (error) {
        console.error('Embedding API Error:', error);
        return res.status(500).json({ 
            error: 'Server error',
            message: 'Embedding service temporarily unavailable'
        });
    }
}
