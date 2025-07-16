const handler = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  try {
    const embeddingKey = process.env.GEMINI_EMBEDDING_API_KEY;
    const generationKey = process.env.GEMINI_GENERATION_API_KEY;
    
    const diagnostics = {
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'unknown',
      hasEmbeddingKey: !!embeddingKey,
      hasGenerationKey: !!generationKey,
      embeddingKeyLength: embeddingKey ? embeddingKey.length : 0,
      generationKeyLength: generationKey ? generationKey.length : 0,
      embeddingKeyPrefix: embeddingKey ? embeddingKey.substring(0, 10) + '...' : 'NOT_FOUND',
      generationKeyPrefix: generationKey ? generationKey.substring(0, 10) + '...' : 'NOT_FOUND',
      availableEnvVars: Object.keys(process.env).filter(key => 
        key.includes('GEMINI') || key.includes('API') || key.includes('KEY')
      ),
      vercelInfo: {
        region: process.env.VERCEL_REGION,
        url: process.env.VERCEL_URL,
        env: process.env.VERCEL_ENV
      }
    };

    // Test a simple embedding API call if keys are available
    if (embeddingKey) {
      try {
        const testApiUrl = `https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key=${embeddingKey}`;
        const testResponse = await fetch(testApiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: "models/text-embedding-004",
            content: { parts: [{ text: "test" }] }
          })
        });
        
        diagnostics.embeddingApiTest = {
          status: testResponse.status,
          statusText: testResponse.statusText,
          success: testResponse.ok
        };
        
        if (!testResponse.ok) {
          const errorText = await testResponse.text();
          diagnostics.embeddingApiTest.error = errorText;
        }
      } catch (error) {
        diagnostics.embeddingApiTest = {
          error: error.message,
          success: false
        };
      }
    }

    res.status(200).json(diagnostics);

  } catch (error) {
    res.status(500).json({
      error: 'Test endpoint error',
      message: error.message,
      stack: error.stack
    });
  }
};

export default handler;
