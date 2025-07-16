// /api/chat.js - Serverless function for AI chat
export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { contents } = req.body;
    
    if (!contents || !Array.isArray(contents)) {
      return res.status(400).json({ error: 'Invalid request format' });
    }

    const apiKey = process.env.GEMINI_GENERATION_API_KEY;
    if (!apiKey) {
      console.error('GEMINI_GENERATION_API_KEY not found in environment variables');
      console.error('Available env vars:', Object.keys(process.env).filter(key => key.includes('GEMINI')));
      return res.status(500).json({ 
        error: 'API configuration error: GEMINI_GENERATION_API_KEY not found',
        debug: {
          nodeEnv: process.env.NODE_ENV,
          vercelEnv: process.env.VERCEL_ENV,
          availableGeminiVars: Object.keys(process.env).filter(key => key.includes('GEMINI'))
        }
      });
    }

    console.log('Processing chat request with', contents.length, 'messages');

    // Call Google Gemini API
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
    
    console.log('Making chat API request to Gemini API');
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ contents })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Gemini API error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      return res.status(response.status).json({ 
        error: `API request failed: ${response.status}`,
        details: errorText
      });
    }

    const result = await response.json();
    console.log('Chat API success, response received');
    res.status(200).json(result);

  } catch (error) {
    console.error('Chat API error:', {
      message: error.message,
      stack: error.stack,
      name: error.name
    });
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message,
      type: error.name
    });
  }
}
