export default async function handler(req, res) {
    // Enable CORS for frontend requests
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
        const { action, text, message, context } = req.body;
        const apiKey = process.env.GEMINI_API_KEY;

        if (!apiKey) {
            return res.status(500).json({ error: 'Gemini API key not configured' });
        }

        const baseUrl = 'https://generativelanguage.googleapis.com/v1beta';

        if (action === 'embedding') {
            // Generate embedding for RAG using correct Gemini embedding model
            const response = await fetch(`${baseUrl}/models/gemini-embedding-001:embedContent?key=${apiKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: "models/gemini-embedding-001",
                    content: {
                        parts: [{ text: text }]
                    }
                })
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Gemini embedding error:', errorData);
                return res.status(response.status).json({ error: 'Failed to generate embedding' });
            }

            const data = await response.json();
            return res.status(200).json({ embedding: data.embedding.values });

        } else if (action === 'chat') {
            // Generate chat response
            const prompt = buildPrompt(message, context);

            const response = await fetch(`${baseUrl}/models/gemma-3-27b-it:generateContent?key=${apiKey}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{ text: prompt }]
                    }],
                    generationConfig: {
                        temperature: 0.7,
                        maxOutputTokens: 1000,
                        topP: 0.9
                    }
                })
            });

            if (!response.ok) {
                const errorData = await response.text();
                console.error('Gemini chat error:', errorData);
                return res.status(response.status).json({ error: 'Failed to generate response' });
            }

            const data = await response.json();
            const botResponse = data.candidates[0].content.parts[0].text;

            return res.status(200).json({ response: botResponse });

        } else {
            return res.status(400).json({ error: 'Invalid action' });
        }

    } catch (error) {
        console.error('Chat API error:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}

function buildPrompt(userMessage, ragContext) {
    return `You are an AI research assistant specializing in the EvacuAIDi dissertation research on AI-driven, causal-informed framework for probabilistic and disability-inclusive evacuation guidance.

**Context from Research:**
${ragContext}

**User Question:** ${userMessage}

**Instructions:**
- Provide accurate, detailed answers based on the research context
- Focus on quantitative findings and specific methodological details
- If the question is outside the research scope, clearly state the limitations
- Use bullet points and formatting for readability
- Keep responses informative but concise (under 300 words)

**Your Response:**`;
}
