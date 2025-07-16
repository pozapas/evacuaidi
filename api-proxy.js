// API proxy to avoid exposing keys
// This would go in a serverless function (Vercel, Netlify, etc.)

export default async function handler(req, res) {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', 'https://pozapas.github.io');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    const { endpoint, ...params } = req.body;
    
    // Your actual API key (stored as environment variable)
    const apiKey = process.env.GEMINI_API_KEY;
    
    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/${endpoint}?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        res.status(200).json(data);
    } catch (error) {
        res.status(500).json({ error: 'API request failed' });
    }
}
