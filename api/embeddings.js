// /api/embeddings.js - Serverless function for generating embeddings
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
    const { text } = req.body;
    
    if (!text || typeof text !== 'string') {
      console.error('Invalid text input:', { text, type: typeof text });
      return res.status(400).json({ error: 'Text is required and must be a string' });
    }

    const apiKey = process.env.GEMINI_EMBEDDING_API_KEY;
    if (!apiKey) {
      console.error('GEMINI_EMBEDDING_API_KEY not found in environment variables');
      console.error('Available env vars:', Object.keys(process.env).filter(key => key.includes('GEMINI')));
      return res.status(500).json({ error: 'API configuration error: GEMINI_EMBEDDING_API_KEY not found' });
    }

    console.log('Processing embedding request for text length:', text.length);

    // Call Google Gemini Embedding API
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=${apiKey}`;
    
    const requestBody = {
      model: "models/gemini-embedding-001",
      content: {
        parts: [{ text: text }]
      }
    };

    console.log('Making API request to:', apiUrl.replace(apiKey, 'HIDDEN_KEY'));
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Gemini Embedding API error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      return res.status(response.status).json({ 
        error: `Embedding API request failed: ${response.status}`,
        details: errorText,
        apiUrl: apiUrl.replace(apiKey, 'HIDDEN_KEY')
      });
    }

    const result = await response.json();
    console.log('Embedding API success, embedding length:', result.embedding?.values?.length || 0);
    res.status(200).json(result);

  } catch (error) {
    console.error('Embeddings API error:', {
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
